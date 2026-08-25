import sys
import os
import json
import gzip
import random
from typing import List, Optional

from core import (
    GRID_X,
    GRID_Y,
    TOTAL_CELLS,
    ACTIVE_X_MIN,
    ACTIVE_X_MAX,
    INPUT_LAYER_SIZE,
    OUTPUT_LAYER_SIZE,
    coord_to_idx,
    idx_to_coord,
    get_all_active_indices,
    get_input_layer_indices,
    get_output_layer_indices,
    Neuron,
    RandomPool,
    DiffusionField,
)
from engines import (
    DiffusionEngine,
    MovementEngine,
    ConnectionEngine,
    SignalEngine,
)
from text_io import encode_text, decode_output


# =====================================================================
# 主循环调度
# =====================================================================

class BrainGrid2D:
    def __init__(self, neuron_density: float = 1.0):
        self.current_round: int = 0
        self.neuron_density: float = max(0.001, min(1.0, neuron_density))
        self.neuron_grid: List[Optional[Neuron]] = [None] * TOTAL_CELLS
        self.diffusion_field: DiffusionField = DiffusionField()
        self.random_pool: RandomPool = RandomPool()

        self.connection_engine: ConnectionEngine = ConnectionEngine(
            self.diffusion_field, self.random_pool)
        self.diffusion_engine: DiffusionEngine = DiffusionEngine(
            self.diffusion_field)
        self.movement_engine: MovementEngine = MovementEngine(
            self.diffusion_field, self.random_pool, self.connection_engine)
        self.signal_engine: SignalEngine = SignalEngine(self.connection_engine)

        self.output_state: List[int] = [0] * OUTPUT_LAYER_SIZE
        self.active_indices: List[int] = get_all_active_indices()
        self.boundary_indices: List[int] = (
            get_input_layer_indices() + get_output_layer_indices()
        )

    # ---- 初始化 ----
    def initialize_boundary_neurons(self):
        for idx in get_input_layer_indices():
            _, y = idx_to_coord(idx)
            self.neuron_grid[idx] = Neuron(0, y, input_val=0, refractory=9)
        for idx in get_output_layer_indices():
            _, y = idx_to_coord(idx)
            self.neuron_grid[idx] = Neuron(GRID_X - 1, y, input_val=0, refractory=9)

    def fill_active_neurons(self):
        for x in range(ACTIVE_X_MIN, ACTIVE_X_MAX + 1):
            for y in range(GRID_Y):
                if random.random() < self.neuron_density:
                    idx = coord_to_idx(x, y)
                    self.neuron_grid[idx] = Neuron(x, y, input_val=0, refractory=9)

    def setup_initial_connections(self):
        SPREAD = 4
        # 输入层连接到活动区第一列附近随机神经元
        for y in range(GRID_Y):
            in_idx = coord_to_idx(0, y)
            in_neuron = self.neuron_grid[in_idx]
            if in_neuron is None:
                continue
            target_y = max(0, min(GRID_Y - 1, y + random.randint(-SPREAD, SPREAD)))
            x1_idx = coord_to_idx(1, target_y)
            x1_neuron = self.neuron_grid[x1_idx]
            if x1_neuron is not None:
                in_neuron.add_output_conn(x1_idx)
                x1_neuron.add_input_conn(in_idx)

        # 活动区最后一列连接到输出层
        for y in range(GRID_Y):
            x214_idx = coord_to_idx(ACTIVE_X_MAX, y)
            x214_neuron = self.neuron_grid[x214_idx]
            out_idx = coord_to_idx(GRID_X - 1, y)
            out_neuron = self.neuron_grid[out_idx]
            if x214_neuron is not None and out_neuron is not None:
                x214_neuron.add_output_conn(out_idx)
                out_neuron.add_input_conn(x214_idx)

        # 活动区相邻列随机前向连接
        for x in range(ACTIVE_X_MIN, ACTIVE_X_MAX):
            for y in range(GRID_Y):
                curr_idx = coord_to_idx(x, y)
                curr_neuron = self.neuron_grid[curr_idx]
                if curr_neuron is None:
                    continue
                target_y = max(0, min(GRID_Y - 1, y + random.randint(-SPREAD, SPREAD)))
                next_idx = coord_to_idx(x + 1, target_y)
                next_neuron = self.neuron_grid[next_idx]
                if next_neuron is not None:
                    if not curr_neuron.has_conn_with(next_idx):
                        curr_neuron.add_output_conn(next_idx)
                        next_neuron.add_input_conn(curr_idx)

    def initialize(self):
        self.initialize_boundary_neurons()
        self.fill_active_neurons()
        self.setup_initial_connections()

    # ---- 每轮重置 ----
    def reset_state(self):
        for neuron in self.neuron_grid:
            if neuron is not None:
                neuron.input_val = 0
        self.diffusion_field.clear()
        for i in range(len(self.output_state)):
            self.output_state[i] = 0

    # ---- 主循环 ----
    def process_text(self, text: str) -> str:
        self.reset_state()

        input_digits = encode_text(text)
        if not input_digits:
            return ""

        chunk_size = INPUT_LAYER_SIZE
        output_texts = []

        for chunk_start in range(0, len(input_digits), chunk_size):
            chunk = input_digits[chunk_start:chunk_start + chunk_size]
            padded = chunk + [0] * (chunk_size - len(chunk))

            # 3 喂入输入层
            self._feed_input_layer(padded)
            # 4 填充随机池（原始数字，跨块累积）
            self.random_pool.add_input_digits(chunk)
            # 5 全局扩散渲染
            self._step_diffusion_all()
            # 6 逐个神经元串行处理
            self._step_neuron_processing()
            # 7 信号传播
            self.signal_engine.propagate_signals(self.neuron_grid, self.output_state)
            # 8 断开检测
            self.connection_engine.disconnect_all_over_distance(self.neuron_grid)
            # 9 读取输出
            output_text = self._read_output_layer()
            if output_text:
                output_texts.append(output_text)
            # 10 不应期恢复
            self._recover_refractory()
            # 11 轮次增加
            self.current_round += 1

        return ''.join(output_texts)

    def _feed_input_layer(self, values: List[int]):
        for i, idx in enumerate(get_input_layer_indices()):
            neuron = self.neuron_grid[idx]
            if neuron is not None and i < len(values):
                neuron.set_input_val(values[i])

    def _step_diffusion_all(self):
        # 有效区与传入/传出层神经元一并参与扩散渲染（渲染允许）
        for gidx in self.active_indices + self.boundary_indices:
            neuron = self.neuron_grid[gidx]
            if neuron is not None:
                self.diffusion_engine.render_diffusion(neuron)

    def _step_neuron_processing(self):
        # 有效区神经元：完整流水线
        for gidx in self.active_indices:
            neuron = self.neuron_grid[gidx]
            if neuron is None:
                continue
            self.diffusion_engine.anneal(neuron)
            self.movement_engine.process_neuron_move(neuron, self.neuron_grid)
            self.connection_engine.try_grow_connection(neuron, self.neuron_grid)
            self.diffusion_engine.re_render(neuron)

        # 传入/传出层神经元（三不管：不退火/不移动/不复渲染）：仅连接生长
        for gidx in self.boundary_indices:
            neuron = self.neuron_grid[gidx]
            if neuron is None:
                continue
            self.connection_engine.try_grow_connection(neuron, self.neuron_grid)

    def _recover_refractory(self):
        for neuron in self.neuron_grid:
            if neuron is not None:
                neuron.update_refractory(3)

    def _read_output_layer(self) -> str:
        output_values = []
        for idx in get_output_layer_indices():
            neuron = self.neuron_grid[idx]
            output_values.append(neuron.input_val if neuron is not None else 0)
        return decode_output(output_values)

    def get_neuron_count(self) -> int:
        count = 0
        for gidx in self.active_indices:
            if self.neuron_grid[gidx] is not None:
                count += 1
        return count


# =====================================================================
# 容器持久化
# =====================================================================

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTAINER_DIR = os.path.join(_MODULE_DIR, "containers")


def _ensure_dir():
    os.makedirs(CONTAINER_DIR, exist_ok=True)


def _container_path(name: str) -> str:
    return os.path.join(CONTAINER_DIR, f"{name}.json.gz")


def container_exists(name: str) -> bool:
    return os.path.exists(_container_path(name))


def list_containers() -> List[str]:
    if not os.path.exists(CONTAINER_DIR):
        return []
    containers = []
    for f in os.listdir(CONTAINER_DIR):
        if f.endswith(".json.gz"):
            containers.append(f[:-8])
    return sorted(containers)


def save_container(system: BrainGrid2D, name: str):
    _ensure_dir()

    neurons_data = [None if n is None else n.to_dict() for n in system.neuron_grid]

    data = {
        "neurons": neurons_data,
        "diffusion_field": system.diffusion_field.get_field(),
        "random_pool_values": list(system.random_pool._pool),
        "random_pool_pointer": system.random_pool._pointer,
        "current_round": system.current_round,
        "output_state": list(system.output_state),
        "neuron_density": system.neuron_density,
    }

    json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    compressed = gzip.compress(json_str.encode('utf-8'))
    filepath = _container_path(name)

    with open(filepath, 'wb') as f:
        f.write(compressed)

    size_kb = os.path.getsize(filepath) / 1024
    print(f"[保存] 容器 '{name}' 已保存: {filepath} ({size_kb:.1f} KB)")


def load_container(name: str) -> Optional[BrainGrid2D]:
    filepath = _container_path(name)
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'rb') as f:
            compressed = f.read()
        json_str = gzip.decompress(compressed).decode('utf-8')
        data = json.loads(json_str)
    except (json.JSONDecodeError, gzip.BadGzipFile, KeyError, EOFError) as e:
        print(f"[警告] 容器文件 '{name}' 损坏: {e}")
        return None

    density = data.get('neuron_density', 1.0)
    system = BrainGrid2D(neuron_density=density)
    system.current_round = data.get('current_round', 0)
    system.output_state = data.get('output_state', [0] * OUTPUT_LAYER_SIZE)

    neurons_data = data.get('neurons', [])
    for i, nd in enumerate(neurons_data):
        if i >= TOTAL_CELLS:
            break
        if nd is None:
            system.neuron_grid[i] = None
        else:
            system.neuron_grid[i] = Neuron.from_dict(nd)

    diff_data = data.get('diffusion_field', [])
    if len(diff_data) == len(system.diffusion_field._field):
        system.diffusion_field._field = diff_data.copy()

    pool_values = data.get('random_pool_values', [])
    system.random_pool._pool = pool_values
    system.random_pool._pointer = data.get('random_pool_pointer', 0)

    system.active_indices = get_all_active_indices()
    return system


# =====================================================================
# 模块级入口函数
# =====================================================================

def load_or_create_system(name: str = "default",
                          neuron_density: float = 1.0) -> BrainGrid2D:
    if container_exists(name):
        print(f"[加载] 从容器 '{name}' 恢复系统状态...")
        system = load_container(name)
        if system is not None:
            print(f"[加载] 完成: {system.get_neuron_count()} 个活动神经元, "
                  f"当前轮次 {system.current_round}")
            return system
        print(f"[加载] 容器 '{name}' 损坏，将创建新容器")

    print(f"[新建] 创建容器 '{name}' (密度={neuron_density})...")
    system = BrainGrid2D(neuron_density=neuron_density)
    system.initialize()
    print(f"[新建] 完成: {system.get_neuron_count()} 个活动神经元, "
          f"总格子 {TOTAL_CELLS} 个")
    save_container(system, name)
    return system


def interactive_loop(system: Optional[BrainGrid2D] = None,
                     container_name: str = "default"):
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

            output = system.process_text(user_input)
            print(f"输出> {output}\n")
    finally:
        save_container(system, container_name)


def main():
    args = sys.argv[1:]

    if args and args[0] == "create":
        if len(args) < 2:
            print("用法: python main.py create <容器名称> [神经元密度]")
            print(f"已有容器: {list_containers()}")
            sys.exit(1)
        name = args[1]
        density = float(args[2]) if len(args) > 2 else 1.0

        if container_exists(name):
            print(f"[错误] 容器 '{name}' 已存在，请使用其他名称或删除后重试")
            sys.exit(1)

        print(f"正在创建容器 '{name}' (密度={density})...")
        system = BrainGrid2D(neuron_density=density)
        system.initialize()
        print(f"创建完成: {system.get_neuron_count()} 个活动神经元")
        save_container(system, name)
        print(f"容器已保存，可用 'python main.py {name}' 启动")
        return

    container_name = args[0] if args else "default"
    system = load_or_create_system(container_name)
    interactive_loop(system, container_name)


if __name__ == '__main__':
    main()