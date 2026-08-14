from typing import List, Optional, Tuple, TYPE_CHECKING
try:
    from .grid import (
        coord_to_idx, 
        idx_to_coord, 
        is_valid_coord,
        is_active_cell, 
        get_neighbor_indices, 
        get_active_neighbor_indices,
        direction_to_offset, 
        ACTIVE_CELLS,
    )
    from .neuron import Neuron
    from .random_pool import RandomPool
except ImportError:
    from grid import (
        coord_to_idx, 
        idx_to_coord, 
        is_valid_coord,
        is_active_cell, 
        get_neighbor_indices, 
        get_active_neighbor_indices,
        direction_to_offset, 
        ACTIVE_CELLS,
    )
    from neuron import Neuron
    from random_pool import RandomPool

if TYPE_CHECKING:
    from .diffusion import DiffusionField, ChildArray

# 神经元移动模块
class MovementEngine:
    # 索引同步
    def __init__(
        self, 
        diffusion_field: 'DiffusionField',
        child_array: 'ChildArray',
        random_pool: RandomPool):
        self._field = diffusion_field
        self._child = child_array
        self._random_pool = random_pool





    # 移动
    def normal_move(self,neuron: Neuron) -> Optional[Tuple[int, int]]:


        x, y = neuron.position
        current_idx = coord_to_idx(x, y)

        neighbor_indices = get_active_neighbor_indices(current_idx)
        if not neighbor_indices:
            return None
        # 检测四邻域
        max_strength = -1
        best_idx = None
        for nidx in neighbor_indices:
            strength = self._field.get(nidx)
            if strength > max_strength:
                max_strength = strength
                best_idx = nidx
        # 向强度最大的方向移动
        if max_strength > neuron.input_val and best_idx is not None:
            return idx_to_coord(best_idx)

        return None





    # 补偿移动
    def should_compensate(self, neuron: Neuron, active_idx: int) -> bool:
        """
        判断是否触发补偿移动。

        触发条件（同时满足）：
        1. 子本数值 < 6
        2. input_conns、control_conns、output_conns 全部为空
        """
        child_val = self._child.get(active_idx)
        if child_val >= 6:
            return False

        if (len(neuron.input_conns) > 0 or
                len(neuron.control_conns) > 0 or
                len(neuron.output_conns) > 0):
            return False

        return True

    def compensate_move(self, neuron: Neuron) -> Optional[Tuple[int, int]]:
        """
        补偿移动：从随机池取方向，直接移动1步。
        """
        direction = self._random_pool.next_direction()
        if direction is None:
            return None

        dx, dy = direction
        x, y = neuron.position
        nx, ny = x + dx, y + dy

        if not is_active_cell(nx, ny):
            return None

        return (nx, ny)

    # ============================================================
    # 移动执行与冲突处理
    # ============================================================

    def execute_move(self, neuron: Neuron, target_coord: Tuple[int, int],
                     mother_grid: List[Optional[Neuron]]) -> bool:
        """
        执行移动操作。

        移动逻辑：
        1. 检查目标格子是否被占用（先到先得）
        2. 更新母本网格
        3. 同步更新所有关联连接的索引
        4. 更新神经元自身 position
        """
        tx, ty = target_coord
        target_idx = coord_to_idx(tx, ty)

        # 冲突检查：目标格子已被占用
        if mother_grid[target_idx] is not None:
            return False

        old_idx = coord_to_idx(neuron.position[0],
                               neuron.position[1])

        # 执行移动
        mother_grid[old_idx] = None
        mother_grid[target_idx] = neuron
        neuron.update_position(tx, ty)

        # 同步连接索引
        self._sync_connections_after_move(neuron, mother_grid,
                                          old_idx, target_idx)
        return True

    def _sync_connections_after_move(self, neuron: Neuron,
                                      mother_grid: List[Optional[Neuron]],
                                      old_idx: int, new_idx: int):
        """
        移动后同步所有关联神经元的连接索引。
        """
        for peer_idx in neuron.output_conns:
            peer = mother_grid[peer_idx]
            if peer is not None:
                peer.replace_conn_index(old_idx, new_idx)

        for peer_idx in neuron.input_conns:
            peer = mother_grid[peer_idx]
            if peer is not None:
                peer.replace_conn_index(old_idx, new_idx)

        for peer_idx in neuron.control_conns:
            peer = mother_grid[peer_idx]
            if peer is not None:
                peer.replace_conn_index(old_idx, new_idx)

    # ============================================================
    # 单神经元移动处理
    # ============================================================

    def process_neuron_move(self, neuron: Neuron, active_idx: int,
                            mother_grid: List[Optional[Neuron]]) -> bool:
        """
        处理单个神经元的完整移动流程。

        流程：
        1. 先校验补偿移动条件
        2. 否则执行正常移动判定
        3. 移动成功后同步所有连接索引
        """
        target = None

        if self.should_compensate(neuron, active_idx):
            target = self.compensate_move(neuron)
        else:
            target = self.normal_move(neuron)

        if target is not None:
            return self.execute_move(neuron, target, mother_grid)

        return False