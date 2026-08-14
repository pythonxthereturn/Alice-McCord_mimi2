import random as _random
from typing import List, Optional, TYPE_CHECKING
try:
    from .grid import (
        TOTAL_CELLS, ACTIVE_CELLS, GRID_X, GRID_Y,
        ACTIVE_X_MIN, ACTIVE_X_MAX,
        coord_to_idx, idx_to_coord, is_active_cell,
        manhattan_distance, get_active_neighbor_indices,
        get_all_active_indices,
    )
    from .neuron import Neuron
    from .random_pool import RandomPool
except ImportError:
    from grid import (
        TOTAL_CELLS, ACTIVE_CELLS, GRID_X, GRID_Y,
        ACTIVE_X_MIN, ACTIVE_X_MAX,
        coord_to_idx, idx_to_coord, is_active_cell,
        manhattan_distance, get_active_neighbor_indices,
        get_all_active_indices,
    )
    from neuron import Neuron
    from random_pool import RandomPool

if TYPE_CHECKING:
    pass


# 扩散渲染与退火模块 (diffusion) — 2D版本
# 负责扩散场的更新、神经元扩散信号的渲染、预检查优化、
# 退火回落与复渲染操作。


# 扩散场管理
class DiffusionField:
    _MAX_STRENGTH: int = 9 # 允许的最大强度

    def __init__(self):
        # 初始化扩散场全部为0
        self._field: List[int] = [0] * TOTAL_CELLS
    def get(self, idx: int) -> int:
        # 获取指定的扩散强度
        if 0 <= idx < TOTAL_CELLS:
            return self._field[idx]
        return 0




    def set(self, idx: int, value: int):
        # 设置指定格子的扩散强度,自动钳制到0~9
        if 0 <= idx < TOTAL_CELLS:
            self._field[idx] = max(0, min(self._MAX_STRENGTH,value))
    def set_max(self, idx: int,value: int):
        # 设置强度，仅当新值大于当前值时才更新（取最大值叠加规则)
        if 0 <= idx < TOTAL_CELLS:
            clamped = max(0, min(self._MAX_STRENGTH,value))
            if clamped > self._field[idx]:
                self._field[idx] = clamped

    def clear(self):
        # 清空全部置0
        for i in range(TOTAL_CELLS):
            self._field[i] = 0

    def get_field(self) -> List[int]:
        # 获取整个扩散场数组的副本
        return self._field.copy()

    def load_field(self, data: List[int]):
        # 从文字加载扩散场
        if len(data) == TOTAL_CELLS:
            self._field = data.copy()



# 子本

class ChildArray:
    _DEFAULT_VALUE: int = 30


    def __init__(self):
        # 初始化子本数组
        self._data: List[int] = [self._DEFAULT_VALUE] * ACTIVE_CELLS

    def get(self, active_idx: int) -> int:
        # 获取指定可活动位置的值
        if 0 <= active_idx < ACTIVE_CELLS:
            return self._data[active_idx]
        return 0
    def get_by_global_idx(self, global_idx: int) -> int:
        # 通过母本索引获取子本值
        try:
            from .grid import global_idx_to_active_idx
        except ImportError:
            from grid import global_idx_to_active_idx
        active_idx = global_idx_to_active_idx(global_idx)
        if active_idx is not None:
            return self._data[active_idx]
        return 0







    
    def decrement(self, active_idx: int) -> bool:
        # 扣减子本数值 - 1
        # 是否成功扣减（已为0则返回False）
        if 0 <= active_idx < ACTIVE_CELLS:
            if self._data[active_idx] > 0:
                self._data[active_idx] -= 1
                return True
        return False

    def set(self,active_idx: int,value: int):
        # 设置子本数值
        if 0 <= active_idx < ACTIVE_CELLS:
            self._data[active_idx] = max(0,value)



    def reset_all(self, value: int = _DEFAULT_VALUE):
        # 重置所有子本数值
        for i in range(ACTIVE_CELLS):
            self._data[i] = value
    def reset_by_indices(self, active_indices: List[int], value: int = _DEFAULT_VALUE):
        # 批量重置指定位置的子本数值
        for idx in active_indices:
            if 0 <= idx < ACTIVE_CELLS:
                self._data[idx] = value
    def increase_by_indices(self, active_indices: List[int], amount: int = 1):
        # 批量增加指定位置的子本数值（正反馈奖赏
        for idx in active_indices:
            if 0 <= idx < ACTIVE_CELLS:
                self._data[idx] = min(9, self._data[idx] + amount)




    def get_data(self) -> List[int]:
        # 获取子本数组副本
        return self._data.copy()

    def load_data(self, data: List[int]):
        # 从数据加载子本数组
        if len(data) == ACTIVE_CELLS:
            self._data = data.copy()





# 扩散渲染核心逻辑
class DiffusionEngine:
    # 负责扩散渲染、预检查优化、退火、复渲染等核心逻辑。


    def __init__(
            self, 
            diffusion_field: DiffusionField,
            child_array: ChildArray,
            random_pool: RandomPool
            ):
        self._field = diffusion_field
        self._child = child_array
        self._random_pool = random_pool




    # 扩散强度计算
    @staticmethod
    def _calc_diffusion_strength(
        source_neuron: Neuron,
        target_x: int, 
        target_y: int) -> int:
        
        # 计算扩散强度。
        sx, sy = source_neuron.position
        distance = abs(sx - target_x) + abs(sy - target_y)
        strength = source_neuron.input_val - distance
        return max(0, min(9, strength))

    def _get_diffusion_range(self, source_neuron: Neuron) -> List[tuple]:
        #获取神经元在可活动区域内的扩散范围。
        #扩散范围 = 曼哈顿距离 ≤ input_val 的所有可活动格子。




        input_val = source_neuron.input_val
        if input_val <= 0:
            return []
        sx, sy = source_neuron.position
        results = []
        # 遍历可能被扩散到的范围（曼哈顿距离 ≤ input_val）
        for dx in range(-input_val,input_val + 1):
            tx = sx + dx
            if not (ACTIVE_X_MIN <= tx <= ACTIVE_X_MAX):
                continue
            remaining = input_val - abs(dx)
            for dy in range(-remaining, remaining + 1):
                ty = sy + dy
                if 0 <= ty < GRID_Y:
                    distance = abs(dx) + abs(dy)
                    strength = input_val - distance
                    if strength > 0:
                        idx = coord_to_idx(tx, ty)
                        results.append((idx, strength))

        return results



    # 预检查优化
    def _pre_check(self, neuron: Neuron) -> bool:
        
        #预检查：在神经元理论扩散范围内随机抽取位点，
        #与当前实际扩散强度比对，判断是否需要重新渲染
        #若?个位点中≥?个与理论值不一致，返回True（需要渲染）。
        
        diffusion_range = self._get_diffusion_range(neuron)
        if not diffusion_range:
            return False
        sample_size = min(6,len(diffusion_range))# 这里示范为6个
        samples = _random.sample(diffusion_range, sample_size)

        mismatch_count = 0
        for idx, expected_strength in samples:
            actual_strength = self._field.get(idx)
            if actual_strength < expected_strength:
                mismatch_count += 1

        return mismatch_count >= 3











    # 全量扩散渲染
    def render_diffusion(self, neuron: Neuron, active_idx: int) -> bool:
      
        # 重叠时采用强度叠加取最大值
    
        if self._child.get(active_idx) <= 0:
            return False
        if neuron.input_val <= 0:
            return False
        diffusion_range = self._get_diffusion_range(neuron)
        for idx, strength in diffusion_range:
            self._field.set_max(idx,strength)
        self._child.decrement(active_idx)
        return True







    def render_diffusion_with_pre_check(
            self, neuron: Neuron,
            active_idx: int) -> bool:
      
        # 预检查的扩散渲染。
        # 先执行预检查，当检查通过时才执行完整渲染。
  


        if self._child.get(active_idx) <= 0:
            return False
        if neuron.input_val <= 0:
            return False
        if not self._pre_check(neuron):
            return False

        
        return self.render_diffusion(neuron, active_idx)


 
    # 退火回落
    def anneal(self, neuron: Neuron):
        # 退火操作：以自身 input_val 为基数，
        # 扣减扩散场中自身的信号
        # 位置保护：神经元自身所在格子的强度不被退火扣减



        input_val = neuron.input_val
        if input_val <= 0:
            return

        sx, sy = neuron.position
        self_idx = coord_to_idx(sx, sy)
        diffusion_range = self._get_diffusion_range(neuron)


        for idx, strength in diffusion_range:
            if idx == self_idx:
                continue
            current = self._field.get(idx)
            new_val = max(0, current - strength)
            self._field.set(idx, new_val)





    # 复渲染
    def re_render(self, neuron: Neuron):
        # 复渲染：以自身 input_val 为基数，重新执行扩散渲染
        # 恢复自身的扩散信号分量。不扣减子本次数
     
        if neuron.input_val <= 0:
            return
        diffusion_range = self._get_diffusion_range(neuron)

        for idx, strength in diffusion_range:
            self._field.set_max(idx,strength)

  
    # 批量操作
    def render_all(
            self, 
            mother_grid: List[Optional[Neuron]],
            active_indices: List[int]) -> int:


        
        # 批量执行预检查扩散渲染
        count = 0
        for active_idx, global_idx in enumerate(active_indices):
            neuron = mother_grid[global_idx]
            if neuron is not None:
                if self.render_diffusion_with_pre_check(neuron,active_idx):
                    count += 1
        return count