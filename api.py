from typing import List, Optional, Callable, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    try:
        from .diffusion import ChildArray
        from .neuron import Neuron
    except ImportError:
        from diffusion import ChildArray
        from neuron import Neuron


class TrainingAPI:
    def __init__(self):
        """初始化训练API。"""
        self.params: Dict[str, Any] = {
            'refractory_recovery_amount': 1, # 每个时间步不应期恢复量
            'refractory_reset_value': 1, # 触发放电后不应期重置初始值
            'refractory_full_max': 3, # 完全不应期最大时长
            'refractory_high_max': 7, # 高不应期阶段最大时长
            'refractory_high_threshold': 6, # 进入高不应期的阈值
            'diffusion_max_strength': 9, # 扩散信号最大强度
            'diffusion_pre_check_samples': 2, # 扩散前校验采样点数
            'connection_max_per_type': 9, # 单个神经元三通道允许的最大 连接数*3
            'connection_max_total': 27, # 单个神经元允许的最大连接数量
            'connection_max_path_steps': 4, # 单个神神经元允许的最大尝试次数
            'connection_distance_threshold': 10, # 神经元信号传递允许的最大距离
            'signal_max_strength': 9, # 神经元信号允许的最大上限
            'signal_close_boost': [3, 2, 1], # 信号增益
            'signal_distance_decay': 1, # 随距离信号衰减系数
        }

        self._termination_conditions: List[
            Callable[
                [
                    int, 
                    List[int], 
                    'ChildArray'
                ], bool]] = []
        self._reward_callbacks: List[Callable] = []





    
    # 子本管理接口
    def increase_child_batch(
            self, 
            child_array: 'ChildArray',
            active_indices: 
            List[int],
            amount: int = 1):
        # 批量增加子本数值（正反馈奖赏）
        child_array.increase_by_indices(active_indices, amount)

    def reset_child_all(self, child_array: 'ChildArray', value: int = 30):
        #重置所有子本数值
        child_array.reset_all(value)

    def reset_child_batch(
            self, 
            child_array: 'ChildArray',
            active_indices: List[int], 
            value: int = 30
            ):
        # 批量重置指定位置的子本数值
        child_array.reset_by_indices(active_indices, value)




    # 参数调节接口
    def set_param(self, key: str, value: Any):
        # 全局参数
        if key in self.params:
            self.params[key] = value

    def get_param(self, key: str) -> Optional[Any]:
        # 获取全局参数
        return self.params.get(key)


    # 终止条件扩展

    def register_termination_condition(self,condition: Callable):
        # 注册自定义终止条件
        self._termination_conditions.append(condition)





    def check_termination(
            self, round_num: int, 
            output_state: List[int],
            child_array: 'ChildArray') -> bool:
        # 检查是否满足终止条件
        for condition in self._termination_conditions:
            if condition(round_num, output_state, child_array):
                return True
        return False




    # 正反馈机制
    def register_reward_callback(self,callback: Callable):
        # 注册正反馈回调
        self._reward_callbacks.append(callback)

    def apply_reward(self,*args,**kwargs):
        # 触发所有正反馈回调
        for callback in self._reward_callbacks:
            callback(*args,**kwargs)