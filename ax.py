# -*- coding: utf-8 -*-
import numpy as np
import random
import os

# ===========================================================================
# 全局配置（这里统一改后缀为.exdc）
# ===========================================================================
GRID_SIDE_LENGTH = 32
TOTAL_CELLS = 1024
SEED_BRIGHTNESS = 4
DEFAULT_GRID_LAYERS = 5
DEFAULT_POINTS_PER_LAYER = 12  # 每层随机12个点，可改
DEFAULT_FILE_SUFFIX = ".esbc"  # ✅ 你的自定义后缀

# ===========================================================================
# Point类（和主程序完全一致）
# ===========================================================================
class Point:
    """32x32 grid node class."""
    def __init__(self, center_index: int, brightness: int,
                 control_ports: list | None = None,
                 input_ports: list | None = None,
                 output_ports: list | None = None):
        self.center_index = center_index
        self.brightness = brightness
        self.control_ports = [] if control_ports is None else control_ports
        self.input_ports = [] if input_ports is None else input_ports
        self.output_ports = [] if output_ports is None else output_ports

# ===========================================================================
# 生成随机网格（不变）
# ===========================================================================
def generate_random_grid(
    layers: int = DEFAULT_GRID_LAYERS,
    points_per_layer: int = DEFAULT_POINTS_PER_LAYER,
    seed_brightness: int = SEED_BRIGHTNESS
) -> np.ndarray:
    grid = np.zeros((layers, TOTAL_CELLS), dtype=object)
    for layer_idx in range(layers):
        point_indices = random.sample(range(TOTAL_CELLS), points_per_layer)
        for idx in point_indices:
            grid[layer_idx][idx] = Point(
                center_index=idx,
                brightness=seed_brightness
            )
    print(f"✅ 网格生成完成：{layers}层 × {TOTAL_CELLS}格，每层{points_per_layer}个随机点")
    return grid

# ===========================================================================
# ✅ 修正：保存为纯.exdc后缀（禁止numpy自动加.npy）
# ===========================================================================
def save_grid_to_binary(
    grid: np.ndarray,
    filename: str,
    suffix: str = DEFAULT_FILE_SUFFIX
) -> None:
    full_filename = f"{filename}{suffix}"
    # 关键：用文件对象保存，numpy不会自动加后缀
    with open(full_filename, "wb") as f:
        np.save(f, grid, allow_pickle=True)
    print(f"✅ 网格已保存为：{full_filename}（无多余后缀）")

# ===========================================================================
# ✅ 修正：读取.exdc后缀文件
# ===========================================================================
def load_grid_component(
    filename: str,
    suffix: str = DEFAULT_FILE_SUFFIX,
    layer: int | None = None,
    index_range: tuple | None = None
) -> np.ndarray:
    full_filename = f"{filename}{suffix}"
    # 关键：用文件对象读取，避免numpy自动补.npy
    with open(full_filename, "rb") as f:
        full_grid = np.load(f, allow_pickle=True)
    
    if layer is not None:
        full_grid = full_grid[layer:layer+1]
    if index_range is not None:
        start, end = index_range
        full_grid = full_grid[:, start:end]
    
    print(f"✅ 分量读取完成：加载了{full_grid.shape[0]}层，每层{full_grid.shape[1]}个单元格")
    return full_grid

# ===========================================================================
# 示例用法（注释掉分量读取，避免报错）
# ===========================================================================
if __name__ == "__main__":
    # 1. 生成随机网格
    my_grid = generate_random_grid(
        layers=5,
        points_per_layer=12,
        seed_brightness=4
    )
    
    # 2. 保存为 my_custom_grid.exdc
    save_grid_to_binary(
        grid=my_grid,
        filename="Alice_McCord",
        suffix=".exdc"
    )
    
    # 3. 注释掉分量读取，避免刚保存就读取的测试报错
    # partial_grid = load_grid_component(
    #     filename="my_custom_grid",
    #     suffix=".exdc",
    #     layer=1,
    #     index_range=(0, 200)
    # )