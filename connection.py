from typing import List, Optional, Tuple, TYPE_CHECKING



try:
    from .grid import (
        coord_to_idx, idx_to_coord, is_valid_coord, is_active_cell,
        get_neighbor_indices, get_active_neighbor_indices,
        manhattan_distance, direction_to_offset,
    )
    from .neuron import Neuron
    from .random_pool import RandomPool
except ImportError:
    from grid import (
        coord_to_idx, idx_to_coord, is_valid_coord, is_active_cell,
        get_neighbor_indices, get_active_neighbor_indices,
        manhattan_distance, direction_to_offset,
    )
    from neuron import Neuron
    from random_pool import RandomPool

if TYPE_CHECKING:
    from .diffusion import DiffusionField








# 连接
class ConnectionEngine:


    # 寻路、绑定、超距检测与断开。


    # 连接参数
    MAX_PATH_STEPS: int = 4          # 最大移动步数
    MAX_DISTANCE_THRESHOLD: int = 10  # 超距断开阈值

    def __init__(
            self, 
            diffusion_field: 'DiffusionField',
            random_pool: RandomPool
        ):
        self._field = diffusion_field
        self._random_pool = random_pool





    # 连接生长
    def try_grow_connection(
            self, 
            neuron: Neuron,
            mother_grid: List[Optional[Neuron]]) -> bool:
        
        # 尝试为神经元建立一条新连接.....
        if not neuron.can_grow_connections():
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

        if neuron.total_conns() >= Neuron.MAX_TOTAL_CONNS:
            return False

        target_idx = self._pathfind(neuron, mother_grid)
        if target_idx is None:
            return False

        target_neuron = mother_grid[target_idx]
        if target_neuron is None:
            return False

        return self._establish_connection(
            neuron, 
            target_neuron,
            conn_type, 
            mother_grid
            )

    def _pathfind(
            self, 
            neuron: Neuron,
            mother_grid: List[Optional[Neuron]]) -> Optional[int]:




        
        # 寻路
        # 从神经元出发,指针沿扩散场方向寻路
        current_x, current_y = neuron.position
        current_idx = coord_to_idx(current_x, current_y)

        for step in range(self.MAX_PATH_STEPS):
            # 第一步：检测邻域是否有神经元
            neighbor_indices = get_neighbor_indices(current_idx)
            valid_neighbors = []
            for nidx in neighbor_indices:
                if nidx == neuron.get_idx():
                    continue
                if mother_grid[nidx] is not None:
                    valid_neighbors.append(nidx)

            if valid_neighbors:
                import random
                return random.choice(valid_neighbors)

            # 第二步：检测邻域扩散场强度
            active_neighbor_indices = get_active_neighbor_indices(current_idx)
            active_neighbor_indices = [
                n for n in active_neighbor_indices
                if n != coord_to_idx(
                    neuron.position[0],
                    neuron.position[1])
                ]





            max_strength = 0
            best_idx = None
            for nidx in active_neighbor_indices:
                strength = self._field.get(nidx)
                if strength > max_strength:
                    max_strength = strength
                    best_idx = nidx
            if max_strength > 0 and best_idx is not None:
                current_x, current_y = idx_to_coord(best_idx)
                current_idx = best_idx
            else:
                # 补偿兜底：随机方向
                direction = self._random_pool.next_direction()
                if direction is None:
                    return None
                dx, dy = direction
                nx = current_x + dx
                ny = current_y + dy
                if not is_valid_coord(nx, ny):
                    return None
                current_x, current_y = nx, ny
                current_idx = coord_to_idx(nx, ny)

        return None

    def _establish_connection(
            self, source: Neuron, 
            target: Neuron,
            conn_type: str,
            mother_grid: List[Optional[Neuron]]) -> bool:
        



        """
        连接规则：
        输出端 → 对方的输入端 或 控制端
        控制端 → 对方的输出端
        输入端 → 对方的输出端
        """
        source_idx = source.get_idx()
        target_idx = target.get_idx()

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


    # 连接消亡

    def check_and_disconnect(
            self, 
            neuron_a: Neuron, 
            neuron_b: Neuron,
            mother_grid: List[Optional[Neuron]]) -> bool:

        # 检测两方经元曼哈顿距离，超过阈值则断开连接。

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
            if idx_a in neuron_b.input_conns:
                neuron_b.remove_input_conn(idx_a)
            if idx_a in neuron_b.control_conns:
                neuron_b.remove_control_conn(idx_a)
            disconnected = True
        if idx_b in neuron_a.control_conns:
            neuron_a.remove_control_conn(idx_b)
            neuron_b.remove_output_conn(idx_a)
            disconnected = True

        return disconnected

    def disconnect_all_over_distance(
            self, 
            neuron: Neuron,
            mother_grid: List[Optional[Neuron]]):
        # 检测神经元所有连接的距离断开超距连接


        idx = neuron.get_idx()
        for conn_list_name in ['input_conns','output_conns','control_conns']:
            conn_list = getattr(neuron, conn_list_name)
            for peer_idx in conn_list[:]:
                peer = mother_grid[peer_idx]
                if peer is not None:
                    distance = manhattan_distance(neuron.position,peer.position)
                    if distance > self.MAX_DISTANCE_THRESHOLD:
                        self._remove_bidirectional_connection(
                            neuron, 
                            peer, 
                            mother_grid
                            )

    def _remove_bidirectional_connection(
            self, 
            neuron_a: Neuron,
            neuron_b: Neuron,
            mother_grid: List[Optional[Neuron]]):
        # 移除神经元之间的所有双向连接


        
        idx_a = neuron_a.get_idx()
        idx_b = neuron_b.get_idx()
        neuron_a.remove_input_conn(idx_b)
        neuron_a.remove_output_conn(idx_b)
        neuron_a.remove_control_conn(idx_b)
        neuron_b.remove_input_conn(idx_a)
        neuron_b.remove_output_conn(idx_a)
        neuron_b.remove_control_conn(idx_a)