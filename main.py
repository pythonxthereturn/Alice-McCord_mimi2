import sys
import random
from typing import List, Optional
try:
    from .grid import (
        TOTAL_CELLS, 
        ACTIVE_CELLS,
        GRID_X, 
        GRID_Y,
        INPUT_LAYER_SIZE,
        OUTPUT_LAYER_SIZE,
        ACTIVE_X_MIN, 
        ACTIVE_X_MAX,
        coord_to_idx, 
        idx_to_coord,
        get_all_active_indices,
        get_input_layer_indices, 
        get_output_layer_indices,
        global_idx_to_active_idx,
    )
    from .neuron import Neuron
    from .random_pool import RandomPool
    from .diffusion import DiffusionField, ChildArray, DiffusionEngine
    from .movement import MovementEngine
    from .connection import ConnectionEngine
    from .signal import SignalEngine
    from .api import TrainingAPI
    from .text_io import encode_text, decode_output
except ImportError:
    from grid import (
        TOTAL_CELLS, 
        ACTIVE_CELLS,
        GRID_X, 
        GRID_Y,
        INPUT_LAYER_SIZE, 
        OUTPUT_LAYER_SIZE,
        ACTIVE_X_MIN, 
        ACTIVE_X_MAX,
        coord_to_idx, 
        idx_to_coord,
        get_all_active_indices,
        get_input_layer_indices,
        get_output_layer_indices,
        global_idx_to_active_idx,
    )
    from neuron import Neuron
    from random_pool import RandomPool
    from diffusion import DiffusionField, ChildArray, DiffusionEngine
    from movement import MovementEngine
    from connection import ConnectionEngine
    from signal import SignalEngine
    from api import TrainingAPI
    from text_io import encode_text, decode_output














# 主循环调度
class BrainGrid2D:
    # 输入层: 0 - 1079
    # 活动区: 1080 - 1103759
    # 输出层: 1103760 - 1105920
   
    def __init__(self,neuron_density : float = 1.0):
        # 初始化系统
        self.current_round: int = 0
        self.neuron_density: float = max(0.001, min(1.0, neuron_density))
        self.mother_grid: List[Optional[Neuron]] = [None] * TOTAL_CELLS # 母本网格：长度为221184的数组
        self.child_array: ChildArray = ChildArray() # 子本数组：长度为219136
        self.diffusion_field: DiffusionField = DiffusionField() # 扩散场：长度为221184
        self.random_pool: RandomPool = RandomPool() # 全局随机池

        # 各引擎
        self.diffusion_engine: DiffusionEngine = DiffusionEngine(
            self.diffusion_field, 
            self.child_array, 
            self.random_pool
            )
        self.movement_engine: MovementEngine = MovementEngine(
            self.diffusion_field, 
            self.child_array, 
            self.random_pool
            )
        self.connection_engine: ConnectionEngine = ConnectionEngine(
            self.diffusion_field, 
            self.random_pool
            )
        self.signal_engine: SignalEngine = SignalEngine(
            self.connection_engine
            )




        # 训练API
        self.api: TrainingAPI = TrainingAPI()

        # 传出层状态记录 (1024个神经元)
        self.output_state: List[int] = [0] * OUTPUT_LAYER_SIZE

        # 传入层输入数据缓冲区
        self.input_buffer: List[int] = []

        # 可活动区域索引列表（全部219136个格子，含空的）
        self.active_indices: List[int] = get_all_active_indices()






    # 初始化
    def initialize_boundary_neurons(self):
        # 传入层
        input_indices = get_input_layer_indices()
        for idx in input_indices:
            _, y = idx_to_coord(idx)
            self.mother_grid[idx] = Neuron(
                0, 
                y,
                input_val=0, 
                refractory=9
                )

        # 传出层
        output_indices = get_output_layer_indices()
        for idx in output_indices:
            _, y = idx_to_coord(idx)
            self.mother_grid[idx] = Neuron(
                GRID_X - 1, 
                y,
                input_val=0, 
                refractory=9
                )

    def fill_active_neurons(self):
        # 填充区域
        import random as _random
        for x in range(ACTIVE_X_MIN, ACTIVE_X_MAX + 1):
            for y in range(GRID_Y):
                if _random.random() < self.neuron_density:
                    idx = coord_to_idx(x, y)
                    self.mother_grid[idx] = Neuron(
                        x, y,
                        input_val=0,
                        refractory=9,
                    )





    def setup_initial_connections(self):
        # 建立初始连接通路
        # 每列神经元连接到下一列同Y±5范围内的随机神经元
        # 这样信号大致沿Y方向传播，但路径有随机偏移
        import random as _random
        SPREAD = 1080  # Y方向随机偏移范围
        for y in range(GRID_Y):
            in_idx = coord_to_idx(0, y)
            in_neuron = self.mother_grid[in_idx]
            if in_neuron is None:
                continue
            target_y = max(
                0, 
                min(
                    GRID_Y - 1,
                    y + _random.randint(
                        -SPREAD, 
                        SPREAD
                        )
                    )
                )
            x1_idx = coord_to_idx(1, target_y)
            x1_neuron = self.mother_grid[x1_idx]
            if x1_neuron is not None:
                in_neuron.add_output_conn(x1_idx)
                x1_neuron.add_input_conn(in_idx)

        # 信号变换
        for y in range(GRID_Y):
            x214_idx = coord_to_idx(ACTIVE_X_MAX, y)
            x214_neuron = self.mother_grid[x214_idx]
            out_idx = coord_to_idx(GRID_X - 1, y)
            out_neuron = self.mother_grid[out_idx]
            if x214_neuron is not None and out_neuron is not None:
                x214_neuron.add_output_conn(out_idx)
                out_neuron.add_input_conn(x214_idx)

        # 活动层随机连接
        for x in range(ACTIVE_X_MIN,ACTIVE_X_MAX):
            for y in range(GRID_Y):
                curr_idx = coord_to_idx(x, y)
                curr_neuron = self.mother_grid[curr_idx]
                if curr_neuron is None:
                    continue
                target_y = max(
                    0, min(
                        GRID_Y - 1,
                        y + _random.randint(-SPREAD,SPREAD)
                        )
                    )
                next_idx = coord_to_idx(x + 1,target_y)
                next_neuron = self.mother_grid[next_idx]
                if next_neuron is not None:
                    if not curr_neuron.has_conn_with(next_idx):
                        curr_neuron.add_output_conn(next_idx)
                        next_neuron.add_input_conn(curr_idx)

    def initialize(self):
        self.initialize_boundary_neurons()
        self.fill_active_neurons()
        self.setup_initial_connections()

    def reset_state(self):
        # 重置
        # 清除所有活动神经元的信号
        for idx in self.active_indices:
            neuron = self.mother_grid[idx]
            if neuron is not None:
                neuron.input_val = 0
                neuron.refractory = 9
        # 清除输入层和输出层神经元的信号
        for indices in [get_input_layer_indices(), get_output_layer_indices()]:
            for idx in indices:
                neuron = self.mother_grid[idx]
                if neuron is not None:
                    neuron.input_val = 0
                    neuron.refractory = 9

        # 清除扩散场
        self.diffusion_field.clear()

        # 子本回满
        self.child_array.reset_all(30)

        # 清除输出状态
        for i in range(len(self.output_state)):
            self.output_state[i] = 0

        # 注意：不重建连接！保留有机连接通路






    # 主循环
    def process_text(self, text: str) -> str:
        # 还原文字
        # 步骤0: 重置状态，确保从干净状态开始
        self.reset_state()

        # 编码输入文本
        input_digits = encode_text(text)
        if not input_digits:
            return ""

        # 按输入层大小分块
        chunk_size = INPUT_LAYER_SIZE
        output_texts = []

        for chunk_start in range(0, len(input_digits), chunk_size):
            chunk = input_digits[chunk_start:chunk_start + chunk_size]

            # 填充到输入层大小（不足补0）
            padded = chunk + [0] * (chunk_size - len(chunk))

            # 步骤1: 喂入输入层
            self._feed_input_layer(padded)

            # 步骤2: 全量扩散渲染
            self._step_diffusion()

            # 步骤3: 单神经元串行处理
            self._step_neuron_processing()

            # 步骤4: 全量信号传递
            self._step_signal_propagation()

            # 步骤5: 读取输出层并解码
            output_text = self._read_output_layer()
            if output_text:
                output_texts.append(output_text)

            self.current_round += 1

        # 提问完成，子本全部回满
        self.child_array.reset_all(30)

        return ''.join(output_texts)


    # 步骤1: 喂入输入层
    def _feed_input_layer(self, values: List[int]):
        # 列表写入传入层神经元
        input_indices = get_input_layer_indices()
        for i, idx in enumerate(input_indices):
            neuron = self.mother_grid[idx]
            if neuron is not None and i < len(values):
                neuron.set_input_val(values[i])





    # 步骤2: 全量扩散渲染
    def _step_diffusion(self):
        # 遍历所有中间层神经元，执行预检查扩散渲染
        # 渲染完成后执行 refractory 扣除与恢复




        # 全量扩散渲染
        for active_idx, global_idx in enumerate(self.active_indices):
            neuron = self.mother_grid[global_idx]
            if neuron is not None:
                self.diffusion_engine.render_diffusion_with_pre_check(
                    neuron, 
                    active_idx
                    )

        # refractory 扣除: ≤5 扣1, >5 扣2
        for neuron in self.mother_grid:
            if neuron is not None:
                if neuron.refractory <= 5:
                    neuron.refractory = max(0,neuron.refractory - 1)
                else:
                    neuron.refractory = max(0,neuron.refractory - 2)

        # 全量渲染后 refractory += 2
        for neuron in self.mother_grid:
            if neuron is not None:
                neuron.refractory = min(9,neuron.refractory + 2)




    # 单神经元串行全链路处理
    def _step_neuron_processing(self):
        # 按线性顺序逐个处理中间层每个神经元
       
        for active_idx, global_idx in enumerate(self.active_indices):
            neuron = self.mother_grid[global_idx]
            if neuron is None:
                continue

            #1 退火
            self.diffusion_engine.anneal(neuron)

            #2 移动判定与执行
            self.movement_engine.process_neuron_move(
                neuron, active_idx, self.mother_grid)

            #3 连接生长尝试（所有神经元都参与）
            self.connection_engine.try_grow_connection(
                neuron, 
                self.mother_grid
                )

            #4 复渲染
            self.diffusion_engine.re_render(neuron)






    # 步骤4: 全量信号传递
    def _step_signal_propagation(self):
        # BFS广度优先信号传递
        self.signal_engine.propagate_signals(
            self.mother_grid, 
            self.output_state
            )







    # 全局时效更新
    def _step_refractory_update(self):
        # 更新所有神经元的时效值
        recovery = self.api.get_param('refractory_recovery_amount')
        if recovery is None:
            recovery = 1
        for neuron in self.mother_grid:
            if neuron is not None:
                neuron.update_refractory(recovery)


   



    # 读取输出层
    def _read_output_layer(self) -> str:
        # 读取传出层状态并解码
        output_values = []# 从传出层神经元读取 input_val
        output_indices = get_output_layer_indices()
        for i, idx in enumerate(output_indices):
            neuron = self.mother_grid[idx]
            if neuron is not None:
                output_values.append(neuron.input_val)
            else:
                output_values.append(0)

        return decode_output(output_values)



    # 便捷方法
    def get_active_neurons(self) -> List[Neuron]:
        """获取所有活动神经元列表。"""
        neurons = []
        for idx in self.active_indices:
            neuron = self.mother_grid[idx]
            if neuron is not None:
                neurons.append(neuron)
        return neurons

    def get_neuron_count(self) -> int:
        # 获取活动神经元数量
        count = 0
        for idx in self.active_indices:
            if self.mother_grid[idx] is not None:
                count += 1
        return count







    def print_status(self):
        """
        print(f"=== 轮次 {self.current_round} ===")
        print(f"活动神经元数: {self.get_neuron_count()}")
        print(f"传出层非零信号数: {sum(1 for v in self.output_state if v > 0)}")
        print(f"随机池大小: {self.random_pool.size}")
        """


def load_or_create_system(
        name: str = "default",
        neuron_density : float = 1.0) -> BrainGrid2D:


    
    # 加载已有容器或创建新容器
    try:
        from .container_io import load_container, save_container, container_exists
    except ImportError:
        from container_io import load_container, save_container, container_exists

    if container_exists(name):
        print(f"[加载] 从容器 '{name}' 恢复系统状态...")
        system = load_container(name)
        if system is not None:
            neuron_count = system.get_neuron_count()
            print(
                f"[加载] 完成: {neuron_count} 个活动神经元, "
                f"当前轮次 {system.current_round}"
                )
            return system
        print(f"[加载] 容器 '{name}' 损坏，将创建新容器")

    # 创建新容器
    print(f"[新建] 创建容器 '{name}' (密度={neuron_density})...")
    system = BrainGrid2D(neuron_density=neuron_density)
    system.initialize()
    neuron_count = system.get_neuron_count()
    print(f"[新建] 完成: {neuron_count} 个活动神经元, "
          f"总格子 {TOTAL_CELLS} 个")
    save_container(system, name)
    return system


def create_system(neuron_density: float = 1.0) -> BrainGrid2D:
    # 创建并初始化
    print(f"正在初始化 ({GRID_X}×{GRID_Y}, 密度={neuron_density})...")
    system = BrainGrid2D(neuron_density=neuron_density)
    system.initialize()
    neuron_count = system.get_neuron_count()
    print(
        "初始化完成: {neuron_count} 个活动神经元, "
          f"总 {TOTAL_CELLS} 个"
          )
    return system


def interactive_loop(
        system: Optional[BrainGrid2D] = None,
        container_name: str = "default"
        ):
    if system is None:
        system = load_or_create_system(container_name)

    print("\n" + "=" * 50)
    print(f"容器: {container_name}")
    print("=" * 50 + "\n")

    try:
        while True:
            try:
                user_input = input("输入> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[中断]")
                break

            if not user_input:
                continue
            if user_input.lower() in ('quit', 'exit'):
                break

            # 处理文本
            output = system.process_text(user_input)
            print(f"输出> {output}\n")
    finally:
        # 退出时自动保存容器
        try:
            from .container_io import save_container
        except ImportError:
            from container_io import save_container
        save_container(system, container_name)


if __name__ == '__main__':
    system = load_or_create_system()
    interactive_loop(system)