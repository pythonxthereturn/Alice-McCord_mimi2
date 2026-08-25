from typing import List, Optional, Tuple


# =====================================================================
# 常量与坐标工具函数
# =====================================================================

# 网格尺寸
GRID_X: int = 1080         # 水平列数，0~1079
GRID_Y: int = 1024         # 垂直行数，0~1023
LAYER_SIZE: int = GRID_Y   # 每列格子数 = 1024
TOTAL_CELLS: int = GRID_X * GRID_Y  # 全网格总格子数 = 1,105,920

# 活动区域
ACTIVE_X_MIN: int = 1
ACTIVE_X_MAX: int = GRID_X - 2      # 1078
ACTIVE_COLS: int = ACTIVE_X_MAX - ACTIVE_X_MIN + 1   # 1078
ACTIVE_CELLS: int = ACTIVE_COLS * GRID_Y             # 1,103,872

# 边界层
INPUT_LAYER_X: int = 0
OUTPUT_LAYER_X: int = GRID_X - 1
INPUT_LAYER_SIZE: int = GRID_Y
OUTPUT_LAYER_SIZE: int = GRID_Y

# 方向定义：1 上 / 2 下 / 3 左 / 4 右
DIRECTION_OFFSETS: List[Tuple[int, int]] = [
    (0, -1),    # 1: 上
    (0, 1),     # 2: 下
    (-1, 0),    # 3: 左
    (1, 0),     # 4: 右
]


def coord_to_idx(x: int, y: int) -> int:
    return y * GRID_X + x


def idx_to_coord(idx: int) -> Tuple[int, int]:
    y = idx // GRID_X
    x = idx % GRID_X
    return (x, y)


def is_valid_coord(x: int, y: int) -> bool:
    return 0 <= x < GRID_X and 0 <= y < GRID_Y


def is_active_cell(x: int, y: int) -> bool:
    return is_valid_coord(x, y) and ACTIVE_X_MIN <= x <= ACTIVE_X_MAX


def manhattan_distance(
        coord1: Tuple[int, int],
        coord2: Tuple[int, int]) -> int:
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])


def get_neighbor_indices(idx: int) -> List[int]:
    """获取四邻域一维索引，不区分边界层。"""
    x, y = idx_to_coord(idx)
    result = []
    for dx, dy in DIRECTION_OFFSETS:
        nx, ny = x + dx, y + dy
        if is_valid_coord(nx, ny):
            result.append(coord_to_idx(nx, ny))
    return result


def get_active_neighbor_indices(idx: int) -> List[int]:
    """获取四邻域中仅活动区的索引。"""
    x, y = idx_to_coord(idx)
    result = []
    for dx, dy in DIRECTION_OFFSETS:
        nx, ny = x + dx, y + dy
        if is_active_cell(nx, ny):
            result.append(coord_to_idx(nx, ny))
    return result


def get_all_active_indices() -> List[int]:
    """获取所有可活动格子的母本一维索引列表。"""
    indices = []
    for x in range(ACTIVE_X_MIN, ACTIVE_X_MAX + 1):
        for y in range(GRID_Y):
            indices.append(coord_to_idx(x, y))
    return indices


def get_input_layer_indices() -> List[int]:
    return [coord_to_idx(INPUT_LAYER_X, y) for y in range(GRID_Y)]


def get_output_layer_indices() -> List[int]:
    return [coord_to_idx(OUTPUT_LAYER_X, y) for y in range(GRID_Y)]


# =====================================================================
# 神经元实体类
# =====================================================================

class Neuron:
    """
    神经元

    属性：
    - input_val: 当前输入信号强度 (0~9)
    - refractory: 不应期状态 (0~9)
    - input_conns: 输入端连接列表（目标神经元一维索引）
    - control_conns: 控制端连接列表
    - output_conns: 输出端连接列表
    - position: 二维坐标 (x, y)
    - render_radius: 扩散半径 (0~9)，等于三端连接总数（上限 9）
    """

    MAX_CONNS_PER_TYPE: int = 9
    MAX_TOTAL_CONNS: int = 27

    # 不应期阶段
    REFRACTORY_FULL: Tuple[int, int] = (0, 3)      # 绝对不应期
    REFRACTORY_MEDIUM: Tuple[int, int] = (4, 7)    # 中度不应期
    REFRACTORY_NORMAL: Tuple[int, int] = (8, 9)    # 正常期

    __slots__ = (
        'input_val',
        'refractory',
        'input_conns',
        'control_conns',
        'output_conns',
        'position',
        'render_radius',
    )

    def __init__(
            self,
            x: int,
            y: int,
            input_val: int = 0,
            refractory: int = 9):
        self.input_val: int = max(0, min(9, input_val))
        self.refractory: int = max(0, min(9, refractory))
        self.input_conns: List[int] = []
        self.control_conns: List[int] = []
        self.output_conns: List[int] = []
        self.position: Tuple[int, int] = (x, y)
        self.render_radius: int = 0

    # ---- 连接管理 ----
    def add_input_conn(self, target_idx: int) -> bool:
        if target_idx == self.get_idx():
            return False
        if len(self.input_conns) >= self.MAX_CONNS_PER_TYPE:
            return False
        if target_idx in self.input_conns:
            return False
        if self.total_conns() >= self.MAX_TOTAL_CONNS:
            return False
        self.input_conns.append(target_idx)
        self.recalc_render_radius()
        return True

    def add_control_conn(self, target_idx: int) -> bool:
        if target_idx == self.get_idx():
            return False
        if len(self.control_conns) >= self.MAX_CONNS_PER_TYPE:
            return False
        if target_idx in self.control_conns:
            return False
        if self.total_conns() >= self.MAX_TOTAL_CONNS:
            return False
        self.control_conns.append(target_idx)
        self.recalc_render_radius()
        return True

    def add_output_conn(self, target_idx: int) -> bool:
        if target_idx == self.get_idx():
            return False
        if len(self.output_conns) >= self.MAX_CONNS_PER_TYPE:
            return False
        if target_idx in self.output_conns:
            return False
        if self.total_conns() >= self.MAX_TOTAL_CONNS:
            return False
        self.output_conns.append(target_idx)
        self.recalc_render_radius()
        return True

    def remove_input_conn(self, target_idx: int) -> bool:
        if target_idx in self.input_conns:
            self.input_conns.remove(target_idx)
            self.recalc_render_radius()
            return True
        return False

    def remove_control_conn(self, target_idx: int) -> bool:
        if target_idx in self.control_conns:
            self.control_conns.remove(target_idx)
            self.recalc_render_radius()
            return True
        return False

    def remove_output_conn(self, target_idx: int) -> bool:
        if target_idx in self.output_conns:
            self.output_conns.remove(target_idx)
            self.recalc_render_radius()
            return True
        return False

    def has_conn_with(self, target_idx: int) -> bool:
        return (
            target_idx in self.input_conns or
            target_idx in self.control_conns or
            target_idx in self.output_conns
        )

    def replace_conn_index(self, old_idx: int, new_idx: int):
        for conn_list in [self.input_conns, self.control_conns, self.output_conns]:
            for i in range(len(conn_list)):
                if conn_list[i] == old_idx:
                    conn_list[i] = new_idx

    def total_conns(self) -> int:
        return len(self.input_conns) + len(self.control_conns) + len(self.output_conns)

    def recalc_render_radius(self):
        self.render_radius = min(9, self.total_conns())

    def is_input_full(self) -> bool:
        return len(self.input_conns) >= self.MAX_CONNS_PER_TYPE

    def is_control_full(self) -> bool:
        return len(self.control_conns) >= self.MAX_CONNS_PER_TYPE

    def is_output_full(self) -> bool:
        return len(self.output_conns) >= self.MAX_CONNS_PER_TYPE

    # ---- 不应期阶段 ----
    def is_in_full_refractory(self) -> bool:
        return self.REFRACTORY_FULL[0] <= self.refractory <= self.REFRACTORY_FULL[1]

    def is_in_medium_refractory(self) -> bool:
        return self.REFRACTORY_MEDIUM[0] <= self.refractory <= self.REFRACTORY_MEDIUM[1]

    def is_in_normal_period(self) -> bool:
        return self.REFRACTORY_NORMAL[0] <= self.refractory <= self.REFRACTORY_NORMAL[1]

    def can_send_signal(self, signal_strength: int) -> bool:
        if self.is_in_full_refractory():
            return False
        if self.is_in_medium_refractory() and signal_strength < 6:
            return False
        return True

    def trigger_signal_output(self):
        # 触发发射后进入不应期
        self.refractory = 3

    def update_refractory(self, recovery_amount: int = 1):
        self.refractory = min(9, self.refractory + recovery_amount)

    # ---- 位置与信号 ----
    def update_position(self, x: int, y: int):
        self.position = (x, y)

    def get_idx(self) -> int:
        return coord_to_idx(self.position[0], self.position[1])

    def set_input_val(self, val: int):
        self.input_val = max(0, min(9, val))

    def __repr__(self) -> str:
        return (f"Neuron(pos={self.position}, input={self.input_val}, "
                f"ref={self.refractory}, radius={self.render_radius}, "
                f"in={len(self.input_conns)}, ctrl={len(self.control_conns)}, "
                f"out={len(self.output_conns)})")

    def to_dict(self) -> dict:
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
        x, y = data['position']
        neuron = cls(x, y, data.get('input_val', 0), data.get('refractory', 9))
        neuron.input_conns = data.get('input_conns', []).copy()
        neuron.control_conns = data.get('control_conns', []).copy()
        neuron.output_conns = data.get('output_conns', []).copy()
        neuron.recalc_render_radius()
        return neuron


# =====================================================================
# 随机池
# =====================================================================

class RandomPool:
    """全局随机池，值范围仅 1~4。所有引擎共享同一实例。"""

    CONN_TYPE_MAP = {
        1: 'input',
        2: 'control',
        3: 'output',
    }

    def __init__(self):
        self._pool: List[int] = []
        self._pointer: int = 0

    @property
    def size(self) -> int:
        return len(self._pool)

    @property
    def is_empty(self) -> bool:
        return len(self._pool) == 0

    def add_values(self, values: List[int]):
        # 直接追加已是 1~4 的值
        self._pool.extend(values)

    def add_input_digits(self, digits: List[int]):
        # 将 0~9 的数字拆分转换为 1~4 的序列追加
        for d in digits:
            v = d + 1  # 1~10
            while v > 4:
                self._pool.append(4)
                v -= 4
            if v > 0:
                self._pool.append(v)

    def next(self) -> Optional[int]:
        if self.is_empty:
            return None
        value = self._pool[self._pointer % len(self._pool)]
        self._pointer = (self._pointer + 1) % len(self._pool)
        return value

    def next_direction(self) -> Optional[Tuple[int, int]]:
        value = self.next()
        if value is None:
            return None
        return DIRECTION_OFFSETS[value - 1]

    def next_conn_type(self) -> Optional[str]:
        value = self.next()
        if value is None:
            return None
        key = ((value - 1) % 3) + 1
        return self.CONN_TYPE_MAP[key]

    def peek(self) -> Optional[int]:
        if self.is_empty:
            return None
        return self._pool[self._pointer % len(self._pool)]

    def reset_pointer(self):
        self._pointer = 0

    def clear(self):
        self._pool.clear()
        self._pointer = 0

    def get_remaining_count(self) -> int:
        if self.is_empty:
            return 0
        return len(self._pool) - self._pointer

    def __repr__(self) -> str:
        return (f"RandomPool(size={len(self._pool)}, "
                f"pointer={self._pointer}, next={self.peek()})")


# =====================================================================
# 扩散场
# =====================================================================

class DiffusionField:
    _MAX_STRENGTH: int = 9

    def __init__(self):
        self._field: List[int] = [0] * TOTAL_CELLS

    def get(self, idx: int) -> int:
        if 0 <= idx < TOTAL_CELLS:
            return self._field[idx]
        return 0

    def set(self, idx: int, value: int):
        if 0 <= idx < TOTAL_CELLS:
            self._field[idx] = max(0, min(self._MAX_STRENGTH, value))

    def set_max(self, idx: int, value: int):
        if 0 <= idx < TOTAL_CELLS:
            clamped = max(0, min(self._MAX_STRENGTH, value))
            if clamped > self._field[idx]:
                self._field[idx] = clamped

    def clear(self):
        for i in range(TOTAL_CELLS):
            self._field[i] = 0

    def get_field(self) -> List[int]:
        return self._field.copy()

    def load_field(self, data: List[int]):
        if len(data) == TOTAL_CELLS:
            self._field = data.copy()