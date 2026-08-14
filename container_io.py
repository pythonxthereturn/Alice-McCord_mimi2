import os
import json
import gzip
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from .main import BrainGrid2D



# 容器持久化模块
# BrainGrid2D保存和加载。
# JSON+gzip 格式，保存到项目根目录的 containers/ 文件夹。
# 容器文件夹（2D/containers/）





_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTAINER_DIR = os.path.join(_MODULE_DIR,"containers")
def _ensure_dir():
    # 确保容器文件夹存在
    os.makedirs(CONTAINER_DIR,exist_ok=True)
def _container_path(name: str) -> str:
    # 获取容器文件路径
    return os.path.join(CONTAINER_DIR,f"{name}.json.gz")
def container_exists(name: str) -> bool:
    # 检查指定名称的容器是否存在
    return os.path.exists(_container_path(name))
def list_containers() -> List[str]:
    # 列出所有已保存的容器名称
    if not os.path.exists(CONTAINER_DIR):
        return []
    containers = []
    for f in os.listdir(CONTAINER_DIR):
        if f.endswith(".json.gz"):
            containers.append(f[:-8])  # 去掉 .json.gz 后缀
    return sorted(containers)


def save_container(system: 'BrainGrid2D', name: str):
    # 将 BrainGrid2D 系统状态保存到容器文件。
    _ensure_dir()

    # 序列化神经元
    neurons_data = []
    for neuron in system.mother_grid:
        if neuron is None:
            neurons_data.append(None)
        else:
            neurons_data.append(neuron.to_dict())

    data = {
        "neurons": neurons_data,
        "child_array": system.child_array.get_data(),
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


def load_container(name: str) -> Optional['BrainGrid2D']:
    
    # 从容器文件加载 BrainGrid2D 系统状态。
    # name: 容器名称（不含扩展名）
    # BrainGrid2D 实例，文件不存在或损坏返回 None
    # 延迟导入避免循环依赖

    try:
        from .neuron import Neuron
    except ImportError:
        from neuron import Neuron
    try:
        from .main import BrainGrid2D
    except ImportError:
        from main import BrainGrid2D


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

    # 重建系统
    density = data.get('neuron_density', 1.0)
    system = BrainGrid2D(neuron_density=density)
    system.current_round = data.get('current_round', 0)
    system.output_state = data.get('output_state', [0] * 1024)

    # 恢复神经元
    neurons_data = data['neurons']
    for i, nd in enumerate(neurons_data):
        if nd is None:
            system.mother_grid[i] = None
        else:
            neuron = Neuron.from_dict(nd)
            system.mother_grid[i] = neuron

    # 恢复扩散场
    diff_data = data.get('diffusion_field', [])
    if len(diff_data) == len(system.diffusion_field._field):
        system.diffusion_field._field = diff_data

    # 恢复子本
    child_data = data.get('child_array', [])
    if len(child_data) == len(system.child_array._data):
        system.child_array._data = child_data

    # 恢复随机池
    pool_values = data.get('random_pool_values', [])
    system.random_pool._pool = pool_values
    system.random_pool._pointer = data.get('random_pool_pointer', 0)

    # 重建 active_indices（包含所有有神经元的活动格子）
    try:
        from .grid import get_all_active_indices
    except ImportError:
        from grid import get_all_active_indices
    system.active_indices = get_all_active_indices()

    return system