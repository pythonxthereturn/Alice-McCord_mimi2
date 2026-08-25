import random
from collections import deque
from typing import List, Optional, Tuple

from core import (
    GRID_X,
    GRID_Y,
    TOTAL_CELLS,
    ACTIVE_X_MIN,
    ACTIVE_X_MAX,
    OUTPUT_LAYER_X,
    coord_to_idx,
    idx_to_coord,
    is_valid_coord,
    get_neighbor_indices,
    get_active_neighbor_indices,
    get_input_layer_indices,
    manhattan_distance,
    Neuron,
    RandomPool,
    DiffusionField,
)


# =====================================================================
# 渲染引擎（扩散渲染 / 退火 / 复渲染）
# =====================================================================

class DiffusionEngine:
    """基于 render_radius 的扩散渲染、退火与复渲染。"""

    def __init__(self, diffusion_field: DiffusionField):
        self._field = diffusion_field

    def _get_diffusion_range(self, neuron: Neuron) -> List[Tuple[int, int]]:
        radius = neuron.render_radius
        if radius <= 0:
            return []
        input_val = neuron.input_val
        if input_val <= 0:
            return []
        sx, sy = neuron.position
        results = []
        for dx in range(-radius, radius + 1):
            tx = sx + dx
            if not (ACTIVE_X_MIN <= tx <= ACTIVE_X_MAX):
                continue
            remaining = radius - abs(dx)
            for dy in range(-remaining, remaining + 1):
                ty = sy + dy
                if 0 <= ty < GRID_Y:
                    distance = abs(dx) + abs(dy)
                    strength = input_val - distance
                    if strength > 0:
                        idx = coord_to_idx(tx, ty)
                        results.append((idx, strength))
        return results

    def render_diffusion(self, neuron: Neuron) -> bool:
        if neuron.render_radius <= 0 or neuron.input_val <= 0:
            return False
        for idx, strength in self._get_diffusion_range(neuron):
            self._field.set_max(idx, strength)
        return True

    def anneal(self, neuron: Neuron):
        if neuron.render_radius <= 0 or neuron.input_val <= 0:
            return
        for idx, strength in self._get_diffusion_range(neuron):
            current = self._field.get(idx)
            self._field.set(idx, max(0, current - strength))

    def re_render(self, neuron: Neuron):
        if neuron.render_radius <= 0 or neuron.input_val <= 0:
            return
        for idx, strength in self._get_diffusion_range(neuron):
            self._field.set_max(idx, strength)


# =====================================================================
# 移动引擎
# =====================================================================

class MovementEngine:
    """按周围扩散场强度移动神经元；邻域有神经元时优先直接连接。"""

    def __init__(
            self,
            diffusion_field: DiffusionField,
            random_pool: RandomPool,
            connection_engine: 'ConnectionEngine'):
        self._field = diffusion_field
        self._random_pool = random_pool
        self._conn_engine = connection_engine

    def process_neuron_move(self, neuron: Neuron, neuron_grid: List[Optional[Neuron]]) -> bool:
        x, y = neuron.position
        current_idx = coord_to_idx(x, y)
        neighbors = get_active_neighbor_indices(current_idx)
        if not neighbors:
            return False

        # 邻域有神经元 → 直接尝试连接，本回合不移动
        for nidx in neighbors:
            if neuron_grid[nidx] is not None:
                self._conn_engine.try_grow_connection(neuron, neuron_grid)
                return False

        # 基于扩散场强度移动
        max_strength = -1
        for nidx in neighbors:
            s = self._field.get(nidx)
            if s > max_strength:
                max_strength = s
        if max_strength <= 0:
            return False

        candidates = [nidx for nidx in neighbors if self._field.get(nidx) == max_strength]
        if len(candidates) == 1:
            target_idx = candidates[0]
        else:
            target_idx = self._tie_break(x, y, candidates)
            if target_idx is None:
                return False

        return self._execute_move(neuron, target_idx, neuron_grid)

    def _tie_break(self, x: int, y: int, candidates: List[int]) -> Optional[int]:
        direction = self._random_pool.next_direction()
        if direction is not None:
            dx, dy = direction
            cand_idx = coord_to_idx(x + dx, y + dy)
            if cand_idx in candidates:
                return cand_idx
        v = self._random_pool.next()
        if v is None:
            return None
        return candidates[v % len(candidates)]

    def _execute_move(self, neuron: Neuron, target_idx: int,
                      neuron_grid: List[Optional[Neuron]]) -> bool:
        if neuron_grid[target_idx] is not None:
            return False
        old_idx = neuron.get_idx()
        neuron_grid[old_idx] = None
        neuron_grid[target_idx] = neuron
        tx, ty = idx_to_coord(target_idx)
        neuron.update_position(tx, ty)
        self._sync_connections_after_move(neuron, neuron_grid, old_idx, target_idx)
        return True

    def _sync_connections_after_move(self, neuron: Neuron,
                                     neuron_grid: List[Optional[Neuron]],
                                     old_idx: int, new_idx: int):
        for peer_idx in neuron.output_conns:
            peer = neuron_grid[peer_idx]
            if peer is not None:
                peer.replace_conn_index(old_idx, new_idx)
        for peer_idx in neuron.input_conns:
            peer = neuron_grid[peer_idx]
            if peer is not None:
                peer.replace_conn_index(old_idx, new_idx)
        for peer_idx in neuron.control_conns:
            peer = neuron_grid[peer_idx]
            if peer is not None:
                peer.replace_conn_index(old_idx, new_idx)


# =====================================================================
# 连接引擎
# =====================================================================

class ConnectionEngine:
    MAX_PATH_STEPS: int = 4
    MAX_DISTANCE_THRESHOLD: int = 10

    def __init__(self, diffusion_field: DiffusionField, random_pool: RandomPool):
        self._field = diffusion_field
        self._random_pool = random_pool

    def try_grow_connection(self, neuron: Neuron,
                            neuron_grid: List[Optional[Neuron]]) -> bool:
        if neuron.total_conns() >= Neuron.MAX_TOTAL_CONNS:
            return False

        conn_type = self._random_pool.next_conn_type()
        if conn_type is None:
            return False

        if conn_type == 'input' and neuron.is_input_full():
            return False
        if conn_type == 'control' and neuron.is_control_full():
            return False
        if conn_type == 'output' and neuron.is_output_full():
            return False

        target_idx = self._find_target(neuron, neuron_grid)
        if target_idx is None:
            return False
        target = neuron_grid[target_idx]
        if target is None:
            return False
        return self._establish_connection(neuron, target, conn_type, neuron_grid)

    def _find_target(self, neuron: Neuron,
                     neuron_grid: List[Optional[Neuron]]) -> Optional[int]:
        x, y = neuron.position
        current_idx = coord_to_idx(x, y)

        # 先检查四邻域是否有神经元
        neighbor_indices = get_neighbor_indices(current_idx)
        valid = [n for n in neighbor_indices
                 if neuron_grid[n] is not None and n != neuron.get_idx()]
        if valid:
            return random.choice(valid)

        # 寻路（最多 4 步）
        cx, cy = x, y
        for _ in range(self.MAX_PATH_STEPS):
            neighbor_indices = get_neighbor_indices(current_idx)
            valid = [n for n in neighbor_indices
                     if neuron_grid[n] is not None and n != neuron.get_idx()]
            if valid:
                return random.choice(valid)

            active = get_active_neighbor_indices(current_idx)
            active = [n for n in active if n != neuron.get_idx()]
            if not active:
                break

            max_strength = -1
            for n in active:
                s = self._field.get(n)
                if s > max_strength:
                    max_strength = s

            if max_strength <= 0:
                direction = self._random_pool.next_direction()
                if direction is None:
                    return None
                dx, dy = direction
                nx, ny = cx + dx, cy + dy
                if not is_valid_coord(nx, ny):
                    return None
                cx, cy = nx, ny
                current_idx = coord_to_idx(nx, ny)
            else:
                candidates = [n for n in active if self._field.get(n) == max_strength]
                if len(candidates) == 1:
                    best = candidates[0]
                else:
                    best = None
                    direction = self._random_pool.next_direction()
                    if direction is not None:
                        dx, dy = direction
                        cand = coord_to_idx(cx + dx, cy + dy)
                        if cand in candidates:
                            best = cand
                    if best is None:
                        v = self._random_pool.next()
                        if v is None:
                            return None
                        best = candidates[v % len(candidates)]
                cx, cy = idx_to_coord(best)
                current_idx = best

        return None

    def _establish_connection(self, source: Neuron, target: Neuron,
                              conn_type: str,
                              neuron_grid: List[Optional[Neuron]]) -> bool:
        source_idx = source.get_idx()
        target_idx = target.get_idx()

        if source_idx == target_idx:
            return False
        if source.has_conn_with(target_idx) or target.has_conn_with(source_idx):
            return False

        if conn_type == 'output':
            if not target.is_input_full():
                if source.add_output_conn(target_idx) and target.add_input_conn(source_idx):
                    return True
            if not target.is_control_full():
                if source.add_output_conn(target_idx) and target.add_control_conn(source_idx):
                    return True
        elif conn_type == 'input':
            if not target.is_output_full():
                if source.add_input_conn(target_idx) and target.add_output_conn(source_idx):
                    return True
        elif conn_type == 'control':
            if not target.is_output_full():
                if source.add_control_conn(target_idx) and target.add_output_conn(source_idx):
                    return True
        return False

    def check_and_disconnect(self, neuron_a: Neuron, neuron_b: Neuron,
                             neuron_grid: List[Optional[Neuron]]) -> bool:
        distance = manhattan_distance(neuron_a.position, neuron_b.position)
        if distance <= self.MAX_DISTANCE_THRESHOLD:
            return False

        idx_a = neuron_a.get_idx()
        idx_b = neuron_b.get_idx()
        disconnected = False

        if idx_b in neuron_a.input_conns:
            neuron_a.remove_input_conn(idx_b)
            neuron_b.remove_output_conn(idx_a)
            disconnected = True
        if idx_b in neuron_a.output_conns:
            neuron_a.remove_output_conn(idx_b)
            neuron_b.remove_input_conn(idx_a)
            neuron_b.remove_control_conn(idx_a)
            disconnected = True
        if idx_b in neuron_a.control_conns:
            neuron_a.remove_control_conn(idx_b)
            neuron_b.remove_output_conn(idx_a)
            disconnected = True

        return disconnected

    def disconnect_all_over_distance(self, neuron_grid: List[Optional[Neuron]]):
        for neuron in neuron_grid:
            if neuron is None:
                continue
            self._disconnect_neuron_if_over_distance(neuron, neuron_grid)

    def _disconnect_neuron_if_over_distance(self, neuron: Neuron,
                                            neuron_grid: List[Optional[Neuron]]):
        for conn_list_name in ['input_conns', 'output_conns', 'control_conns']:
            conn_list = getattr(neuron, conn_list_name)
            for peer_idx in conn_list[:]:
                peer = neuron_grid[peer_idx]
                if peer is None:
                    continue
                if manhattan_distance(neuron.position, peer.position) > self.MAX_DISTANCE_THRESHOLD:
                    self._remove_bidirectional(neuron, peer, neuron_grid)

    def _remove_bidirectional(self, neuron_a: Neuron, neuron_b: Neuron,
                              neuron_grid: List[Optional[Neuron]]):
        idx_a = neuron_a.get_idx()
        idx_b = neuron_b.get_idx()
        neuron_a.remove_input_conn(idx_b)
        neuron_a.remove_output_conn(idx_b)
        neuron_a.remove_control_conn(idx_b)
        neuron_b.remove_input_conn(idx_a)
        neuron_b.remove_output_conn(idx_a)
        neuron_b.remove_control_conn(idx_a)


# =====================================================================
# 信号引擎（仅 output_conns 发射）
# =====================================================================

class SignalEngine:
    def __init__(self, connection_engine: ConnectionEngine):
        self._conn_engine = connection_engine

    def propagate_signals(self, neuron_grid: List[Optional[Neuron]],
                          output_state: List[int]) -> int:
        for i in range(len(output_state)):
            output_state[i] = 0

        queue: deque = deque()
        received: List[int] = [0] * TOTAL_CELLS
        signal_count = 0

        # 从输入层启动
        for idx in get_input_layer_indices():
            src = neuron_grid[idx]
            if src is None or src.input_val <= 0:
                continue
            for target_idx in src.output_conns:
                queue.append((idx, target_idx, src.input_val))

        # BFS 主循环
        while queue:
            from_idx, to_idx, strength = queue.popleft()
            signal_count += 1

            source = neuron_grid[from_idx]
            target = neuron_grid[to_idx]
            if source is None or target is None:
                continue

            if target.is_in_full_refractory():
                continue

            # 判断连接类型并接收
            if from_idx in target.input_conns:
                if strength <= received[to_idx]:
                    continue
                received[to_idx] = strength
                target.input_val = max(target.input_val, strength)
            elif from_idx in target.control_conns:
                target.input_val = 0  # 抑制
            else:
                continue

            # 到达输出层：记录，不续传
            tx, ty = idx_to_coord(to_idx)
            if tx == OUTPUT_LAYER_X:
                output_state[ty] = target.input_val
                continue

            if target.input_val <= 0:
                continue
            if not target.can_send_signal(target.input_val):
                continue

            # 发射
            target.trigger_signal_output()
            out_strength = target.input_val
            target.input_val = 0

            for next_idx in target.output_conns:
                nt = neuron_grid[next_idx]
                if nt is None:
                    continue
                if manhattan_distance(target.position, nt.position) > self._conn_engine.MAX_DISTANCE_THRESHOLD:
                    self._conn_engine.check_and_disconnect(target, nt, neuron_grid)
                    continue
                queue.append((to_idx, next_idx, out_strength))

        return signal_count