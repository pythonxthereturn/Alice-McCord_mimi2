from typing import Optional, Tuple, List



# 容器常量
GRID_X: int = 1080         # X轴: 水平列，取值 0~1079
GRID_Y: int = 1024         # Y轴: 垂直行，取值 0~1023
LAYER_SIZE: int = GRID_Y   # 每列格子数 = 1024
TOTAL_CELLS: int = GRID_X * GRID_Y  # 全网格总格子数 = 1,105,920
ACTIVE_X_MIN: int = 1 # 可活动区域: X=1~1078
ACTIVE_X_MAX: int = GRID_X - 2  # 1078
ACTIVE_COLS: int = ACTIVE_X_MAX - ACTIVE_X_MIN + 1  # 1078列
ACTIVE_CELLS: int = ACTIVE_COLS * GRID_Y  # 1,103,872个可活动格子

# 边界层
INPUT_LAYER_X: int = 0           # 传入神经层 (X=0)
OUTPUT_LAYER_X: int = GRID_X - 1 # 传出神经层 (X=1079)
INPUT_LAYER_SIZE: int = GRID_Y   # 传入层格子数 = 1024
OUTPUT_LAYER_SIZE: int = GRID_Y  # 传出层格子数 = 1024

# 子本初始值
DEFAULT_CHILD_VALUE: int = 30

# 上 下 左 右
# 1  2  3  4
DIRECTION_OFFSETS: List[Tuple[int,int]] = [
    (0, -1),    # 1: 上 (Y-1)
    (0, 1),     # 2: 下 (Y+1)
    (-1, 0),    # 3: 左 (X-1)
    (1, 0),     # 4: 右 (X+1)
]


def coord_to_idx(x: int, y: int) -> int:
    # 将二维坐标转换为一维索引。
    # 公式: idx = y * GRID_X + x

    return y * GRID_X + x


def idx_to_coord(idx: int) -> Tuple[int,int]:
    # 将一维索引转换为二维坐标。
    y = idx // GRID_X
    x = idx % GRID_X
    return (x, y)


def active_idx_to_global_idx(active_idx: int) -> int:
    return active_idx + GRID_Y  # 跳过 X=0 的1024个格子


def global_idx_to_active_idx(global_idx: int) -> Optional[int]:
    # 将母本索引转换为子本索引
    # 仅中间214列有效，边界列返回 None。

    x = global_idx % GRID_X
    if x < ACTIVE_X_MIN or x > ACTIVE_X_MAX:
        return None
    return global_idx - GRID_Y






def is_active_col(x: int) -> bool:
    # 判断X坐标是否在可活动列范围内
    return ACTIVE_X_MIN <= x <= ACTIVE_X_MAX

# 判断二维坐标是否在有效范围内
def is_valid_coord(x: int, y: int) -> bool:
    return 0 <= x < GRID_X and 0 <= y < GRID_Y

def is_active_cell(x: int, y: int) -> bool:
    return is_valid_coord(x, y) and is_active_col(x)# 判断格子是否在可活动区域内


def manhattan_distance(
        coord1: Tuple[int,int],
        coord2: Tuple[int,int]) -> int:
    # 计算两个二维坐标的曼哈顿距离。
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])


def get_neighbor_coords(x: int, y: int) -> List[Tuple[int, int]]:
    # 获取四邻域坐标
    neighbors = []
    for dx, dy in DIRECTION_OFFSETS:
        nx, ny = x + dx, y + dy
        if is_valid_coord(nx, ny):
            neighbors.append((nx, ny))
    return neighbors




def get_neighbor_indices(idx:int) -> List[int]:
    # 获取四邻域的一维索引列表。
    x, y = idx_to_coord(idx)
    neighbors = []
    for dx, dy in DIRECTION_OFFSETS:
        nx, ny = x + dx, y + dy
        if is_valid_coord(nx, ny):
            neighbors.append(coord_to_idx(nx,ny))
    return neighbors




def get_active_neighbor_indices(idx:int) -> List[int]:
    # 获取四邻域中可活动区域的一维索引列表
    # idx: 中心格子的一维索引
    x, y = idx_to_coord(idx)
    neighbors = []
    for dx, dy in DIRECTION_OFFSETS:
        nx, ny = x + dx, y + dy
        if is_active_cell(nx, ny):
            neighbors.append(coord_to_idx(nx,ny))
    return neighbors




def direction_to_offset(direction : int) -> Tuple[int,int]:
    # 将方向转换为坐标偏移量
    return DIRECTION_OFFSETS[direction - 1]


def get_all_active_indices() -> List[int]:
    # 获取所有可活动格子的母本一维索引列表。
    indices = []
    for x in range(ACTIVE_X_MIN, ACTIVE_X_MAX + 1):
        for y in range(GRID_Y):
            indices.append(coord_to_idx(x, y))
    return indices


def get_input_layer_indices() -> List[int]:
    # 获取传入层所有格子的一维索引列表
    return [coord_to_idx(INPUT_LAYER_X,y) for y in range(GRID_Y)]
def get_output_layer_indices() -> List[int]:
    # 获取传出层所有格子的一维索引列表
    return [coord_to_idx(OUTPUT_LAYER_X,y) for y in range(GRID_Y)]