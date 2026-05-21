# -*- coding: utf-8 -*-
#!C:/Users/Administrator/Desktop/Alice McCord/app.py python3
import numpy as np

# ===========================================================================
# 新增：文件配置（这里改文件名和后缀）
# ===========================================================================
GRID_FILE_NAME = "Alice_McCord"  # 网格文件名（不含后缀）
GRID_FILE_SUFFIX = ".exdc"         # 和生成器的后缀一致
INPUT_FILE_NAME = "Alice"      # 输入文本文件名
INPUT_FILE_SUFFIX = ".wtms"         # 输入文件后缀（本质是txt）

# ===========================================================================
# 原全局常量（完全保留）
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

# ===========================================================================
# 原Point类（完全保留）
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
# 原工具函数（完全保留，一字未改）
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

def detect_active_points(grid: list) -> list:
    active_points = []
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            if grid[i].brightness == ACTIVE_BRIGHTNESS:
                active_points.append((i, grid[i].brightness))
    return active_points

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

def determine_movement_direction(grid: list, point_index: int) -> int:
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
    if best_signal > self_brightness:
        return candidates[0][2]
    return -1

def clear_non_point_brightness(grid: list) -> list:
    for i in range(len(grid)):
        if not isinstance(grid[i], Point):
            grid[i] = 0
    return grid

def diamond_render_single_point(grid: list, point_index: int,
                                 source_brightness: int) -> list:
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
                computed_brightness = source_brightness - manhattan_distance
                if isinstance(grid[target_flat_index], Point):
                    if computed_brightness > grid[target_flat_index].brightness:
                        grid[target_flat_index].brightness = min(computed_brightness, MAX_BRIGHTNESS)
                else:
                    if computed_brightness > grid[target_flat_index]:
                        grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return grid

def render_grid(grid: list, active_points: list) -> list:
    for point_index, _ in active_points:
        source_brightness = grid[point_index].brightness
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
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid[target_flat_index], Point):
                        if computed_brightness > grid[target_flat_index].brightness:
                            grid[target_flat_index].brightness = min(computed_brightness, MAX_BRIGHTNESS)
                    else:
                        if computed_brightness > grid[target_flat_index]:
                            grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return grid

def anneal_and_connect(grid: list, active_points: list,
                        random_pool: list, grid_name: str) -> list:
    for point_index, source_brightness in active_points:
        column_x = point_index % GRID_SIDE_LENGTH
        row_y = point_index // GRID_SIDE_LENGTH
        block_modified_flag = False
        print(f"[Anneal] grid={grid_name}, index={point_index}, brightness={source_brightness}")
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < GRID_SIDE_LENGTH:
                    target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                    computed_change = -(source_brightness - manhattan_distance)
                    changed = False
                    if isinstance(grid[target_flat_index], Point):
                        new_brightness = grid[target_flat_index].brightness + computed_change
                        if new_brightness < 0:
                            new_brightness = 0
                        if new_brightness != grid[target_flat_index].brightness:
                            grid[target_flat_index].brightness = new_brightness
                            changed = True
                    else:
                        new_brightness = grid[target_flat_index] + computed_change
                        if new_brightness < 0:
                            new_brightness = 0
                        if new_brightness != grid[target_flat_index]:
                            grid[target_flat_index] = new_brightness
                            changed = True
                    if changed:
                        block_modified_flag = True
        if block_modified_flag:
            for direction_offset in [32, -32, -1, 1]:
                if point_index < len(random_pool) and random_pool[point_index] == 1:
                    target_index = point_index + direction_offset
                    if 0 <= target_index < TOTAL_CELLS:
                        if isinstance(grid[target_index], Point):
                            if grid[target_index].brightness < MAX_BRIGHTNESS:
                                port_type_accumulator = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_type_accumulator += 1
                                connection_established = False
                                if port_type_accumulator == 1:
                                    if len(grid[target_index].input_ports) < MAX_PORTS_PER_TYPE and len(grid[point_index].output_ports) < MAX_PORTS_PER_TYPE:
                                        source_connection = {
                                            "source_point_index": point_index,
                                            "target_point_index": target_index,
                                            "signal": 0,
                                            "port_type": "output"
                                        }
                                        target_connection = {
                                            "source_point_index": target_index,
                                            "target_point_index": point_index,
                                            "signal": 0,
                                            "port_type": "input"
                                        }
                                        grid[point_index].output_ports.append(source_connection)
                                        grid[target_index].input_ports.append(target_connection)
                                        connection_established = True
                                        print(f"[Connect] grid={grid_name}, type=signal(output->input), source={point_index}, target={target_index}")
                                elif port_type_accumulator == 2:
                                    if len(grid[target_index].control_ports) < MAX_PORTS_PER_TYPE and len(grid[point_index].output_ports) < MAX_PORTS_PER_TYPE:
                                        source_connection = {
                                            "source_point_index": point_index,
                                            "target_point_index": target_index,
                                            "signal": 0,
                                            "port_type": "output"
                                        }
                                        target_connection = {
                                            "source_point_index": target_index,
                                            "target_point_index": point_index,
                                            "signal": 0,
                                            "port_type": "control"
                                        }
                                        grid[point_index].output_ports.append(source_connection)
                                        grid[target_index].control_ports.append(target_connection)
                                        connection_established = True
                                        print(f"[Connect] grid={grid_name}, type=control(output->control), source={point_index}, target={target_index}")
                                else:
                                    if len(grid[target_index].control_ports) < MAX_PORTS_PER_TYPE and len(grid[point_index].output_ports) < MAX_PORTS_PER_TYPE:
                                        source_connection = {
                                            "source_point_index": point_index,
                                            "target_point_index": target_index,
                                            "signal": 0,
                                            "port_type": "output"
                                        }
                                        target_connection = {
                                            "source_point_index": target_index,
                                            "target_point_index": point_index,
                                            "signal": 0,
                                            "port_type": "control"
                                        }
                                        grid[point_index].output_ports.append(source_connection)
                                        grid[target_index].control_ports.append(target_connection)
                                        connection_established = True
                                        print(f"[Connect] grid={grid_name}, type=control(default), source={point_index}, target={target_index}")
                                if connection_established:
                                    if (len(grid[point_index].control_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[point_index].input_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[point_index].output_ports) == MAX_PORTS_PER_TYPE):
                                        grid[point_index].brightness = ACTIVE_BRIGHTNESS
                                    if (len(grid[target_index].control_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[target_index].input_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[target_index].output_ports) == MAX_PORTS_PER_TYPE):
                                        grid[target_index].brightness = ACTIVE_BRIGHTNESS
                                    if grid[point_index].brightness > 0:
                                        grid = diamond_render_single_point(grid, point_index, grid[point_index].brightness)
                                        print(f"[Re-render] grid={grid_name}, index={point_index}")
    return grid

def preload_next_grid(source_grid: list, target_grid: list,
                       active_points: list) -> list:
    for point_index, _ in active_points:
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
                if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < 3:
                    target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(target_grid[target_flat_index], Point):
                        if computed_brightness > target_grid[target_flat_index].brightness:
                            target_grid[target_flat_index].brightness = min(computed_brightness, MAX_BRIGHTNESS)
                    else:
                        if computed_brightness > target_grid[target_flat_index]:
                            target_grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return target_grid

def execute_movement_phase(grid_layer_1: list, grid_layer_2: list,
                            grid_layer_3: list, grid_layer_4: list,
                            grid_layer_5: list) -> tuple:
    grids = [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]
    grid_names = ["grid_layer_1", "grid_layer_2", "grid_layer_3", "grid_layer_4", "grid_layer_5"]
    for grid_index in range(len(grids)):
        grid = grids[grid_index]
        grid_name = grid_names[grid_index]
        all_points = detect_all_points(grid)
        moved_to_indices = set()
        for original_index, _ in all_points:
            if original_index in moved_to_indices:
                continue
            if not isinstance(grid[original_index], Point):
                continue
            new_index = determine_movement_direction(grid, original_index)
            if new_index == -1:
                continue
            grid[new_index] = grid[original_index]
            grid[new_index].center_index = new_index
            grid[original_index] = 0
            update_connections_after_move(grid, grid_name, original_index, new_index)
            moved_to_indices.add(new_index)
            print(f"[Move] grid={grid_name}, old_index={original_index} -> new_index={new_index}")
    return grids[0], grids[1], grids[2], grids[3], grids[4]

def transistor_style_signal_propagation(grid_layer_1: list,
                                         grid_layer_2: list,
                                         grid_layer_3: list,
                                         grid_layer_4: list,
                                         grid_layer_5: list) -> tuple:
    all_grids = [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]
    for grid in all_grids:
        for i in range(len(grid)):
            if not isinstance(grid[i], Point):
                continue
            point = grid[i]
            input_signals = []
            for input_connection in point.input_ports:
                signal_value = input_connection.get("signal", 0)
                if signal_value > 0:
                    input_signals.append(signal_value)
            control_triggered = False
            for control_connection in point.control_ports:
                if control_connection.get("signal", 0) > CONTROL_SIGNAL_THRESHOLD:
                    control_triggered = True
                    break
            if control_triggered:
                for control_connection in point.control_ports:
                    control_connection["signal"] = 0
                for input_connection in point.input_ports:
                    input_connection["signal"] = 0
                continue
            output_signal = max(input_signals) if input_signals else 0
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
                    target_point.brightness = min(max(target_point.brightness, output_signal), MAX_BRIGHTNESS)
            for output_connection in point.output_ports:
                output_connection["signal"] = 0
            for control_connection in point.control_ports:
                control_connection["signal"] = 0
            for input_connection in point.input_ports:
                input_connection["signal"] = 0
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

def initialize_api_ports(grid_layer_1: list, grid_layer_5: list) -> tuple:
    for port_index in range(API_PORT_COUNT):
        grid_layer_1[port_index] = Point(center_index=port_index, brightness=0)
    for port_index in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        grid_layer_5[port_index] = Point(center_index=port_index, brightness=0)
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
            print(f"[API] Error: binary_string position {port_index} is not 0 or 1, received '{character}'")
            return False
        if isinstance(grid_layer_1[port_index], Point):
            grid_layer_1[port_index].brightness = signal_value
            grid_layer_1[port_index].input_ports.clear()
            grid_layer_1[port_index].input_ports.append({
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value,
                "port_type": "input"
            })
        else:
            grid_layer_1[port_index] = Point(center_index=port_index, brightness=signal_value)
            grid_layer_1[port_index].input_ports.append({
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value,
                "port_type": "input"
            })
    print(f"[API] set_api_input: wrote 32-bit binary -> {binary_string}")
    return True

def get_api_output(grid_layer_5: list) -> str:
    binary_output = ""
    for port_index in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        if isinstance(grid_layer_5[port_index], Point):
            if grid_layer_5[port_index].brightness >= 5:
                binary_output += "1"
            else:
                binary_output += "0"
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
        return utf8_character
    except (ValueError, UnicodeDecodeError):
        return binary_output

# ===========================================================================
# 新增：读取二进制网格文件
# ===========================================================================
def load_full_grid_from_file(
    filename: str = GRID_FILE_NAME,
    suffix: str = GRID_FILE_SUFFIX
) -> tuple:
    """
    从二进制文件加载完整的5层网格
    :return: (grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5)
    """
    full_filename = f"{filename}{suffix}"
    full_grid = np.load(full_filename, allow_pickle=True)
    
    # 转换为原代码的列表格式（完全兼容）
    grid_layer_1 = full_grid[0].tolist()
    grid_layer_2 = full_grid[1].tolist()
    grid_layer_3 = full_grid[2].tolist()
    grid_layer_4 = full_grid[3].tolist()
    grid_layer_5 = full_grid[4].tolist()
    
    print(f"✅ 网格加载完成：{full_filename}")
    return grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5

# ===========================================================================
# 新增：读取自定义格式文本输入文件
# ===========================================================================
def read_input_from_text_file(
    filename: str = INPUT_FILE_NAME,
    suffix: str = INPUT_FILE_SUFFIX
) -> list:
    """
    读取文本输入文件，解析# 开头的行
    格式要求：每行以# 开头，# 后面的空格自动去掉
    示例：
    # Hello World
    # 123456
    # 测试中文
    :return: 解析后的输入内容列表
    """
    full_filename = f"{filename}{suffix}"
    input_lines = []
    
    try:
        with open(full_filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    # 去掉# 和后面的空格
                    content = line[2:].strip()
                    if content:
                        input_lines.append(content)
        print(f"✅ 输入文件加载完成：{full_filename}，共{len(input_lines)}条输入")
        return input_lines
    except FileNotFoundError:
        print(f"❌ 错误：输入文件 {full_filename} 不存在")
        return []

# ===========================================================================
# 主程序初始化（替换原硬编码部分）
# ===========================================================================
if __name__ == "__main__":
    # 1. 从二进制文件加载网格（替换原硬编码种子点）
    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = load_full_grid_from_file()
    
    # 2. 初始化API端口（保留原逻辑）
    grid_layer_1, grid_layer_5 = initialize_api_ports(grid_layer_1, grid_layer_5)
    
    # 3. 读取文本输入文件
    input_list = read_input_from_text_file()
    if not input_list:
        print("❌ 没有可处理的输入，程序退出")
        exit()
    
    # 4. 主循环（依次处理每条输入）
    for input_index, user_input in enumerate(input_list):
        print(f"\n{'='*50}")
        print(f"处理第 {input_index+1}/{len(input_list)} 条输入：{user_input}")
        print(f"{'='*50}\n")
        
        # ===== Stage A: Input Processing =====
        active_points_grid_layer_1 = []
        active_points_grid_layer_2 = []
        active_points_grid_layer_3 = []
        active_points_grid_layer_4 = []
        active_points_grid_layer_5 = []
        binary_string_list = []
        random_pool = []
        
        input_character_list = list(user_input)
        binary_string_list = []
        padded_binary_string_list = []
        for character in input_character_list:
            unicode_encoded_bytes = character.encode("utf-8")
            binary_string = ''.join(f'{byte:08b}' for byte in unicode_encoded_bytes)
            padded_binary_string = binary_string.ljust(GRID_SIDE_LENGTH, '0')[:GRID_SIDE_LENGTH]
            print(f"'{character}' -> {padded_binary_string}")
            padded_binary_string_list.append(padded_binary_string)
            binary_string_list.append(padded_binary_string)
        
        random_pool = build_random_pool(binary_string_list)
        print(f"[Debug] random_pool length: {len(random_pool)}")
        
        api_input_string = padded_binary_string_list[0]
        set_api_input(grid_layer_1, api_input_string)
        
        # ===== Stage B: Active Point Detection =====
        active_points_grid_layer_1 = detect_active_points(grid_layer_1)
        active_points_grid_layer_2 = detect_active_points(grid_layer_2)
        active_points_grid_layer_3 = detect_active_points(grid_layer_3)
        active_points_grid_layer_4 = detect_active_points(grid_layer_4)
        active_points_grid_layer_5 = detect_active_points(grid_layer_5)
        print(f"[Debug] active_points count - Layer1:{len(active_points_grid_layer_1)}, Layer2:{len(active_points_grid_layer_2)}, Layer3:{len(active_points_grid_layer_3)}, Layer4:{len(active_points_grid_layer_4)}, Layer5:{len(active_points_grid_layer_5)}")
        
        # ===== Stage C: Diamond Render (Additive) =====
        grid_layer_1 = render_grid(grid_layer_1, active_points_grid_layer_1)
        grid_layer_2 = render_grid(grid_layer_2, active_points_grid_layer_2)
        grid_layer_3 = render_grid(grid_layer_3, active_points_grid_layer_3)
        grid_layer_4 = render_grid(grid_layer_4, active_points_grid_layer_4)
        grid_layer_5 = render_grid(grid_layer_5, active_points_grid_layer_5)
        
        # ===== Stage D: Anneal (Subtractive) + Connection Establishment =====
        grid_layer_1 = anneal_and_connect(grid_layer_1, active_points_grid_layer_1, random_pool, "grid_layer_1")
        grid_layer_2 = anneal_and_connect(grid_layer_2, active_points_grid_layer_2, random_pool, "grid_layer_2")
        grid_layer_3 = anneal_and_connect(grid_layer_3, active_points_grid_layer_3, random_pool, "grid_layer_3")
        grid_layer_4 = anneal_and_connect(grid_layer_4, active_points_grid_layer_4, random_pool, "grid_layer_4")
        grid_layer_5 = anneal_and_connect(grid_layer_5, active_points_grid_layer_5, random_pool, "grid_layer_5")
        
        # ===== Stage E: Clear Non-Point Brightness =====
        grid_layer_1 = clear_non_point_brightness(grid_layer_1)
        grid_layer_2 = clear_non_point_brightness(grid_layer_2)
        grid_layer_3 = clear_non_point_brightness(grid_layer_3)
        grid_layer_4 = clear_non_point_brightness(grid_layer_4)
        grid_layer_5 = clear_non_point_brightness(grid_layer_5)
        
        # ===== Stage F: Cross-Layer Preload =====
        grid_layer_2 = preload_next_grid(grid_layer_1, grid_layer_2, active_points_grid_layer_1)
        grid_layer_3 = preload_next_grid(grid_layer_2, grid_layer_3, active_points_grid_layer_2)
        grid_layer_4 = preload_next_grid(grid_layer_3, grid_layer_4, active_points_grid_layer_3)
        grid_layer_5 = preload_next_grid(grid_layer_4, grid_layer_5, active_points_grid_layer_4)
        
        # ===== Stage G: Node Movement =====
        grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = execute_movement_phase(
            grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
        )
        
        # ===== Stage H: Transistor-Style Signal Propagation =====
        grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = transistor_style_signal_propagation(
            grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
        )
        
        # ===== Stage I: Display Grids =====
        display_grid(grid_layer_1, "Grid Layer 1")
        display_grid(grid_layer_2, "Grid Layer 2")
        display_grid(grid_layer_3, "Grid Layer 3")
        display_grid(grid_layer_4, "Grid Layer 4")
        display_grid(grid_layer_5, "Grid Layer 5")
        
        # ===== Stage J: API Output =====
        api_output_character = get_api_output(grid_layer_5)
        print(f"[API Output] UTF-8 character: {api_output_character}")
    
    print("\n✅ 所有输入处理完成！")