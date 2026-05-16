# -*- coding: utf-8 -*-
#!C:/Users/Administrator/Desktop/Alice McCord/app.py python3
import inspect


# ===========================================================================
# Point 类定义
# ===========================================================================
class Point:
    """32×32网格中的节点类，包含亮度值和三种端口列表。

    属性:
        center_index: 该Point在网格中的扁平索引（0~1023）
        brightness: 当前亮度值（0~9），9为最亮/活跃状态
        control_ports: 控制端口连接列表，每个连接为dict
        input_ports: 输入端口连接列表，每个连接为dict
        output_ports: 输出端口连接列表，每个连接为dict
    """
    def __init__(self, center_index, brightness, control_ports=None, input_ports=None, output_ports=None):
        self.center_index = center_index
        self.brightness = brightness
        self.control_ports = [] if control_ports is None else control_ports
        self.input_ports = [] if input_ports is None else input_ports
        self.output_ports = [] if output_ports is None else output_ports


# ===========================================================================
# 工具函数
# ===========================================================================
def build_random_pool(binary_string_list):
    """根据二进制字符串列表构建随机池。

    将每个32位二进制字符串按4位一组拆分为6组，
    每组4位求和得到一个0~4的整数，存入随机池。

    参数:
        binary_string_list: 二进制字符串列表，每个字符串长度为32

    返回:
        list: 随机池，包含若干个0~4的整数
    """
    random_pool = []
    for i in range(len(binary_string_list)):
        current_binary_string = binary_string_list[i]
        random_pool.append(int(current_binary_string[0]) + int(current_binary_string[1]) + int(current_binary_string[2]) + int(current_binary_string[3]))
        random_pool.append(int(current_binary_string[4]) + int(current_binary_string[5]) + int(current_binary_string[6]) + int(current_binary_string[7]))
        random_pool.append(int(current_binary_string[8]) + int(current_binary_string[9]) + int(current_binary_string[10]) + int(current_binary_string[11]))
        random_pool.append(int(current_binary_string[12]) + int(current_binary_string[13]) + int(current_binary_string[14]) + int(current_binary_string[15]))
        random_pool.append(int(current_binary_string[16]) + int(current_binary_string[17]) + int(current_binary_string[18]) + int(current_binary_string[19]))
        random_pool.append(int(current_binary_string[20]) + int(current_binary_string[21]) + int(current_binary_string[22]) + int(current_binary_string[23]))
    return random_pool


def detect_active_points(grid):
    """检测网格中所有亮度为9的活跃Point。

    遍历整个网格，找到所有isinstance为Point且brightness==9的元素，
    返回其索引和亮度值的元组列表。

    参数:
        grid: 长度为1024的网格列表

    返回:
        list: [(point_index, brightness), ...] 活跃点列表
    """
    active_points = []
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            if grid[i].brightness == 9:
                active_points.append((i, grid[i].brightness))
    return active_points


def detect_all_points(grid):
    all_points = []
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            all_points.append((i, grid[i].brightness))
    return all_points


def determine_movement_direction(grid, point_index):
    direction_offsets = [
        ("down", 32),
        ("right", 1),
        ("up", -32),
        ("left", -1),
    ]
    candidates = []
    for dir_name, offset in direction_offsets:
        target_idx = point_index + offset
        if target_idx < 0 or target_idx >= 1024:
            continue
        if dir_name == "left" and point_index % 32 == 0:
            continue
        if dir_name == "right" and point_index % 32 == 31:
            continue
        if isinstance(grid[target_idx], Point):
            continue
        signal_val = grid[target_idx]
        candidates.append((signal_val, dir_name, target_idx))
    if not candidates:
        return -1
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_signal = candidates[0][0]
    if best_signal <= 0:
        return -1
    return candidates[0][2]


def update_connections_after_move(grid, grid_name, old_index, new_index):
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            point = grid[i]
            for port_list in [point.control_ports, point.input_ports, point.output_ports]:
                for conn in port_list:
                    if conn.get("block_name") == grid_name:
                        if conn.get("source_point_index") == old_index:
                            conn["source_point_index"] = new_index
                        if conn.get("target_point_index") == old_index:
                            conn["target_point_index"] = new_index


def execute_movement_phase(grid_1, grid_2, grid_3, grid_4, grid_5):
    grids = [grid_1, grid_2, grid_3, grid_4, grid_5]
    grid_names = ["grid_1", "grid_2", "grid_3", "grid_4", "grid_5"]
    for grid_idx in range(len(grids)):
        grid = grids[grid_idx]
        grid_name = grid_names[grid_idx]
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
            print(f"[移动] 网格={grid_name}, 旧索引={original_index} -> 新索引={new_index}")
    return grids[0], grids[1], grids[2], grids[3], grids[4]


def clear_non_point_brightness(grid):
    """将网格中所有非Point对象位置的亮度值清零。

    遍历网格，对于不是Point实例的位置（即存储数字的位置），
    将其值重置为0。这用于退火后清理残留的数字亮度值。

    参数:
        grid: 长度为1024的网格列表

    返回:
        list: 清理后的网格列表
    """
    for i in range(len(grid)):
        if not isinstance(grid[i], Point):
            grid[i] = 0
    return grid


def diamond_render_single_point(grid, point_index, source_brightness):
    """对单个Point执行一次菱形亮度扩散渲染（加法操作）。

    以该Point为中心，向其曼哈顿距离内的所有邻居扩散亮度。
    亮度值 = source_brightness - 曼哈顿距离。
    对于Point对象只修改其brightness属性，绝不覆盖Point对象本身。
    对于非Point位置直接存储计算出的亮度值。

    参数:
        grid: 长度为1024的网格列表
        point_index: 源Point的扁平索引
        source_brightness: 源Point的亮度值

    返回:
        list: 修改后的网格列表
    """
    column_x = point_index % 32
    row_y = point_index // 32
    for delta_y in range(-source_brightness, source_brightness + 1):
        for delta_x in range(-source_brightness, source_brightness + 1):
            manhattan_distance = abs(delta_x) + abs(delta_y)
            if manhattan_distance >= source_brightness:
                continue
            neighbor_x = column_x + delta_x
            neighbor_y = row_y + delta_y
            if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                target_flat_index = neighbor_y * 32 + neighbor_x
                computed_brightness = source_brightness - manhattan_distance
                if isinstance(grid[target_flat_index], Point):
                    if computed_brightness > grid[target_flat_index].brightness:
                        grid[target_flat_index].brightness = min(computed_brightness, 9)
                else:
                    if computed_brightness > grid[target_flat_index]:
                        grid[target_flat_index] = min(computed_brightness, 9)
    return grid


# ===========================================================================
# 渲染函数
# ===========================================================================
def render_grid(grid, active_points):
    """对整个网格执行菱形亮度扩散渲染（加法操作）。

    遍历所有活跃点，以每个活跃点为中心进行菱形扩散。
    渲染是加法操作：新亮度 = max(原亮度, 计算亮度)。
    对于Point对象只修改brightness属性，绝不覆盖Point对象为数字。
    对于非Point位置直接存储计算出的亮度值。

    参数:
        grid: 长度为1024的网格列表
        active_points: [(point_index, brightness), ...] 活跃点列表

    返回:
        list: 渲染后的网格列表
    """
    for point_index, _ in active_points:
        source_brightness = grid[point_index].brightness
        column_x = point_index % 32
        row_y = point_index // 32
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid[target_flat_index], Point):
                        if computed_brightness > grid[target_flat_index].brightness:
                            grid[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid[target_flat_index]:
                            grid[target_flat_index] = min(computed_brightness, 9)
    return grid


# ===========================================================================
# 退火函数
# ===========================================================================
def anneal_and_connect(grid, active_points, random_pool, grid_name):
    """对网格执行退火（减法操作）并建立Point之间的端口连接。

    退火是渲染的逆操作：新亮度 = 原亮度 + 计算亮度变化（负值）。
    退火遍历范围比渲染多一圈（manhattan_distance <= source_brightness），
    确保完全抵消渲染的影响。

    连接逻辑：
    - 退火过程中若某个区域被修改，且random_pool条件满足，
      则在四个方向（上下左右）尝试建立连接。
    - 分别检查目标Point的control_ports、input_ports、output_ports长度，
      只有对应类型端口列表长度<9时才建立该类型的双向连接。
    - 连接信息包含：block_name, port_identifier, source_point_index,
      target_point_index, signal=0。
    - 当一个Point的三个端口列表长度都等于9时，将该Point亮度设为9。
    - 连接完成后仅对当前修改过的Point执行一次单点菱形渲染。

    参数:
        grid: 长度为1024的网格列表
        active_points: [(point_index, brightness), ...] 活跃点列表
        random_pool: 随机池列表，用于端口类型判定和连接方向判定
        grid_name: 网格名称字符串，如"grid_1"

    返回:
        list: 退火并建立连接后的网格列表
    """
    for point_index, source_brightness in active_points:
        column_x = point_index % 32
        row_y = point_index // 32
        block_modified_flag = False

        # 调试打印：每个活跃点开始处理
        print(f"[退火] 网格={grid_name}, 索引={point_index}, 亮度={source_brightness}")

        # 退火：减法操作，遍历范围 manhattan_distance <= source_brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    # 计算亮度变化量（负值），退火是减法操作
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

        # 连接建立：仅在退火修改了区域且random_pool条件满足时执行
        if block_modified_flag:
            # 四个方向：下(+32)、上(-32)、左(-1)、右(+1)
            for direction_offset in [32, -32, -1, 1]:
                if point_index < len(random_pool) and random_pool[point_index] == 1:
                    target_idx = point_index + direction_offset
                    if 0 <= target_idx < 1024:
                        if isinstance(grid[target_idx], Point):
                            if grid[target_idx].brightness < 9:
                                # 确定端口类型：根据random_pool连续3个值累加
                                port_type_accumulator = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_type_accumulator += 1
                                if port_type_accumulator == 1:
                                    port_label = "control"
                                elif port_type_accumulator == 2:
                                    port_label = "input"
                                elif port_type_accumulator == 3:
                                    port_label = "output"
                                else:
                                    port_label = "control"

                                # 分别检查三种端口列表长度，只有<9时才建立该类型连接
                                connection_established = False

                                if port_label == "control":
                                    if len(grid[target_idx].control_ports) < 9 and len(grid[point_index].control_ports) < 9:
                                        connection_info_source = {
                                            "block_name": grid_name,
                                            "port_identifier": "control",
                                            "source_point_index": point_index,
                                            "target_point_index": target_idx,
                                            "signal": 0
                                        }
                                        connection_info_target = {
                                            "block_name": grid_name,
                                            "port_identifier": "control",
                                            "source_point_index": target_idx,
                                            "target_point_index": point_index,
                                            "signal": 0
                                        }
                                        grid[point_index].control_ports.append(connection_info_source)
                                        grid[target_idx].control_ports.append(connection_info_target)
                                        connection_established = True
                                        print(f"[连接] 网格={grid_name}, 端口类型=control, 源索引={point_index}, 目标索引={target_idx}")

                                elif port_label == "input":
                                    if len(grid[target_idx].input_ports) < 9 and len(grid[point_index].input_ports) < 9:
                                        connection_info_source = {
                                            "block_name": grid_name,
                                            "port_identifier": "input",
                                            "source_point_index": point_index,
                                            "target_point_index": target_idx,
                                            "signal": 0
                                        }
                                        connection_info_target = {
                                            "block_name": grid_name,
                                            "port_identifier": "input",
                                            "source_point_index": target_idx,
                                            "target_point_index": point_index,
                                            "signal": 0
                                        }
                                        grid[point_index].input_ports.append(connection_info_source)
                                        grid[target_idx].input_ports.append(connection_info_target)
                                        connection_established = True
                                        print(f"[连接] 网格={grid_name}, 端口类型=input, 源索引={point_index}, 目标索引={target_idx}")

                                elif port_label == "output":
                                    if len(grid[target_idx].output_ports) < 9 and len(grid[point_index].output_ports) < 9:
                                        connection_info_source = {
                                            "block_name": grid_name,
                                            "port_identifier": "output",
                                            "source_point_index": point_index,
                                            "target_point_index": target_idx,
                                            "signal": 0
                                        }
                                        connection_info_target = {
                                            "block_name": grid_name,
                                            "port_identifier": "output",
                                            "source_point_index": target_idx,
                                            "target_point_index": point_index,
                                            "signal": 0
                                        }
                                        grid[point_index].output_ports.append(connection_info_source)
                                        grid[target_idx].output_ports.append(connection_info_target)
                                        connection_established = True
                                        print(f"[连接] 网格={grid_name}, 端口类型=output, 源索引={point_index}, 目标索引={target_idx}")

                                # 连接建立后检查：若三个端口列表长度都等于9，设亮度为9
                                if connection_established:
                                    if (len(grid[point_index].control_ports) == 9 and
                                        len(grid[point_index].input_ports) == 9 and
                                        len(grid[point_index].output_ports) == 9):
                                        grid[point_index].brightness = 9
                                    if (len(grid[target_idx].control_ports) == 9 and
                                        len(grid[target_idx].input_ports) == 9 and
                                        len(grid[target_idx].output_ports) == 9):
                                        grid[target_idx].brightness = 9

                                    # 连接完成后仅对当前修改过的Point执行一次单点菱形渲染
                                    if grid[point_index].brightness > 0:
                                        grid = diamond_render_single_point(grid, point_index, grid[point_index].brightness)
                                        print(f"[重渲染] 网格={grid_name}, 索引={point_index}")

    return grid


# ===========================================================================
# 预加载函数
# ===========================================================================
def preload_next_grid(source_grid, target_grid, active_points):
    """将源网格活跃点的菱形扩散预加载到目标网格的前3行。

    仅对目标网格的 y < 3 区域进行亮度扩散（加法操作），
    用于跨网格的信号预加载。

    参数:
        source_grid: 源网格列表（长度为1024）
        target_grid: 目标网格列表（长度为1024）
        active_points: 源网格的活跃点列表

    返回:
        list: 修改后的目标网格列表
    """
    for point_index, _ in active_points:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = source_grid[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                # 仅处理目标网格的前3行（y < 3）
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 3:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(target_grid[target_flat_index], Point):
                        if computed_brightness > target_grid[target_flat_index].brightness:
                            target_grid[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > target_grid[target_flat_index]:
                            target_grid[target_flat_index] = min(computed_brightness, 9)
    return target_grid


# ===========================================================================
# 显示函数
# ===========================================================================
def display_grid(grid, grid_name):
    """按32×32矩阵格式打印网格的亮度值。

    对于Point对象打印其brightness属性值，
    对于非Point位置直接打印存储的数字值。

    参数:
        grid: 长度为1024的网格列表
        grid_name: 网格名称字符串，如"Grid 1"
    """
    print(f"====== {grid_name} ======")
    for i in range(0, 32 * 32, 32):
        row = []
        for j in range(i, i + 32):
            if isinstance(grid[j], Point):
                row.append(str(grid[j].brightness))
            else:
                row.append(str(grid[j]))
        print(' '.join(row))
    print()


# ===========================================================================
# API 函数
# ===========================================================================
def initialize_api_ports(grid_1, grid_5):
    """初始化API输入输出端口。

    在grid_1的第一行（索引0~31）放置32个亮度=0的空Point作为API输入端口。
    在grid_5的最后一行（索引992~1023）放置32个亮度=0的空Point作为API输出端口。

    参数:
        grid_1: 网格1列表
        grid_5: 网格5列表

    返回:
        tuple: (修改后的grid_1, 修改后的grid_5)
    """
    # grid_1 第一行：32个API输入端口（初始亮度为0，等待二进制字符串输入）
    for port_index in range(32):
        grid_1[port_index] = Point(center_index=port_index, brightness=0)

    # grid_5 最后一行（索引992~1023）：32个API输出端口（初始亮度为0）
    for port_index in range(992, 1024):
        grid_5[port_index] = Point(center_index=port_index, brightness=0)

    return grid_1, grid_5


def set_api_input(grid_1, binary_string):
    """将二进制字符串写入grid_1第一行的API输入端口。

    按索引依次设置grid_1[0]~grid_1[31]共32个Point的brightness值：
    字符'1'对应brightness=9，字符'0'对应brightness=0。
    同时在每个端口的input_ports中记录单向信号（不需要双向连接）。
    输入不足32位自动补0，超过32位自动截断。

    参数:
        grid_1: 网格1列表
        binary_string: 二进制字符串，如"0100100001101001..."

    返回:
        bool: 设置成功返回True，失败返回False
    """

    # 自动补齐或截断到32位
    if len(binary_string) < 32:
        binary_string = binary_string.ljust(32, '0')
    elif len(binary_string) > 32:
        binary_string = binary_string[:32]

    for port_index in range(32):
        char = binary_string[port_index]
        if char == '1':
            signal_value = 9
        elif char == '0':
            signal_value = 0
        else:
            print(f"[API] 错误：binary_string第{port_index}位不是0或1，收到'{char}'")
            return False

        if isinstance(grid_1[port_index], Point):
            grid_1[port_index].brightness = signal_value
            # 清空旧的API信号记录，添加新的单向信号记录
            grid_1[port_index].input_ports.clear()
            grid_1[port_index].input_ports.append({
                "block_name": "api_input",
                "port_identifier": "input",
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value
            })
        else:
            grid_1[port_index] = Point(center_index=port_index, brightness=signal_value)
            grid_1[port_index].input_ports.append({
                "block_name": "api_input",
                "port_identifier": "input",
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value
            })

    print(f"[API] set_api_input: 已写入32位二进制字符串 -> {binary_string}")
    return True


def get_api_output(grid_5):
    """读取grid_5最后一行API输出端口，转换为UTF-8字符。

    读取grid_5索引992~1023的32个Point的brightness值，
    将>=5的视为'1'，<5的视为'0'，拼接成32位二进制字符串。
    再将32位二进制字符串按每8位一组拆分为4个字节，
    转换为UTF-8编码的字符并返回。

    参数:
        grid_5: 网格5列表

    返回:
        str: UTF-8解码后的字符，解码失败则返回原始二进制字符串
    """
    binary_output = ""
    for port_index in range(992, 1024):
        if isinstance(grid_5[port_index], Point):
            if grid_5[port_index].brightness >= 5:
                binary_output += "1"
            else:
                binary_output += "0"
        else:
            binary_output += "0"

    # 将32位二进制字符串按每8位拆分为字节，转换为UTF-8字符
    try:
        byte_list = []
        for byte_index in range(0, 32, 8):
            byte_str = binary_output[byte_index:byte_index + 8]
            byte_value = int(byte_str, 2)
            byte_list.append(byte_value)
        byte_data = bytes(byte_list)
        utf8_character = byte_data.decode("utf-8")
        return utf8_character
    except (ValueError, UnicodeDecodeError):
        return binary_output


def propagate_signals(grid_1, grid_2, grid_3, grid_4, grid_5):
    """在所有已建立连接的端口间传播signal值。

    遍历所有5个网格的所有Point，检查每个Point的output_ports列表。
    若某个output_port的signal值不为0，则将该signal值传播到
    target_point_index对应Point的input_ports中匹配的连接。

    参数:
        grid_1 ~ grid_5: 五个网格列表

    返回:
        tuple: (grid_1, grid_2, grid_3, grid_4, grid_5) 信号传播后的网格
    """
    all_grids = [grid_1, grid_2, grid_3, grid_4, grid_5]

    for grid in all_grids:
        for i in range(len(grid)):
            if isinstance(grid[i], Point):
                point = grid[i]
                # 遍历该Point的所有output_ports
                for output_conn in point.output_ports:
                    signal_val = output_conn.get("signal", 0)
                    if signal_val != 0:
                        target_idx = output_conn.get("target_point_index", -1)
                        source_idx = output_conn.get("source_point_index", -1)
                        # 在目标Point的input_ports中查找匹配的连接并更新signal
                        if 0 <= target_idx < 1024 and isinstance(grid[target_idx], Point):
                            for input_conn in grid[target_idx].input_ports:
                                if input_conn.get("source_point_index") == target_idx and input_conn.get("target_point_index") == source_idx:
                                    input_conn["signal"] = signal_val
                            # 同时更新目标Point的brightness
                            if signal_val > grid[target_idx].brightness:
                                grid[target_idx].brightness = min(signal_val, 9)

    return grid_1, grid_2, grid_3, grid_4, grid_5


# ===========================================================================
# 全局变量初始化
# ===========================================================================
# 五个32×32网格，每个1024个元素，初值为0
grid_1 = [0] * 1024
grid_2 = [0] * 1024
grid_3 = [0] * 1024
grid_4 = [0] * 1024
grid_5 = [0] * 1024

# 用户输入相关变量
user_input_raw = 0
input_character_list = 0
unicode_encoded_bytes = 0
binary_string = 0
padded_binary_string = 0
binary_string_list = []

# 随机池和活跃点列表
random_pool = []
active_points_grid_1 = []
active_points_grid_2 = []
active_points_grid_3 = []
active_points_grid_4 = []
active_points_grid_5 = []

# 当前处理的二进制字符串
current_binary_string = []

# ===========================================================================
# 初始种子点放置：每个网格索引30~39处放置10个亮度=4的Point
# ===========================================================================
for i in range(10):
    grid_1[i + 30] = Point(center_index=int(i) + 3, brightness=4)
for i in range(10):
    grid_2[i + 30] = Point(center_index=int(i) + 3, brightness=4)
for i in range(10):
    grid_3[i + 30] = Point(center_index=int(i) + 3, brightness=4)
for i in range(10):
    grid_4[i + 30] = Point(center_index=int(i) + 3, brightness=4)
for i in range(10):
    grid_5[i + 30] = Point(center_index=int(i) + 3, brightness=4)

# ===========================================================================
# API端口初始化：grid_1首行输入 + grid_5末行输出
# ===========================================================================
grid_1, grid_5 = initialize_api_ports(grid_1, grid_5)
for i in range(420):
    grid_1[i + 3] = Point(center_index= int(i) + 3, brightness=4)
for i in range(420):
    grid_2[i + 3] = Point(center_index= int(i) + 3, brightness=4)
for i in range(420):
    grid_3[i + 3] = Point(center_index= int(i) + 3, brightness=4)
for i in range(420):
    grid_4[i + 3] = Point(center_index= int(i) + 3, brightness=4)
for i in range(420):
    grid_5[i + 3] = Point(center_index= int(i) + 3, brightness=4)
# ===========================================================================
# 主循环
# ===========================================================================
while True:
    # ===== 阶段A：清空并处理输入 =====
    active_points_grid_1.clear()
    active_points_grid_2.clear()
    active_points_grid_3.clear()
    active_points_grid_4.clear()
    active_points_grid_5.clear()
    binary_string_list.clear()
    random_pool.clear()

    # 第一个输入：用于随机池构建和处理逻辑
    user_input_raw = input("input:")
    input_character_list = list(user_input_raw)
    binary_string_list = []
    padded_binary_string_list = []
    # 逐字符转换为32位二进制字符串
    for i in input_character_list:
        unicode_encoded_bytes = i.encode("utf-8")
        binary_string = ''.join(f'{byte:08b}' for byte in unicode_encoded_bytes)
        padded_binary_string = binary_string.ljust(32, '0')[:32]
        print(f"'{i}' -> {padded_binary_string}")
        padded_binary_string_list.append(padded_binary_string)
        binary_string_list.append(padded_binary_string)

    # 构建随机池（仅用第一个输入）
    random_pool = build_random_pool(binary_string_list)
    print(f"[调试] 随机池长度: {len(random_pool)}")

    # 第二个输入：用于API输入端口（独立于随机池输入）
    api_input_string = padded_binary_string_list[0]
    set_api_input(grid_1, api_input_string)

    # ===== 阶段B：活跃点检测 =====
    active_points_grid_1 = detect_active_points(grid_1)
    active_points_grid_2 = detect_active_points(grid_2)
    active_points_grid_3 = detect_active_points(grid_3)
    active_points_grid_4 = detect_active_points(grid_4)
    active_points_grid_5 = detect_active_points(grid_5)

    print(f"[调试] 活跃点数量 - Grid1:{len(active_points_grid_1)}, Grid2:{len(active_points_grid_2)}, Grid3:{len(active_points_grid_3)}, Grid4:{len(active_points_grid_4)}, Grid5:{len(active_points_grid_5)}")

    # ===== 阶段C：菱形渲染（加法操作）=====
    grid_1 = render_grid(grid_1, active_points_grid_1)
    grid_2 = render_grid(grid_2, active_points_grid_2)
    grid_3 = render_grid(grid_3, active_points_grid_3)
    grid_4 = render_grid(grid_4, active_points_grid_4)
    grid_5 = render_grid(grid_5, active_points_grid_5)

    # ===== 阶段D：退火（减法操作）+ 连接建立 =====
    grid_1 = anneal_and_connect(grid_1, active_points_grid_1, random_pool, "grid_1")
    grid_2 = anneal_and_connect(grid_2, active_points_grid_2, random_pool, "grid_2")
    grid_3 = anneal_and_connect(grid_3, active_points_grid_3, random_pool, "grid_3")
    grid_4 = anneal_and_connect(grid_4, active_points_grid_4, random_pool, "grid_4")
    grid_5 = anneal_and_connect(grid_5, active_points_grid_5, random_pool, "grid_5")

    # ===== 阶段E：退火后清理 —— 将所有非Point位置亮度设为0 =====
    grid_1 = clear_non_point_brightness(grid_1)
    grid_2 = clear_non_point_brightness(grid_2)
    grid_3 = clear_non_point_brightness(grid_3)
    grid_4 = clear_non_point_brightness(grid_4)
    grid_5 = clear_non_point_brightness(grid_5)

    # ===== 阶段F：预加载 —— 跨网格菱形扩散到下一网格的前3行 =====
    grid_2 = preload_next_grid(grid_1, grid_2, active_points_grid_1)
    grid_3 = preload_next_grid(grid_2, grid_3, active_points_grid_2)
    grid_4 = preload_next_grid(grid_3, grid_4, active_points_grid_3)
    grid_5 = preload_next_grid(grid_4, grid_5, active_points_grid_4)

    # ===== 阶段G：信号传播 =====
    grid_1, grid_2, grid_3, grid_4, grid_5 = propagate_signals(grid_1, grid_2, grid_3, grid_4, grid_5)

    # ===== 阶段G+：Point移动与连接更新 =====
    grid_1, grid_2, grid_3, grid_4, grid_5 = execute_movement_phase(grid_1, grid_2, grid_3, grid_4, grid_5)

    # ===== 阶段H：显示输出 =====
    display_grid(grid_1, "Grid 1")
    display_grid(grid_2, "Grid 2")
    display_grid(grid_3, "Grid 3")
    display_grid(grid_4, "Grid 4")
    display_grid(grid_5, "Grid 5")

    # ===== 阶段I：API输出 =====
    api_output_character = get_api_output(grid_5)
    print(f"[API输出] UTF-8字符: {api_output_character}")

    # ===== 阶段J：调试信息 =====
    if isinstance(grid_1[30], Point):
        print("grid_1[30].control_ports:", grid_1[30].control_ports)
        print("grid_1[30].input_ports:", grid_1[30].input_ports)
        print("grid_1[30].output_ports:", grid_1[30].output_ports)