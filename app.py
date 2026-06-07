# -*- coding: utf-8 -*-
import numpy as np
import copy
import sys

# ===========================================================================
# 文件配置常量
# ===========================================================================
GRID_FILE_NAME = "Alice_McCord"
GRID_FILE_SUFFIX = ".exdc"
INPUT_FILE_NAME = "alice"
INPUT_FILE_SUFFIX = ".wtms"
DEBUG = False  # 关闭调试日志，只打印关键信息
PRINT_TIMEOUT_LOGS = False  # 关闭超时日志刷屏

# ===========================================================================
# 全局常量
# ===========================================================================
GRID_SIDE_LENGTH = 32
TOTAL_CELLS = 1024
MAX_BRIGHTNESS = 9
ACTIVE_BRIGHTNESS = 9
SEED_BRIGHTNESS = 4
MAX_PORTS_PER_TYPE = 9
API_PORT_COUNT = 32
CONTROL_SIGNAL_THRESHOLD = 1
BINARY_GROUP_BITS = 4
RANDOM_POOL_GROUPS = 7
CONNECTION_TIMEOUT_THRESHOLD = 5

# ===========================================================================
# Point类定义（与ax.py完全一致，保证序列化兼容）
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
# 工具函数
# ===========================================================================
def build_random_pool(binary_string_list: list) -> list:
    random_pool = []
    for i in range(len(binary_string_list)):
        current_binary_string = binary_string_list[i]
        random_pool.append(int(current_binary_string[0]) + int(current_binary_string[1]) + int(current_binary_string[2]) + int(current_binary_string[3]))
        random_pool.append(int(current_binary_string[4]) + int(current_binary_string[5]) + int(current_binary_string[6]) + int(current_binary_string[7]))
        random_pool.append(int(current_binary_string[8]) + int(current_binary_string[9]) + int(current_binary_string[10]) + int(current_binary_string[11]))
        random_pool.append(int(current_binary_string[12]) + int(current_binary_string[13]) + int(current_binary_string[14]) + int(current_binary_string[15]))
        random_pool.append(int(current_binary_string[16]) + int(current_binary_string[17]) + int(current_binary_string[18]) + int(current_binary_string[19]))
        random_pool.append(int(current_binary_string[20]) + int(current_binary_string[21]) + int(current_binary_string[22]) + int(current_binary_string[23]))
        random_pool.append(int(current_binary_string[24]) + int(current_binary_string[25]) + int(current_binary_string[26]) + int(current_binary_string[27]))
    return random_pool

def detect_active_points(grid: list, grid_layer: int) -> list:
    """检测所有活跃点（亮度>0的普通节点，排除API整行）"""
    active_points = []
    for i in range(len(grid)):
        if isinstance(grid[i], Point) and is_in_normal_region(i, grid_layer) and grid[i].brightness > 0:
            active_points.append((i, grid[i].brightness))
    return active_points

def detect_active_cells(grid: list, grid_layer: int) -> list:
    """检测所有亮度>0的单元格（Point对象 + 非Point数字），用于跨层传播"""
    active_cells = []
    for i in range(len(grid)):
        if not is_in_normal_region(i, grid_layer):
            continue
        if isinstance(grid[i], Point):
            if grid[i].brightness > 0:
                active_cells.append((i, grid[i].brightness))
        elif isinstance(grid[i], (int, float)) and grid[i] > 0:
            active_cells.append((i, int(grid[i])))
    return active_cells

def detect_all_points(grid: list) -> list:
    all_points = []
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            all_points.append((i, grid[i].brightness))
    return all_points

def update_connections_after_move(grid: list, grid_name: str,
                                   old_index: int, new_index: int) -> None:
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            point = grid[i]
            for port_list in [point.control_ports, point.input_ports, point.output_ports]:
                for connection in port_list:
                    if connection.get("source_point_index") == old_index:
                        connection["source_point_index"] = new_index
                    if connection.get("target_point_index") == old_index:
                        connection["target_point_index"] = new_index

def determine_movement_direction(grid: list, point_index: int, grid_layer: int) -> int:
    if not isinstance(grid[point_index], Point):
        return -1
    if not is_in_normal_region(point_index, grid_layer):
        return -1
        
    self_brightness = grid[point_index].brightness
    direction_offsets = [
        ("down", 32),
        ("right", 1),
        ("up", -32),
        ("left", -1),
    ]
    candidates = []
    
    for direction_name, offset in direction_offsets:
        target_index = point_index + offset
        if target_index < 0 or target_index >= TOTAL_CELLS:
            continue
        if direction_name == "left" and point_index % GRID_SIDE_LENGTH == 0:
            continue
        if direction_name == "right" and point_index % GRID_SIDE_LENGTH == GRID_SIDE_LENGTH - 1:
            continue
        if isinstance(grid[target_index], Point):
            continue
        neighbor_signal = grid[target_index]
        candidates.append((neighbor_signal, direction_name, target_index))
    
    if not candidates:
        return -1
        
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_signal = candidates[0][0]
    
    # 降低移动阈值，让节点更容易移动但不会乱跑
    if best_signal > self_brightness - 1:
        return candidates[0][2]
    return -1

def clear_non_point_brightness(grid: list, grid_layer: int | None = None) -> list:
    for i in range(TOTAL_CELLS):
        if grid_layer is not None and not is_in_normal_region(i, grid_layer):
            continue
        if not isinstance(grid[i], Point):
            grid[i] = 0
    return grid

def clear_all_connection_signals(grid: list) -> list:
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            point = grid[i]
            for port_list in [point.control_ports, point.input_ports, point.output_ports]:
                for connection in port_list:
                    connection["signal"] = 0
    return grid

def validate_grid_integrity(grid: list) -> bool:
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            point = grid[i]
            if point.center_index != i:
                print(f"[Error] 网格完整性验证失败: 索引 {i} 的节点 center_index={point.center_index} 不匹配")
                return False
            for port_list in [point.control_ports, point.input_ports, point.output_ports]:
                for connection in port_list:
                    src = connection.get("source_point_index", -1)
                    tgt = connection.get("target_point_index", -1)
                    if src != -1 and (src < 0 or src >= TOTAL_CELLS):
                        print(f"[Error] 网格完整性验证失败: 索引 {i} 的节点连接 source_point_index={src} 超出范围")
                        return False
                    if tgt < 0 or tgt >= TOTAL_CELLS:
                        print(f"[Error] 网格完整性验证失败: 索引 {i} 的节点连接 target_point_index={tgt} 超出范围")
                        return False
    return True

def guard_api_rows(grid_layer_1, grid_layer_5):
    """绝对保证 API 行每个单元格都是 Point 对象，is_api=True，亮度恒为 9"""
    for i in range(API_PORT_COUNT):
        if not isinstance(grid_layer_1[i], Point):
            grid_layer_1[i] = Point(center_index=i, brightness=ACTIVE_BRIGHTNESS, is_api=True, api_signal=0)
        else:
            grid_layer_1[i].is_api = True
            grid_layer_1[i].brightness = ACTIVE_BRIGHTNESS
    for i in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        if not isinstance(grid_layer_5[i], Point):
            grid_layer_5[i] = Point(center_index=i, brightness=ACTIVE_BRIGHTNESS, is_api=True, api_signal=0)
        else:
            grid_layer_5[i].is_api = True
            grid_layer_5[i].brightness = ACTIVE_BRIGHTNESS
    return grid_layer_1, grid_layer_5

def is_in_normal_region(index, grid_layer):
    """返回 True 表示该索引属于可移动/可连接/可渲染的普通区域"""
    row = index // GRID_SIDE_LENGTH
    if grid_layer == 1:
        return row != 0          # 跳过第一行（API输入行）
    elif grid_layer == 5:
        return row != 31         # 跳过最后一行（API输出行）
    else:
        return True

def diamond_render_single_point(grid: list, point_index: int,
                                 source_brightness: int, grid_layer: int) -> list:
    if not isinstance(grid[point_index], Point):
        return grid
    if not is_in_normal_region(point_index, grid_layer):
        return grid
        
    column_x = point_index % GRID_SIDE_LENGTH
    row_y = point_index // GRID_SIDE_LENGTH
    
    for delta_y in range(-source_brightness, source_brightness + 1):
        for delta_x in range(-source_brightness, source_brightness + 1):
            manhattan_distance = abs(delta_x) + abs(delta_y)
            if manhattan_distance >= source_brightness:
                continue
                
            neighbor_x = column_x + delta_x
            neighbor_y = row_y + delta_y
            
            if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < GRID_SIDE_LENGTH:
                target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                if not is_in_normal_region(target_flat_index, grid_layer):
                    continue
                computed_brightness = source_brightness - manhattan_distance
                # 只修改非Point单元格，遇到Point直接绕过不修改
                if not isinstance(grid[target_flat_index], Point):
                    if computed_brightness > grid[target_flat_index]:
                        grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return grid

def render_grid(grid: list, active_points: list, grid_layer: int) -> list:
    grid = clear_non_point_brightness(grid, grid_layer)
    
    for point_index, _ in active_points:
        if not isinstance(grid[point_index], Point):
            continue
        if not is_in_normal_region(point_index, grid_layer):
            continue
        source_brightness = grid[point_index].brightness
        grid = diamond_render_single_point(grid, point_index, source_brightness, grid_layer)
    return grid

def check_connection_exists(source_point: Point, target_index: int) -> bool:
    for conn in source_point.output_ports:
        if conn.get("target_point_index") == target_index:
            return True
    for conn in source_point.input_ports:
        if conn.get("source_point_index") == target_index:
            return True
    for conn in source_point.control_ports:
        if conn.get("source_point_index") == target_index:
            return True
    return False

def propagate_to_output_api(grid_layer_5):
    """将第五层第 31 行（倒数第二行，索引行30）的信号传递给第 32 行（API行）"""
    source_row = 30
    target_row = 31
    for col in range(GRID_SIDE_LENGTH):
        source_idx = source_row * GRID_SIDE_LENGTH + col
        target_idx = target_row * GRID_SIDE_LENGTH + col
        if isinstance(grid_layer_5[source_idx], Point):
            signal = grid_layer_5[source_idx].brightness
        else:
            signal = grid_layer_5[source_idx] if isinstance(grid_layer_5[source_idx], (int, float)) else 0
        grid_layer_5[target_idx] = Point(
            center_index=target_idx,
            brightness=ACTIVE_BRIGHTNESS,
            is_api=True,
            api_signal=signal,
            input_ports=[{
                "source_point_index": source_idx,
                "target_point_index": target_idx,
                "signal": signal,
                "port_type": "input",
                "last_signal_value": signal,
                "timeout_counter": 0
            }]
        )

def anneal_and_connect(grid: list, active_points: list,
                        random_pool: list, grid_name: str, grid_layer: int) -> list:
    if not random_pool:
        return grid
    pool_len = len(random_pool)
    connection_count = 0
    
    for point_index, source_brightness in active_points:
        if not isinstance(grid[point_index], Point):
            continue
        if not is_in_normal_region(point_index, grid_layer):
            continue
            
        column_x = point_index % GRID_SIDE_LENGTH
        row_y = point_index // GRID_SIDE_LENGTH
        block_modified_flag = False
        
        # 退火阶段
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                    
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                
                if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < GRID_SIDE_LENGTH:
                    target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                    if not is_in_normal_region(target_flat_index, grid_layer):
                        continue
                    computed_change = -(source_brightness - manhattan_distance)
                    # 只修改非Point单元格，遇到Point直接绕过
                    if isinstance(grid[target_flat_index], Point):
                        continue
                    new_brightness = grid[target_flat_index] + computed_change
                    if new_brightness < 0:
                        new_brightness = 0
                    if new_brightness != grid[target_flat_index]:
                        grid[target_flat_index] = new_brightness
                        block_modified_flag = True
        
        # 连接建立阶段（降低连接门槛，让神经元更容易连接）
        if not block_modified_flag:
            continue
        for direction_offset in [-32, 32, -1, 1]:
            random_pool_idx = point_index % pool_len
            # 降低随机池门槛，从1改成<=2
            if random_pool[random_pool_idx] > 2:
                continue
            target_index = point_index + direction_offset
            if not (0 <= target_index < TOTAL_CELLS):
                continue
            if not isinstance(grid[target_index], Point):
                continue
            # 检查重复连接
            if check_connection_exists(grid[point_index], target_index):
                continue
            # 检查源节点输出端口是否已满
            if len(grid[point_index].output_ports) >= MAX_PORTS_PER_TYPE:
                continue
            # 源节点是输出API节点则跳过
            if grid[point_index].center_index >= TOTAL_CELLS - API_PORT_COUNT:
                continue
            # 目标节点是输入API节点则跳过
            if grid[target_index].center_index < API_PORT_COUNT:
                continue
            # 计算port_type_accumulator
            port_type_accumulator = 0
            for offset_counter in range(3):
                idx = (point_index + offset_counter) % pool_len
                if random_pool[idx] < 4:
                    port_type_accumulator += 1
            # 根据port_type_accumulator决定连接类型
            if port_type_accumulator == 1:
                # 输出 -> 输入
                if len(grid[target_index].input_ports) >= MAX_PORTS_PER_TYPE:
                    continue
                source_connection = {
                    "source_point_index": point_index,
                    "target_point_index": target_index,
                    "signal": 0,
                    "port_type": "output",
                    "last_signal_value": 0,
                    "timeout_counter": 0
                }
                target_connection = {
                    "source_point_index": target_index,
                    "target_point_index": point_index,
                    "signal": 0,
                    "port_type": "input",
                    "last_signal_value": 0,
                    "timeout_counter": 0
                }
                grid[point_index].output_ports.append(source_connection)
                grid[target_index].input_ports.append(target_connection)
                connection_count += 1
            elif port_type_accumulator == 2:
                # 输出 -> 控制
                if len(grid[target_index].control_ports) >= MAX_PORTS_PER_TYPE:
                    continue
                source_connection = {
                    "source_point_index": point_index,
                    "target_point_index": target_index,
                    "signal": 0,
                    "port_type": "output",
                    "last_signal_value": 0,
                    "timeout_counter": 0
                }
                target_connection = {
                    "source_point_index": target_index,
                    "target_point_index": point_index,
                    "signal": 0,
                    "port_type": "control",
                    "last_signal_value": 0,
                    "timeout_counter": 0
                }
                grid[point_index].output_ports.append(source_connection)
                grid[target_index].control_ports.append(target_connection)
                connection_count += 1
            else:
                # 默认：输出 -> 控制
                if len(grid[target_index].control_ports) >= MAX_PORTS_PER_TYPE:
                    continue
                source_connection = {
                    "source_point_index": point_index,
                    "target_point_index": target_index,
                    "signal": 0,
                    "port_type": "output",
                    "last_signal_value": 0,
                    "timeout_counter": 0
                }
                target_connection = {
                    "source_point_index": target_index,
                    "target_point_index": point_index,
                    "signal": 0,
                    "port_type": "control",
                    "last_signal_value": 0,
                    "timeout_counter": 0
                }
                grid[point_index].output_ports.append(source_connection)
                grid[target_index].control_ports.append(target_connection)
                connection_count += 1
            # 检查源节点是否满端口
            if (len(grid[point_index].control_ports) == MAX_PORTS_PER_TYPE and
                len(grid[point_index].input_ports) == MAX_PORTS_PER_TYPE and
                len(grid[point_index].output_ports) == MAX_PORTS_PER_TYPE):
                if grid[point_index].is_api == False:
                    grid[point_index].brightness = ACTIVE_BRIGHTNESS
            # 检查目标节点是否满端口
            if (len(grid[target_index].control_ports) == MAX_PORTS_PER_TYPE and
                len(grid[target_index].input_ports) == MAX_PORTS_PER_TYPE and
                len(grid[target_index].output_ports) == MAX_PORTS_PER_TYPE):
                if grid[target_index].is_api == False:
                    grid[target_index].brightness = ACTIVE_BRIGHTNESS
    
    if connection_count > 0 and DEBUG:
        print(f"[Connect] {grid_name} 本轮建立 {connection_count} 个新连接")
    return grid

def preload_next_grid(source_grid: list, target_grid: list,
                       active_points: list, target_grid_layer: int) -> list:
    target_grid = clear_non_point_brightness(target_grid, target_grid_layer)
    
    for point_index, _ in active_points:
        if not isinstance(source_grid[point_index], Point):
            # 支持非Point的活跃单元格（来自 detect_active_cells）
            source_brightness = source_grid[point_index] if isinstance(source_grid[point_index], (int, float)) else 0
            if source_brightness <= 0:
                continue
            column_x = point_index % GRID_SIDE_LENGTH
            row_y = point_index // GRID_SIDE_LENGTH
        else:
            column_x = point_index % GRID_SIDE_LENGTH
            row_y = point_index // GRID_SIDE_LENGTH
            source_brightness = source_grid[point_index].brightness
        
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                    
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                
                if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < GRID_SIDE_LENGTH:
                    target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                    if not is_in_normal_region(target_flat_index, target_grid_layer):
                        continue
                    computed_brightness = source_brightness - manhattan_distance
                    # 只修改非Point单元格，遇到Point直接绕过
                    if not isinstance(target_grid[target_flat_index], Point):
                        if computed_brightness > target_grid[target_flat_index]:
                            target_grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return target_grid

def signal_preload_next_grid(source_grid: list, target_grid: list,
                              active_cells: list, target_grid_layer: int) -> list:
    """跨层信号注入：将源层活跃信号直接注入到目标层同位置单元格。
    使用 1:1 位置映射（无距离衰减），确保信号强度不随层数递减。"""
    for cell_index, _ in active_cells:
        if not is_in_normal_region(cell_index, target_grid_layer):
            continue
        if isinstance(source_grid[cell_index], Point):
            source_brightness = source_grid[cell_index].brightness
        elif isinstance(source_grid[cell_index], (int, float)):
            source_brightness = int(source_grid[cell_index])
        else:
            continue
        if source_brightness <= 0:
            continue

        if isinstance(target_grid[cell_index], Point):
            if source_brightness > target_grid[cell_index].brightness:
                target_grid[cell_index].brightness = min(source_brightness, MAX_BRIGHTNESS)
        else:
            if source_brightness > target_grid[cell_index]:
                target_grid[cell_index] = min(source_brightness, MAX_BRIGHTNESS)
    return target_grid

def inject_api_signal_vertically(grid_layer_1, grid_layer_2, grid_layer_3,
                                  grid_layer_4, grid_layer_5):
    """将 API 输入信号从 L1 第 0 行直接垂直注入到所有层的第 1 行，以及逐层传递到输出 API。
    这绕过了 Point 位置随机导致的跨层传播断层问题。"""
    # 从 L1 row 0 读取 API 信号
    api_signals = []
    for col in range(API_PORT_COUNT):
        idx = col  # row 0, col
        if isinstance(grid_layer_1[idx], Point) and grid_layer_1[idx].is_api:
            api_signals.append(grid_layer_1[idx].api_signal)
        else:
            api_signals.append(0)

    # 注入到 L1 row 1 的 Point 单元格
    for col in range(API_PORT_COUNT):
        target_idx = 1 * GRID_SIDE_LENGTH + col  # row 1
        if api_signals[col] > 0:
            if isinstance(grid_layer_1[target_idx], Point):
                if api_signals[col] > grid_layer_1[target_idx].brightness:
                    grid_layer_1[target_idx].brightness = api_signals[col]
            else:
                grid_layer_1[target_idx] = api_signals[col]

    # 注入到 L2 row 1（同列位置）
    for col in range(API_PORT_COUNT):
        target_idx = 1 * GRID_SIDE_LENGTH + col
        if api_signals[col] > 0:
            if isinstance(grid_layer_2[target_idx], Point):
                if api_signals[col] > grid_layer_2[target_idx].brightness:
                    grid_layer_2[target_idx].brightness = api_signals[col]
            else:
                grid_layer_2[target_idx] = api_signals[col]

    # 注入到 L3 row 1
    for col in range(API_PORT_COUNT):
        target_idx = 1 * GRID_SIDE_LENGTH + col
        if api_signals[col] > 0:
            if isinstance(grid_layer_3[target_idx], Point):
                if api_signals[col] > grid_layer_3[target_idx].brightness:
                    grid_layer_3[target_idx].brightness = api_signals[col]
            else:
                grid_layer_3[target_idx] = api_signals[col]

    # 注入到 L4 row 1
    for col in range(API_PORT_COUNT):
        target_idx = 1 * GRID_SIDE_LENGTH + col
        if api_signals[col] > 0:
            if isinstance(grid_layer_4[target_idx], Point):
                if api_signals[col] > grid_layer_4[target_idx].brightness:
                    grid_layer_4[target_idx].brightness = api_signals[col]
            else:
                grid_layer_4[target_idx] = api_signals[col]

    # 注入到 L5 row 30（输出 API 的前一行）
    for col in range(API_PORT_COUNT):
        target_idx = 30 * GRID_SIDE_LENGTH + col
        if api_signals[col] > 0:
            if isinstance(grid_layer_5[target_idx], Point):
                if api_signals[col] > grid_layer_5[target_idx].brightness:
                    grid_layer_5[target_idx].brightness = api_signals[col]
            else:
                grid_layer_5[target_idx] = api_signals[col]

    return grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5

def execute_movement_phase(grid_layer_1: list, grid_layer_2: list,
                            grid_layer_3: list, grid_layer_4: list,
                            grid_layer_5: list) -> tuple:
    grids = [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]
    grid_names = ["grid_layer_1", "grid_layer_2", "grid_layer_3", "grid_layer_4", "grid_layer_5"]
    grid_layers = [1, 2, 3, 4, 5]
    total_moved = 0
    
    for grid_index in range(len(grids)):
        grid = grids[grid_index]
        grid_name = grid_names[grid_index]
        current_layer = grid_layers[grid_index]
        all_points = detect_all_points(grid)
        # 构建移动映射
        move_map = {}
        for original_index, _ in all_points:
            if not isinstance(grid[original_index], Point):
                continue
            if not is_in_normal_region(original_index, current_layer):
                continue
            new_index = determine_movement_direction(grid, original_index, current_layer)
            if new_index != -1:
                move_map[original_index] = new_index
        # 统计每个目标被选中的次数
        target_count = {}
        for old_idx, new_idx in move_map.items():
            target_count[new_idx] = target_count.get(new_idx, 0) + 1
        # 过滤出只被一个节点选中的目标
        valid_move_map = {}
        for old_idx, new_idx in move_map.items():
            if target_count[new_idx] == 1:
                valid_move_map[old_idx] = new_idx
        # 执行有效移动
        moved_to_indices = set()
        for old_idx, new_idx in valid_move_map.items():
            if new_idx in moved_to_indices:
                continue
            # 禁止移动到 API 行
            if current_layer == 1 and new_idx // GRID_SIDE_LENGTH == 0:
                continue
            if current_layer == 5 and new_idx // GRID_SIDE_LENGTH == 31:
                continue
            if isinstance(grid[new_idx], Point):
                continue
            grid[new_idx] = copy.deepcopy(grid[old_idx])
            grid[new_idx].center_index = new_idx
            grid[old_idx] = 0
            update_connections_after_move(grid, grid_name, old_idx, new_idx)
            moved_to_indices.add(new_idx)
            total_moved += 1
    
    if total_moved > 0 and DEBUG:
        print(f"[Move] 本轮共移动 {total_moved} 个节点")
    return grids[0], grids[1], grids[2], grids[3], grids[4]

def transistor_style_signal_propagation(grid_layer_1: list,
                                         grid_layer_2: list,
                                         grid_layer_3: list,
                                         grid_layer_4: list,
                                         grid_layer_5: list) -> tuple:
    all_grids = [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]
    grid_layers = [1, 2, 3, 4, 5]
    
    for grid_idx in range(len(all_grids)):
        grid = all_grids[grid_idx]
        current_layer = grid_layers[grid_idx]
        # 第一阶段：计算所有节点输出信号
        output_signals = {}
        for i in range(len(grid)):
            if not isinstance(grid[i], Point):
                continue
            point = grid[i]
            # API 节点不产生输出信号
            if point.is_api:
                output_signals[i] = 0
                continue
            input_signals = []
            for input_connection in point.input_ports:
                signal_value = input_connection.get("signal", 0)
                if signal_value > 0:
                    input_signals.append(signal_value)
            # 第一层：从 API 行直接注入信号给第二行（row=1）的节点
            if current_layer == 1:
                row = i // GRID_SIDE_LENGTH
                if row == 1:
                    col = i % GRID_SIDE_LENGTH
                    api_idx = col
                    if isinstance(grid[api_idx], Point) and grid[api_idx].is_api:
                        api_sig = grid[api_idx].api_signal
                        if api_sig > 0:
                            input_signals.append(api_sig)
                            if DEBUG:
                                print(f"[Inject] L1 row=1 col={col} injected api_signal={api_sig}")
            control_triggered = False
            for control_connection in point.control_ports:
                if control_connection.get("signal", 0) > CONTROL_SIGNAL_THRESHOLD:
                    control_triggered = True
                    break
            if control_triggered:
                output_signals[i] = 0
            else:
                output_signals[i] = max(input_signals) if input_signals else 0
        # 第二阶段：传播输出信号
        for i in range(len(grid)):
            if not isinstance(grid[i], Point):
                continue
            if i not in output_signals:
                continue
            output_signal = output_signals[i]
            point = grid[i]
            # API 节点不参与传播阶段
            if point.is_api:
                continue
            if is_in_normal_region(i, current_layer):
                point.brightness = min(max(point.brightness, output_signal), MAX_BRIGHTNESS)
            for output_connection in point.output_ports:
                output_connection["signal"] = output_signal
                target_index = output_connection.get("target_point_index", -1)
                if 0 <= target_index < TOTAL_CELLS and isinstance(grid[target_index], Point):
                    target_point = grid[target_index]
                    for receiving_connection in target_point.input_ports:
                        if receiving_connection.get("target_point_index") == i:
                            receiving_connection["signal"] = output_signal
                    for receiving_connection in target_point.control_ports:
                        if receiving_connection.get("target_point_index") == i:
                            receiving_connection["signal"] = output_signal
    return grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5

def display_grid(grid: list, grid_name: str) -> None:
    print(f"====== {grid_name} ======")
    for i in range(0, TOTAL_CELLS, GRID_SIDE_LENGTH):
        row = []
        for j in range(i, i + GRID_SIDE_LENGTH):
            if isinstance(grid[j], Point):
                row.append(str(grid[j].brightness))
            else:
                row.append(str(grid[j]))
        print(' '.join(row))
    print()

# [DEPRECATED] 此函数将 API 亮度设为 0，与 guard_api_rows（亮度=9）冲突。
# 主循环中已不再调用，请使用 guard_api_rows 代替。
def initialize_api_ports(grid_layer_1: list, grid_layer_5: list) -> tuple:
    # 强制初始化API端口，确保永远存在
    for port_index in range(API_PORT_COUNT):
        grid_layer_1[port_index] = Point(
            center_index=port_index, 
            brightness=0, 
            is_api=True
        )
    for port_index in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        grid_layer_5[port_index] = Point(
            center_index=port_index, 
            brightness=0, 
            is_api=True
        )
    print("✅ API端口初始化完成")
    return grid_layer_1, grid_layer_5

def set_api_input(grid_layer_1: list, binary_string: str) -> bool:
    if len(binary_string) < API_PORT_COUNT:
        binary_string = binary_string.ljust(API_PORT_COUNT, '0')
    elif len(binary_string) > API_PORT_COUNT:
        binary_string = binary_string[:API_PORT_COUNT]
    for port_index in range(API_PORT_COUNT):
        character = binary_string[port_index]
        if character == '1':
            signal_value = ACTIVE_BRIGHTNESS
        elif character == '0':
            signal_value = 0
        else:
            print(f"[Error] 无效的二进制字符: {character}")
            return False
        grid_layer_1[port_index] = Point(
            center_index=port_index,
            brightness=ACTIVE_BRIGHTNESS,
            api_signal=signal_value,
            input_ports=[{
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value,
                "port_type": "input",
                "last_signal_value": signal_value,
                "timeout_counter": 0
            }],
            is_api=True
        )
    if DEBUG:
        print(f"[Debug] API 输入已设置: {binary_string}")
    return True

def get_api_output(grid_layer_5: list) -> tuple:
    """同时返回二进制信号和UTF-8字符"""
    binary_output = ""
    for port_index in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        # 确保API节点存在
        if not isinstance(grid_layer_5[port_index], Point) or not grid_layer_5[port_index].is_api:
            grid_layer_5[port_index] = Point(center_index=port_index, brightness=ACTIVE_BRIGHTNESS, is_api=True, api_signal=0)
        if grid_layer_5[port_index].api_signal >= 5:
            binary_output += "1"
        else:
            binary_output += "0"
    try:
        byte_list = []
        for byte_index in range(0, API_PORT_COUNT, 8):
            byte_string = binary_output[byte_index:byte_index + 8]
            byte_value = int(byte_string, 2)
            byte_list.append(byte_value)
        byte_data = bytes(byte_list)
        utf8_character = byte_data.decode("utf-8")
        return binary_output, utf8_character
    except (ValueError, UnicodeDecodeError):
        return binary_output, None

def load_full_grid_from_file(
    filename: str = GRID_FILE_NAME,
    suffix: str = GRID_FILE_SUFFIX
) -> tuple:
    full_filename = f"{filename}{suffix}"
    try:
        full_grid = np.load(full_filename, allow_pickle=True)
    except FileNotFoundError:
        print(f"[Error] 网格文件 {full_filename} 不存在")
        exit()
    if full_grid.shape[0] != 5 or full_grid.shape[1] != TOTAL_CELLS:
        print(f"[Error] 网格结构不正确: shape={full_grid.shape}, 期望 (5, {TOTAL_CELLS})")
        exit()
    grid_layer_1 = full_grid[0].tolist()
    grid_layer_2 = full_grid[1].tolist()
    grid_layer_3 = full_grid[2].tolist()
    grid_layer_4 = full_grid[3].tolist()
    grid_layer_5 = full_grid[4].tolist()
    
    # 强制转换所有Point对象为当前文件的Point类，解决序列化兼容问题
    for layer in [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]:
        for i in range(len(layer)):
            cell = layer[i]
            if hasattr(cell, 'center_index') and hasattr(cell, 'brightness'):
                new_point = Point(
                    center_index=cell.center_index,
                    brightness=cell.brightness,
                    control_ports=getattr(cell, 'control_ports', []),
                    input_ports=getattr(cell, 'input_ports', []),
                    output_ports=getattr(cell, 'output_ports', []),
                    is_api=getattr(cell, 'is_api', False),
                    api_signal=getattr(cell, 'api_signal', 0)
                )
                layer[i] = new_point
    
    print(f"✅ 网格加载完成：{full_filename}")
    return grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5

def read_input_from_text_file(
    filename: str = INPUT_FILE_NAME,
    suffix: str = INPUT_FILE_SUFFIX
) -> list:
    full_filename = f"{filename}{suffix}"
    input_lines = []
    try:
        with open(full_filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    content = line[2:].strip()
                    if content:
                        input_lines.append(content)
        print(f"✅ 输入文件加载完成：{full_filename}，共{len(input_lines)}条输入")
        return input_lines
    except FileNotFoundError:
        print(f"[Error] 输入文件 {full_filename} 不存在")
        return []

def check_connection_timeouts(grid_layer_1: list, grid_layer_2: list,
                               grid_layer_3: list, grid_layer_4: list,
                               grid_layer_5: list) -> tuple:
    all_grids = [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]
    grid_names = ["grid_layer_1", "grid_layer_2", "grid_layer_3", "grid_layer_4", "grid_layer_5"]
    total_deleted = 0
    
    for grid_idx in range(len(all_grids)):
        grid = all_grids[grid_idx]
        grid_name = grid_names[grid_idx]
        connections_to_delete = []
        for i in range(len(grid)):
            if not isinstance(grid[i], Point):
                continue
            point = grid[i]
            for port_list in [point.control_ports, point.input_ports, point.output_ports]:
                for connection in port_list:
                    # API永久输入连接跳过
                    if connection.get("source_point_index") == -1:
                        continue
                    if connection.get("signal", 0) == 0:
                        connection["timeout_counter"] = connection.get("timeout_counter", 0) + 1
                    else:
                        connection["timeout_counter"] = 0
                        connection["last_signal_value"] = connection.get("signal", 0)
                    if connection.get("timeout_counter", 0) >= CONNECTION_TIMEOUT_THRESHOLD:
                        connections_to_delete.append(connection)
        for connection in connections_to_delete:
            source_index = connection.get("source_point_index")
            target_index = connection.get("target_point_index")
            port_type = connection.get("port_type", "")
            # 从源节点output_ports删除
            if 0 <= source_index < TOTAL_CELLS and isinstance(grid[source_index], Point):
                source_point = grid[source_index]
                source_point.output_ports = [
                    conn for conn in source_point.output_ports
                    if conn.get("target_point_index") != target_index
                ]
            # 从目标节点对应端口删除反向连接
            if 0 <= target_index < TOTAL_CELLS and isinstance(grid[target_index], Point):
                target_point = grid[target_index]
                if port_type == "input":
                    target_point.input_ports = [
                        conn for conn in target_point.input_ports
                        if conn.get("source_point_index") != source_index
                    ]
                elif port_type == "control":
                    target_point.control_ports = [
                        conn for conn in target_point.control_ports
                        if conn.get("source_point_index") != source_index
                    ]
            total_deleted += 1
    
    if total_deleted > 0 and PRINT_TIMEOUT_LOGS:
        print(f"[Timeout] 本轮共删除 {total_deleted} 个超时连接")
    return grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5

# ===========================================================================
# 主程序
# ===========================================================================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    # 1. 加载网格
    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = load_full_grid_from_file()
    # 2. 强制初始化API端口（确保永远存在）
    grid_layer_1, grid_layer_5 = initialize_api_ports(grid_layer_1, grid_layer_5)
    # 3. 读取输入
    input_list = read_input_from_text_file()
    if not input_list:
        print("❌ 没有可处理的输入，程序退出")
        exit()
    # 4. 主循环
    current_input_index = 0
    total_inputs = len(input_list)
    while current_input_index < total_inputs:
        user_input = input_list[current_input_index]
        print(f"\n{'='*60}")
        print(f"处理第 {current_input_index+1}/{total_inputs} 条输入：{user_input}")
        print(f"{'='*60}\n")
        try:
            # 阶段1: 回合初始化
            grid_layer_1 = clear_non_point_brightness(grid_layer_1, 1)
            grid_layer_2 = clear_non_point_brightness(grid_layer_2, 2)
            grid_layer_3 = clear_non_point_brightness(grid_layer_3, 3)
            grid_layer_4 = clear_non_point_brightness(grid_layer_4, 4)
            grid_layer_5 = clear_non_point_brightness(grid_layer_5, 5)
            grid_layer_1 = clear_all_connection_signals(grid_layer_1)
            grid_layer_2 = clear_all_connection_signals(grid_layer_2)
            grid_layer_3 = clear_all_connection_signals(grid_layer_3)
            grid_layer_4 = clear_all_connection_signals(grid_layer_4)
            grid_layer_5 = clear_all_connection_signals(grid_layer_5)
            # 重置临时变量
            active_points_grid_layer_1 = []
            active_points_grid_layer_2 = []
            active_points_grid_layer_3 = []
            active_points_grid_layer_4 = []
            active_points_grid_layer_5 = []
            binary_string_list = []
            random_pool = []
            # 验证网格完整性
            for grid, name in [(grid_layer_1, "grid_layer_1"), (grid_layer_2, "grid_layer_2"), (grid_layer_3, "grid_layer_3"), (grid_layer_4, "grid_layer_4"), (grid_layer_5, "grid_layer_5")]:
                if not validate_grid_integrity(grid):
                    print(f"[Error] 网格完整性验证失败: {name}")
                    exit()
            # 阶段2: 输入处理
            input_character_list = list(user_input)
            padded_binary_string_list = []
            for character in input_character_list:
                unicode_encoded_bytes = character.encode("utf-8")
                binary_string = ''.join(f'{byte:08b}' for byte in unicode_encoded_bytes)
                padded_binary_string = binary_string.ljust(GRID_SIDE_LENGTH, '0')[:GRID_SIDE_LENGTH]
                padded_binary_string_list.append(padded_binary_string)
                binary_string_list.append(padded_binary_string)
            random_pool = build_random_pool(binary_string_list)
            api_input_string = padded_binary_string_list[0]
            set_api_input(grid_layer_1, api_input_string)
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 阶段3: 活跃点检测
            active_points_grid_layer_1 = detect_active_points(grid_layer_1, 1)
            active_points_grid_layer_2 = detect_active_points(grid_layer_2, 2)
            active_points_grid_layer_3 = detect_active_points(grid_layer_3, 3)
            active_points_grid_layer_4 = detect_active_points(grid_layer_4, 4)
            active_points_grid_layer_5 = detect_active_points(grid_layer_5, 5)
            print(f"[Status] 活跃点数量 - L1:{len(active_points_grid_layer_1)}, L2:{len(active_points_grid_layer_2)}, L3:{len(active_points_grid_layer_3)}, L4:{len(active_points_grid_layer_4)}, L5:{len(active_points_grid_layer_5)}")
            # 阶段4: 初始渲染
            grid_layer_1 = render_grid(grid_layer_1, active_points_grid_layer_1, 1)
            grid_layer_2 = render_grid(grid_layer_2, active_points_grid_layer_2, 2)
            grid_layer_3 = render_grid(grid_layer_3, active_points_grid_layer_3, 3)
            grid_layer_4 = render_grid(grid_layer_4, active_points_grid_layer_4, 4)
            grid_layer_5 = render_grid(grid_layer_5, active_points_grid_layer_5, 5)
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 阶段5: 退火与连接
            grid_layer_1 = anneal_and_connect(grid_layer_1, active_points_grid_layer_1, random_pool, "grid_layer_1", 1)
            grid_layer_2 = anneal_and_connect(grid_layer_2, active_points_grid_layer_2, random_pool, "grid_layer_2", 2)
            grid_layer_3 = anneal_and_connect(grid_layer_3, active_points_grid_layer_3, random_pool, "grid_layer_3", 3)
            grid_layer_4 = anneal_and_connect(grid_layer_4, active_points_grid_layer_4, random_pool, "grid_layer_4", 4)
            grid_layer_5 = anneal_and_connect(grid_layer_5, active_points_grid_layer_5, random_pool, "grid_layer_5", 5)
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 阶段6: 节点移动
            grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = execute_movement_phase(
                grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
            )
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 阶段7: 移动后重渲染
            active_points_grid_layer_1 = detect_active_points(grid_layer_1, 1)
            active_points_grid_layer_2 = detect_active_points(grid_layer_2, 2)
            active_points_grid_layer_3 = detect_active_points(grid_layer_3, 3)
            active_points_grid_layer_4 = detect_active_points(grid_layer_4, 4)
            active_points_grid_layer_5 = detect_active_points(grid_layer_5, 5)
            grid_layer_1 = render_grid(grid_layer_1, active_points_grid_layer_1, 1)
            grid_layer_2 = render_grid(grid_layer_2, active_points_grid_layer_2, 2)
            grid_layer_3 = render_grid(grid_layer_3, active_points_grid_layer_3, 3)
            grid_layer_4 = render_grid(grid_layer_4, active_points_grid_layer_4, 4)
            grid_layer_5 = render_grid(grid_layer_5, active_points_grid_layer_5, 5)
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 阶段8: 跨层预加载
            grid_layer_2 = preload_next_grid(grid_layer_1, grid_layer_2, active_points_grid_layer_1, 2)
            grid_layer_3 = preload_next_grid(grid_layer_2, grid_layer_3, active_points_grid_layer_2, 3)
            grid_layer_4 = preload_next_grid(grid_layer_3, grid_layer_4, active_points_grid_layer_3, 4)
            grid_layer_5 = preload_next_grid(grid_layer_4, grid_layer_5, active_points_grid_layer_4, 5)
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 阶段9: 信号传播（首轮：注入API信号并传播）
            grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = transistor_style_signal_propagation(
                grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
            )
            # 垂直注入 API 信号到所有层，绕过 Point 位置随机导致的跨层传播断层
            grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = inject_api_signal_vertically(
                grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
            )
            propagate_to_output_api(grid_layer_5)
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 多轮跨层信号注入：逐层顺序传递 L1→L2→L3→L4→L5
            # 使用 signal_preload_next_grid 直接注入到 Point 单元格的亮度
            for _ in range(4):
                # 顺序检测+注入：每层更新后立即检测，确保信号逐层传递
                ac1 = detect_active_cells(grid_layer_1, 1)
                grid_layer_2 = signal_preload_next_grid(grid_layer_1, grid_layer_2, ac1, 2)
                ac2 = detect_active_cells(grid_layer_2, 2)
                grid_layer_3 = signal_preload_next_grid(grid_layer_2, grid_layer_3, ac2, 3)
                ac3 = detect_active_cells(grid_layer_3, 3)
                grid_layer_4 = signal_preload_next_grid(grid_layer_3, grid_layer_4, ac3, 4)
                ac4 = detect_active_cells(grid_layer_4, 4)
                grid_layer_5 = signal_preload_next_grid(grid_layer_4, grid_layer_5, ac4, 5)
                grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = transistor_style_signal_propagation(
                    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
                )
                propagate_to_output_api(grid_layer_5)
                grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            # 阶段10: 连接超时检查与删除
            grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = check_connection_timeouts(
                grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
            )
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            grid_layer_1 = clear_all_connection_signals(grid_layer_1)
            grid_layer_2 = clear_all_connection_signals(grid_layer_2)
            grid_layer_3 = clear_all_connection_signals(grid_layer_3)
            grid_layer_4 = clear_all_connection_signals(grid_layer_4)
            grid_layer_5 = clear_all_connection_signals(grid_layer_5)
            # 阶段11: 显示网格（只在最后集中打印）
            display_grid(grid_layer_1, "Grid Layer 1")
            display_grid(grid_layer_2, "Grid Layer 2")
            display_grid(grid_layer_3, "Grid Layer 3")
            display_grid(grid_layer_4, "Grid Layer 4")
            display_grid(grid_layer_5, "Grid Layer 5")
            # 阶段12: 输出收集
            binary_output, utf8_output = get_api_output(grid_layer_5)
            print(f"\n{'='*60}")
            print(f"[API Output] 二进制信号: {binary_output}")
            print(f"[API Output] UTF-8 字符: {utf8_output if utf8_output is not None else '解码失败'}")
            print(f"{'='*60}")
            # 阶段13: 回合清理
            grid_layer_1 = clear_non_point_brightness(grid_layer_1, 1)
            grid_layer_2 = clear_non_point_brightness(grid_layer_2, 2)
            grid_layer_3 = clear_non_point_brightness(grid_layer_3, 3)
            grid_layer_4 = clear_non_point_brightness(grid_layer_4, 4)
            grid_layer_5 = clear_non_point_brightness(grid_layer_5, 5)
            grid_layer_1 = clear_all_connection_signals(grid_layer_1)
            grid_layer_2 = clear_all_connection_signals(grid_layer_2)
            grid_layer_3 = clear_all_connection_signals(grid_layer_3)
            grid_layer_4 = clear_all_connection_signals(grid_layer_4)
            grid_layer_5 = clear_all_connection_signals(grid_layer_5)
            grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
            current_input_index += 1
        except Exception as e:
            print(f"[Error] 处理第 {current_input_index+1} 条输入时发生异常: {e}")
            import traceback
            traceback.print_exc()
            current_input_index += 1
    print("\n✅ 所有输入处理完成！")