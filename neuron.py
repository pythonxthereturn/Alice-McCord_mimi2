from typing import List, Tuple, Optional


class Neuron:
    """
    神经元

    神经元包含以下
    - input_val: 输入信号强度 (0~9)
    - refractory: 时效值/不应期状态 (0~30)
    - input_conns: 输入端连接列表（存储对端神经元的一维索引）
    - control_conns: 控制端连接列表
    - output_conns: 输出端连接列表
    - position: 二维坐标 (x, y)

    约束：
    - 三类连接列表各自上限9条,总数不超过27条
    - input_val 取值范围 0~9,refractory 取值范围 0~30
    """

    # 连接列表上限
    MAX_CONNS_PER_TYPE: int = 9
    MAX_TOTAL_CONNS: int = 27



    # 时效值分级
    REFRACTORY_FULL: Tuple[int, int] = (0, 3)      # 完全不应期
    REFRACTORY_HIGH: Tuple[int, int] = (4, 7)      # 高阈值期
    REFRACTORY_NORMAL: Tuple[int, int] = (8, 9)    # 正常期

    # 信号阈值
    HIGH_THRESHOLD: int = 6  # 高阈值期的信号触发阈值

    __slots__ = (
        'input_val', 
        'refractory', 
        'input_conns',
        'control_conns', 
        'output_conns', 
        'position')

    def __init__(
        self, 
        x: int, 
        y: int,
        input_val: int = 0,
        refractory: int = 9):

        # 初始化神经元。


        # input_val: 初始输入信号强度，默认0
        # refractory: 初始时效值，默认9（正常期）
      
        self.input_val: int = max(0, min(9, input_val))
        self.refractory: int = max(0, min(9, refractory))
        self.input_conns: List[int] = []
        self.control_conns: List[int] = []
        self.output_conns: List[int] = []
        self.position: Tuple[int, int] = (x, y)







    # 连接管理
    def add_input_conn(self,target_idx: int) -> bool:
        # 传入神经层
        if len(self.input_conns) >= self.MAX_CONNS_PER_TYPE:
            return False
        if target_idx in self.input_conns:
            return False
        if self.total_conns() >= self.MAX_TOTAL_CONNS:
            return False
        self.input_conns.append(target_idx)
        return True

    def add_control_conn(self,target_idx: int) -> bool:
        # 传出神经层
        if len(self.control_conns) >= self.MAX_CONNS_PER_TYPE:
            return False
        if target_idx in self.control_conns:
            return False
        if self.total_conns() >= self.MAX_TOTAL_CONNS:
            return False
        self.control_conns.append(target_idx)
        return True

    def add_output_conn(self,target_idx: int) -> bool:
        # 添加输出连接
        if len(self.output_conns) >= self.MAX_CONNS_PER_TYPE:
            return False
        if target_idx in self.output_conns:
            return False
        if self.total_conns() >= self.MAX_TOTAL_CONNS:
            return False
        self.output_conns.append(target_idx)
        return True

    def remove_input_conn(self,target_idx: int) -> bool:
        # 移除传入神经层
        if target_idx in self.input_conns:
            self.input_conns.remove(target_idx)
            return True
        return False

    def remove_control_conn(self,target_idx: int) -> bool:
        # 移除传出神经层
        if target_idx in self.control_conns:
            self.control_conns.remove(target_idx)
            return True
        return False

    def remove_output_conn(self,target_idx: int) -> bool:
        if target_idx in self.output_conns:
            self.output_conns.remove(target_idx)
            return True
        return False

    def has_conn_with(self,target_idx: int) -> bool:
        # 检查是否与指定神经元存在任何类型的连接
        return (
            target_idx in self.input_conns or
            target_idx in self.control_conns or
            target_idx in self.output_conns
            )

    def replace_conn_index(self, old_idx: int, new_idx: int):

        # 替换所有连接列表中的旧索引为新索引。
        # 用于移动后的索引同步。

        for conn_list in [self.input_conns, 
            self.control_conns, 
            self.output_conns]:
            for i in range(len(conn_list)):
                if conn_list[i] == old_idx:
                    conn_list[i] = new_idx

    def total_conns(self) -> int:
        # 获取的总数
        return len(self.input_conns) + len(self.control_conns) + len(self.output_conns)

    def is_input_full(self) -> bool:
        # 满判断输入端满载
        return len(self.input_conns) >= self.MAX_CONNS_PER_TYPE

    def is_control_full(self) -> bool:
        # 满判控制满载
        return len(self.control_conns) >= self.MAX_CONNS_PER_TYPE

    def is_output_full(self) -> bool:
        # 满判输出端满载
        return len(self.output_conns) >= self.MAX_CONNS_PER_TYPE






    # 时效不应期
    def is_in_full_refractory(self) -> bool:
        # 判断是否处于完全不应期(0~3)
        return self.REFRACTORY_FULL[0] <= self.refractory <= self.REFRACTORY_FULL[1]

    def is_in_high_threshold(self) -> bool:
        # 判断是否处于高阈值期(4~7)
        return self.REFRACTORY_HIGH[0] <= self.refractory <= self.REFRACTORY_HIGH[1]





    def is_in_normal_period(self) -> bool:
        # 判断是否处于正常期(8~9)
        return self.REFRACTORY_NORMAL[0] <= self.refractory <= self.REFRACTORY_NORMAL[1]

    def can_grow_connections(self) -> bool:
        # 判断是否可以进行连接
        return not self.is_in_full_refractory()

    def can_receive_signal(self) -> bool:
        # 判断是否可以接收信号
        return not self.is_in_full_refractory()



    def can_send_signal(self, signal_strength: int) -> bool:
        # 是否可以扩散信号
        if self.is_in_full_refractory():
            return False
        if self.is_in_high_threshold() and signal_strength <= self.HIGH_THRESHOLD:
            return False
        return True

    def trigger_signal_output(self):
        # 触发信号输出后,时效值重置为1,进入不应期
        self.refractory = 1

    def update_refractory(self, recovery_amount: int = 1):
        # 更新时效值（周期回复）
        self.refractory = min(9, self.refractory + recovery_amount)







    # 位置更新
    def update_position(self, x: int, y: int):
        # 更新神经元的二维坐标
        self.position = (x, y)

    def get_idx(self) -> int:
        # 获取当前坐标对应的一维索引
        try:
            from .grid import coord_to_idx
        except ImportError:
            from grid import coord_to_idx
        return coord_to_idx(self.position[0], self.position[1])






    # 信号强度
    def set_input_val(self,val: int):
        # 自动钳制,信号强度
        self.input_val = max(0, min(9, val))




    def __repr__(self) -> str:
        return (f"Neuron(pos={self.position}, input={self.input_val}, "
                f"ref={self.refractory}, "
                f"in={len(self.input_conns)}, "
                f"ctrl={len(self.control_conns)}, "
                f"out={len(self.output_conns)})")

    def to_dict(self) -> dict:
        # 容器保存
        return {
            'input_val': self.input_val,
            'refractory': self.refractory,
            'input_conns': self.input_conns.copy(),
            'control_conns': self.control_conns.copy(),
            'output_conns': self.output_conns.copy(),
            'position': self.position,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Neuron':
        # 加载神经元
        x, y = data['position']
        neuron = cls(x, y, data['input_val'], data['refractory'])
        neuron.input_conns = data['input_conns'].copy()
        neuron.control_conns = data['control_conns'].copy()
        neuron.output_conns = data['output_conns'].copy()
        return neuron