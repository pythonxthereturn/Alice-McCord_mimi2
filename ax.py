# -*- coding: utf-8 -*-
import numpy as np
import random

# ===========================================================================
# 全局配置与常量（与主程序保持一致，保证序列化兼容）
# ===========================================================================
GRID_SIDE_LENGTH = 32
TOTAL_CELLS = 1024
SEED_BRIGHTNESS = 4
DEFAULT_GRID_LAYERS = 5
DEFAULT_FILE_SUFFIX = ".exdc"
GRID_FILE_NAME = "Alice_McCord"

# ===========================================================================
# Point 类（与 app.py 完全一致，解决跨文件序列化识别问题）
# ===========================================================================
class Point:
    """32x32 grid node class."""
    def __init__(self, center_index: int, brightness: int,
                 control_ports: list | None = None,
                 input_ports: list | None = None,
                 output_ports: list | None = None,
                 is_api: bool = False,
                 api_signal: int = 0):
        self.center_index = center_index
        self.brightness = brightness
        self.control_ports = [] if control_ports is None else control_ports
        self.input_ports = [] if input_ports is None else input_ports
        self.output_ports = [] if output_ports is None else output_ports
        self.is_api = is_api
        self.api_signal = api_signal

# ===========================================================================
# 网格生成函数
# ===========================================================================
def generate_random_grid(
    layers: int = DEFAULT_GRID_LAYERS,
    points_per_layer: int = 256,
    seed_brightness: int = SEED_BRIGHTNESS
) -> np.ndarray:
    """生成指定层数、随机节点的网格"""
    grid = np.zeros((layers, TOTAL_CELLS), dtype=object)
    for layer_idx in range(layers):
        # 随机选取节点索引
        point_indices = random.sample(range(TOTAL_CELLS), points_per_layer)
        for idx in point_indices:
            grid[layer_idx][idx] = Point(
                center_index=idx,
                brightness=seed_brightness
            )
    print(f"✅ 随机网格生成完成：{layers} 层 × {TOTAL_CELLS} 单元格，每层 {points_per_layer} 个节点")
    return grid

# ===========================================================================
# 网格保存函数（标准 .exdc 格式）
# ===========================================================================
def save_grid_to_binary(
    grid: np.ndarray,
    filename: str,
    suffix: str = DEFAULT_FILE_SUFFIX
) -> None:
    """将网格保存为 exdc 二进制文件"""
    full_filename = f"{filename}{suffix}"
    with open(full_filename, "wb") as f:
        np.save(f, grid, allow_pickle=True)
    print(f"✅ 网格已成功保存至：{full_filename}")

# ===========================================================================
# 主执行入口
# ===========================================================================
if __name__ == "__main__":
    # 生成 5 层网格，每层 256 个随机节点
    target_grid = generate_random_grid(
        layers=5,
        points_per_layer=256,
        seed_brightness=4
    )

    # 保存为 Alice_McCord.exdc（与主程序读取名称对应）
    save_grid_to_binary(
        grid=target_grid,
        filename=GRID_FILE_NAME,
        suffix=DEFAULT_FILE_SUFFIX
    )