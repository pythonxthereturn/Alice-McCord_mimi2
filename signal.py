from collections import deque
from typing import List, Optional, Tuple, Set, TYPE_CHECKING


# 广度优先遍历(BFS)信号传递模块







try:
    from .grid import (
        coord_to_idx, 
        idx_to_coord, 
        manhattan_distance,
        get_input_layer_indices, 
        get_output_layer_indices,
        TOTAL_CELLS,
    )
    from .neuron import Neuron
except ImportError:
    from grid import (
        coord_to_idx, 
        idx_to_coord, 
        manhattan_distance,
        get_input_layer_indices, 
        get_output_layer_indices,
        TOTAL_CELLS,
    )
    from neuron import Neuron

if TYPE_CHECKING:
    from .connection import ConnectionEngine


class SignalEngine:
    # 安全上限：单次传播最大信号处理步数
    MAX_SIGNAL_STEPS = 2_000_000

    def __init__(
            self, 
            connection_engine: 'ConnectionEngine'
            ):
        self._conn_engine = connection_engine

    # ============================================================
    # 信号强度计算
    # ============================================================

    @staticmethod
    def calc_signal_strength(
        source_strength: int,
        distance: int) -> int:
        return max(0,min(9, source_strength))













    # BFS 信号传递
    def propagate_signals(
        self, 
        mother_grid: List[Optional[Neuron]],
        output_layer_state: List[int]) -> int:






        signal_count = 0
        output_queue: deque = deque()
        control_queue: deque = deque()

        # 初始化传出层状态
        for i in range(len(output_layer_state)):
            output_layer_state[i] = 0

        # 存储每个神经元当前已接收的最大信号强度
        received_strengths: List[int] = [0] * TOTAL_CELLS

        # 从传入层启动信号
        input_indices = get_input_layer_indices()
        for idx in input_indices:
            neuron = mother_grid[idx]
            if neuron is not None and neuron.input_val > 0:
                source_strength = neuron.input_val
                for target_idx in neuron.output_conns:
                    target = mother_grid[target_idx]
                    if target is None:
                        continue
                    dist = manhattan_distance(neuron.position,target.position)
                    if dist > self._conn_engine.MAX_DISTANCE_THRESHOLD:
                        self._conn_engine.check_and_disconnect(neuron,target,mother_grid)
                        continue
                    strength = self.calc_signal_strength(source_strength,dist)
                    if strength > 0:
                        output_queue.append((idx,target_idx,strength,False))

        # BFS主循环：先处理输出信号，再处理控制信号
        while (output_queue or control_queue) and signal_count < self.MAX_SIGNAL_STEPS:
            while output_queue:
                if signal_count >= self.MAX_SIGNAL_STEPS:
                    break
                from_idx, to_idx, strength, is_control = output_queue.popleft()
                signal_count += self._process_signal(
                    from_idx, to_idx, 
                    strength, 
                    is_control,
                    mother_grid, 
                    received_strengths,
                    output_queue, 
                    control_queue,
                    output_layer_state)

            while control_queue:
                if signal_count >= self.MAX_SIGNAL_STEPS:
                    break
                from_idx, to_idx, strength, is_control = control_queue.popleft()
                signal_count += self._process_signal(
                    from_idx, 
                    to_idx, 
                    strength, 
                    is_control,
                    mother_grid, 
                    received_strengths,
                    output_queue, 
                    control_queue,
                    output_layer_state)

        return signal_count

    def _process_signal(
        self, 
        from_idx: int, 
        to_idx: int,
        strength: int, 
        is_control: bool,
        mother_grid: List[Optional[Neuron]],
        received_strengths: List[int],
        output_queue: deque, 
        control_queue: deque,
        output_layer_state: List[int]) -> int:
        # 信号传递
        source = mother_grid[from_idx]
        target = mother_grid[to_idx]

        if source is None or target is None:
            return 0

        if not target.can_receive_signal():
            return 0

        if strength <= received_strengths[to_idx]:
            return 0
        received_strengths[to_idx] = strength

        target.set_input_val(strength)

        # 检查是否到达传出层
        output_indices = get_output_layer_indices()
        if to_idx in output_indices:
            output_pos = output_indices.index(to_idx)
            output_layer_state[output_pos] = strength
            return 1

        # 控制端信号处理
        if is_control:
            return 1

        # 输出端信号处理
        if not target.can_send_signal(strength):
            return 1

        target.trigger_signal_output()

        # 检查控制端抑制
        is_inhibited = False
        for ctrl_idx in target.control_conns:
            if received_strengths[ctrl_idx] > 0:
                is_inhibited = True
                break

        if is_inhibited:
            return 1

        output_strength = target.input_val
        if output_strength <= 0:
            return 1

        for next_idx in target.output_conns:
            next_target = mother_grid[next_idx]
            if next_target is None:
                continue
            dist = manhattan_distance(target.position, next_target.position)

            if dist > self._conn_engine.MAX_DISTANCE_THRESHOLD:
                self._conn_engine.check_and_disconnect(target, next_target, mother_grid)
                continue





            next_strength = self.calc_signal_strength(output_strength, dist)
            if next_strength <= 0:
                continue

            output_queue.append((to_idx, next_idx, next_strength, False))

        for next_idx in target.control_conns:
            next_target = mother_grid[next_idx]
            if next_target is None:
                continue
            dist = manhattan_distance(target.position, next_target.position)

            if dist > self._conn_engine.MAX_DISTANCE_THRESHOLD:
                self._conn_engine.check_and_disconnect(
                    target, next_target, mother_grid)
                continue

            next_strength = self.calc_signal_strength(output_strength, dist)
            if next_strength <= 0:
                continue

            control_queue.append((to_idx, next_idx, next_strength, True))

        return 1