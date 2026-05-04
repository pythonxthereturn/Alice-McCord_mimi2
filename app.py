# -*- coding: utf-8 -*-

import time
import threading
import tkinter as tk
from tkinter import TclError

# ==================== 全局常量配置 ====================
GRID_SIZE = 32                    # 网格大小 32x32
TOTAL_CELLS = GRID_SIZE * GRID_SIZE  # 总格子数
MAX_BRIGHTNESS = 9                # 最大亮度值
STAGGERED_POINT_COUNT = 200       # 交错点数量
POSITIONS_CHUNK_SIZE = 24         # 打印位置分块大小
TERMINAL_SLEEP_SECONDS = 30       # 终端循环休眠时间

# ==================== 全局光源数组 ====================
light_sources_1 = [0] * TOTAL_CELLS  # 第一层光源
light_sources_2 = [0] * TOTAL_CELLS  # 第二层光源
light_sources_3 = [0] * TOTAL_CELLS  # 第三层光源
light_sources_4 = [0] * TOTAL_CELLS  # 第四层光源
light_sources_5 = [0] * TOTAL_CELLS  # 第五层光源












# ------------------计算距离------------------



def index_to_xy(index: int, grid_size: int = 32, start_from: int = 1) -> tuple[int, int]:
    if start_from == 1:
        index = index - 1  # 转换成0基索引方便计算
    row = index // grid_size  # 行号（y轴）
    col = index % grid_size   # 列号（x轴）
    return col, row


def manhattan_step(xy1: tuple[int, int], xy2: tuple[int, int]) -> int:
    """计算四向移动的最短步数（曼哈顿距离）"""
    x1, y1 = xy1
    x2, y2 = xy2
    return abs(x1 - x2) + abs(y1 - y2)


def chebyshev_step(xy1: tuple[int, int], xy2: tuple[int, int]) -> int:
    """计算八向移动的最短步数（切比雪夫距离）"""
    x1, y1 = xy1
    x2, y2 = xy2
    return max(abs(x1 - x2), abs(y1 - y2))






# ==================== Point 类定义 ====================





class Point:
    """
    光源点类
    属性：
        center_index: 中心点索引
        brightness: 亮度值
        asd: 控制连接列表
        asd1: 输入连接列表
        asd2: 输出连接列表
    """
    def __init__(self, center_index, brightness, asd=None, asd1=None, asd2=None): # type: ignore
        self.center_index = center_index      # 中心点位置索引
        self.brightness = brightness          # 亮度等级
        self.asd = [] if asd is None else asd    # type: ignore # 控制连接
        self.asd1 = [] if asd1 is None else asd1 # pyright: ignore[reportUnknownMemberType] # 输入连接
        self.asd2 = [] if asd2 is None else asd2 # pyright: ignore[reportUnknownMemberType] # 输出连接
    
    def __str__(self):
        """返回Point对象的字符串表示"""
        return (f"Point(idx={self.center_index}, brightness={self.brightness}, "
                f"asd={len(self.asd)}, asd1={len(self.asd1)}, asd2={len(self.asd2)})") # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
    
    def get_connection_info(self):
        """获取连接信息的详细字符串"""
        return (f"  控制连接: {self.asd}\n" # type: ignore
                f"  输入连接: {self.asd1}\n"
                f"  输出连接: {self.asd2}") # type: ignore


# ==================== 菱形光源渲染函数 ====================
def render_diamond_light(source_list, grid_size=GRID_SIZE):
    """
    渲染菱形光源
    参数：
        source_list: 光源列表
        grid_size: 网格大小
    返回：
        渲染后的亮度数组
    """
    # 初始化渲染缓冲区
    render_buffer = []
    for item in source_list:
        render_buffer.append(0 if isinstance(item, Point) else item) # pyright: ignore[reportUnknownMemberType]
    
    # 遍历所有光源点进行渲染
    for idx, item in enumerate(source_list):
        if not isinstance(item, Point):
            continue
        
        center_idx = item.center_index
        light_level = item.brightness
        cx = center_idx % grid_size    # 中心X坐标
        cy = center_idx // grid_size   # 中心Y坐标
        
        # 菱形扩散：遍历所有可能的偏移
        for dy in range(-light_level, light_level + 1):
            for dx in range(-light_level, light_level + 1):
                dist = abs(dx) + abs(dy)
                if dist >= light_level:
                    continue
                
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    target_idx = ny * grid_size + nx
                    new_val = light_level - dist
                    if new_val > render_buffer[target_idx]:
                        render_buffer[target_idx] = min(new_val, MAX_BRIGHTNESS)
    
    return render_buffer


# ==================== 退火减法渲染函数 ====================
def render_diamond_anneal(source_list, target_idx, grid_size=GRID_SIZE):
    """
    退火减法渲染：从现有渲染中减去指定Point的菱形区域
    参数：
        source_list: 光源列表
        target_idx: 目标Point索引
        grid_size: 网格大小
    返回：
        退火后的亮度数组
    """
    # 先获取基础渲染结果
    render_buffer = render_diamond_light(source_list, grid_size).copy()
    
    item = source_list[target_idx]
    if not isinstance(item, Point):
        return render_buffer
    
    center_idx = item.center_index
    light_level = item.brightness
    cx = center_idx % grid_size
    cy = center_idx // grid_size
    
    # 减去菱形区域
    for dy in range(-light_level, light_level + 1):
        for dx in range(-light_level, light_level + 1):
            dist = abs(dx) + abs(dy)
            if dist >= light_level:
                continue
            
            nx = cx + dx
            ny = cy + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                target_buffer_idx = ny * grid_size + nx
                subtract_val = light_level - dist
                render_buffer[target_buffer_idx] = max(0, render_buffer[target_buffer_idx] - subtract_val)
    
    return render_buffer


# ==================== 指针移动函数 ====================
def move_pointer(current_idx, direction, grid_size=GRID_SIZE):
    """
    移动指针位置
    参数：
        current_idx: 当前索引
        direction: 方向 (1=上, 2=下, 3=左, 4=右)
        grid_size: 网格大小
    返回：
        新位置索引
    """
    cx = current_idx % grid_size
    cy = current_idx // grid_size
    
    if direction == 1:
        cy = max(0, cy - 1)          # 向上移动
    elif direction == 2:
        cy = min(grid_size - 1, cy + 1)  # 向下移动
    elif direction == 3:
        cx = max(0, cx - 1)          # 向左移动
    elif direction == 4:
        cx = min(grid_size - 1, cx + 1)  # 向右移动
    
    return cy * grid_size + cx


# ==================== 二进制解析函数 ====================
def get_direction_from_bits(bits_str):
    """
    从4位二进制字符串获取方向
    参数：
        bits_str: 4位二进制字符串
    返回：
        方向值 (0-4)
    """
    count_1 = bits_str.count('1')
    if count_1 == 0:
        return 0
    return count_1 % 4 if count_1 % 4 != 0 else 4


def get_type_from_bits(bits_str):
    """
    从3位二进制字符串获取类型
    参数：
        bits_str: 3位二进制字符串
    返回：
        类型值 (0-3)
    """
    count_1 = bits_str.count('1')
    if count_1 == 0:
        return 0
    return count_1 % 3 if count_1 % 3 != 0 else 3


# ==================== 退火与绑定主逻辑 ====================
def process_annealing_and_binding(qwe1, qwe3_start=0):
    """
    处理退火逻辑与指针绑定
    参数：
        qwe1: 二进制字符串列表
        qwe3_start: qwe3起始位置
    返回：
        更新后的qwe3位置
    """
    print("\n" + "="*60)
    print("开始执行退火与绑定逻辑")
    print("="*60)
    
    qwe3 = qwe3_start
    binding_count = 0
    
    # 步骤1：找出所有亮度 < 9 的Point
    targets = []
    for idx, item in enumerate(light_sources_1):
        if isinstance(item, Point) and item.brightness < 9:
            targets.append(idx)
    
    print(f"找到 {len(targets)} 个目标光源点 (亮度 < 9)")
    
    # 步骤2：对每个目标执行退火和绑定
    for i, target_idx in enumerate(targets):
        current_idx = target_idx
        found = False
        
        print(f"\n处理目标 [{i+1}/{len(targets)}]: 初始位置 {target_idx}")
        
        # 最多尝试8次移动
        for attempt in range(8):
            if qwe3 >= len(qwe1):
                qwe3 = 0
            
            bin_str = qwe1[qwe3]
            qwe3 += 1
            if qwe3 >= len(qwe1):
                qwe3 = 0
            
            # 取前4位作为方向
            bits_4 = bin_str[:4]
            direction = get_direction_from_bits(bits_4)
            
            dir_names = {0: "不动", 1: "上", 2: "下", 3: "左", 4: "右"}
            print(f"  尝试 {attempt+1}/8: 二进制 '{bits_4}' -> 方向 {dir_names[direction]}")
            
            if direction != 0:
                current_idx = move_pointer(current_idx, direction)
                print(f"    移动到位置: {current_idx}")
            
            # 检查是否找到Point
            if isinstance(light_sources_1[current_idx], Point):
                found = True
                print(f"  ✓ 找到目标 Point! 位置: {current_idx}")
                break
        
        if not found:
            print(f"  ✗ 尝试8次未找到Point，跳过此目标")
            continue
        
        # 步骤3：获取类型（再取3位）
        if qwe3 >= len(qwe1):
            qwe3 = 0
        bin_str = qwe1[qwe3]
        qwe3 += 1
        if qwe3 >= len(qwe1):
            qwe3 = 0
        
        bits_3 = bin_str[:3]
        type_val = get_type_from_bits(bits_3)
        
        type_names = {0: "无", 1: "控制(asd)", 2: "输入(asd1)", 3: "输出(asd2)"}
        print(f"  类型二进制 '{bits_3}' -> {type_names[type_val]}")
        
        # 步骤4：进行绑定
        point = light_sources_1[current_idx]
        point_id = f"0_{current_idx}"
        
        if type_val == 1:
            if point_id not in point.asd:
                point.asd.append(point_id)
                print(f"  ✓ 添加到控制列表: {point_id}")
                binding_count += 1
        elif type_val == 2:
            if point_id not in point.asd1:
                point.asd1.append(point_id)
                print(f"  ✓ 添加到输入列表: {point_id}")
                binding_count += 1
        elif type_val == 3:
            if point_id not in point.asd2:
                point.asd2.append(point_id)
                print(f"  ✓ 添加到输出列表: {point_id}")
                binding_count += 1
        
        print(f"  当前Point状态: {point}")
    
    # 步骤5：重新渲染网格
    global rendered_grid_1, rendered_grid_2, rendered_grid_3, rendered_grid_4, rendered_grid_5
    rendered_grid_1 = render_diamond_light(light_sources_1, GRID_SIZE)
    rendered_grid_2 = render_diamond_light(light_sources_2, GRID_SIZE)
    rendered_grid_3 = render_diamond_light(light_sources_3, GRID_SIZE)
    rendered_grid_4 = render_diamond_light(light_sources_4, GRID_SIZE)
    rendered_grid_5 = render_diamond_light(light_sources_5, GRID_SIZE)
    
    # 打印完成信息
    print("\n" + "="*60)
    print(f"退火与绑定完成! 共绑定 {binding_count} 个连接")
    print("="*60)
    
    # 打印几个Point的连接状态
    print_sample_points()
    
    return qwe3


def print_sample_points():
    """打印几个样例Point的连接信息"""
    print("\n" + "-"*60)
    print("样例Point连接信息")
    print("-"*60)
    
    count = 0
    for idx, item in enumerate(light_sources_1):
        if isinstance(item, Point):
            # 只打印有连接的Point或前几个
            if item.asd or item.asd1 or item.asd2 or count < 5:
                print(f"\nPoint at index {idx}:")
                print(item.get_connection_info())
                count += 1
            if count >= 10:  # 最多打印10个
                break
    
    print("-"*60 + "\n")


# ==================== 初始化函数 ====================
def create_staggered_points(target_list, start, step, count, grid_size=GRID_SIZE):
    """
    创建交错分布的Point
    参数：
        target_list: 目标列表
        start: 起始索引
        step: 步长
        count: 数量
        grid_size: 网格大小
    """
    idx = start
    for _ in range(count):
        if idx >= grid_size * grid_size:
            break
        target_list[idx] = Point(center_index=idx, brightness=1)
        idx += step


def collect_brightness_1_positions(source_list):
    """收集亮度为1的Point位置"""
    return [idx for idx, item in enumerate(source_list)
            if isinstance(item, Point) and item.brightness == 1]


def print_positions_block(title, positions, chunk_size=POSITIONS_CHUNK_SIZE):
    """分块打印位置信息"""
    print(f"========== {title} ==========")
    for i in range(0, len(positions), chunk_size):
        print(positions[i:i + chunk_size])


# ==================== 初始化网格数据 ====================
# 在中心放置一个高亮度点
light_sources_1[400] = Point(center_index=400, brightness=9)

# 在第一行放置亮度9的点
idx = 0
for _ in range(GRID_SIZE // 2):
    light_sources_1[idx] = Point(center_index=idx, brightness=9)
    idx += 2

# 创建交错分布的亮度1的点
create_staggered_points(light_sources_1, 31, 4, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_2, 0, 5, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_3, 0, 5, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_4, 0, 5, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_5, 0, 5, STAGGERED_POINT_COUNT)

# 初始渲染
rendered_grid_1 = render_diamond_light(light_sources_1, GRID_SIZE)
rendered_grid_2 = render_diamond_light(light_sources_2, GRID_SIZE)
rendered_grid_3 = render_diamond_light(light_sources_3, GRID_SIZE)
rendered_grid_4 = render_diamond_light(light_sources_4, GRID_SIZE)
rendered_grid_5 = render_diamond_light(light_sources_5, GRID_SIZE)


# ==================== 终端循环线程 ====================
def terminal_loop():
    """终端输入处理循环"""
    global rendered_grid_1, rendered_grid_2, rendered_grid_3, rendered_grid_4, rendered_grid_5
    all_sources = [light_sources_1, light_sources_2, light_sources_3, light_sources_4, light_sources_5]
    qwe3 = 0
    
    print("="*60)
    print("神经元网格系统 - 终端已启动")
    print("="*60)
    
    while True:
        try:
            qwe1 = []
            text = input("\n输入文本: ")
            
            # 转换文本为二进制（只保留前8位）
            print("\n文本转二进制（只保留前8位）:")
            print("-"*60)
            for char in text:
                encoded = char.encode("utf-8")
                # 每个字节转8位二进制，然后只保留前8位
                bin_str = ''.join(f'{byte:08b}' for byte in encoded)
                bin_8 = bin_str[:8]  # 只保留前8位
                print(f"'{char}' -> {bin_8}")
                qwe1.append(bin_8)
            print("-"*60)
            

            
            # 重新渲染
            rendered_grid_1 = render_diamond_light(light_sources_1, GRID_SIZE)
            rendered_grid_2 = render_diamond_light(light_sources_2, GRID_SIZE)
            rendered_grid_3 = render_diamond_light(light_sources_3, GRID_SIZE)
            rendered_grid_4 = render_diamond_light(light_sources_4, GRID_SIZE)
            rendered_grid_5 = render_diamond_light(light_sources_5, GRID_SIZE)
            
            # 执行退火与绑定
            if qwe1:
                qwe3 = process_annealing_and_binding(qwe1, qwe3)

            # ---------连接逻辑------------
            light_sources_1




            print(f"\n休眠 {TERMINAL_SLEEP_SECONDS} 秒...")
            time.sleep(TERMINAL_SLEEP_SECONDS)
            
        except Exception as e:
            print(f"\n终端线程异常: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(30)


# ==================== GUI 相关 ====================
CELL_SIZE = 4                     # 每个格子像素大小
CANVAS_SIZE = GRID_SIZE * CELL_SIZE  # Canvas大小
REFRESH_MS = 100                  # 刷新间隔(毫秒)
WINDOW_SPACING = 20               # 窗口间距
SEPARATOR_WIDTH = 2               # 分隔线宽度


def create_grid_rectangles(canvas, origin_x, origin_y, grid_size=GRID_SIZE, cell_size=CELL_SIZE):
    """
    创建网格矩形
    参数：
        canvas: Tkinter Canvas对象
        origin_x: 原点X坐标
        origin_y: 原点Y坐标
        grid_size: 网格大小
        cell_size: 格子大小
    返回：
        二维矩形对象列表
    """
    rects = []
    for y in range(grid_size):
        row_rects = []
        for x in range(grid_size):
            rect = canvas.create_rectangle(
                origin_x + x * cell_size, origin_y + y * cell_size,
                origin_x + (x + 1) * cell_size, origin_y + (y + 1) * cell_size,
                fill="#FFFFFF", outline=""
            )
            row_rects.append(rect)
        rects.append(row_rects)
    return rects


class RedStackedWindow:
    """红色堆叠窗口：显示5层神经元分布"""
    
    def __init__(self, master):
        self.master = master
        self.master.title("神经元分布")
        self.master.configure(bg='white')
        self.master.resizable(False, False)
        
        total_height = CANVAS_SIZE * 5
        self.canvas = tk.Canvas(
            master,
            width=CANVAS_SIZE,
            height=total_height,
            bg='white',
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack(padx=0, pady=0)
        
        # 创建5层网格
        self.rects = []
        for layer in range(5):
            y_offset = layer * CANVAS_SIZE
            layer_rects = create_grid_rectangles(self.canvas, 0, y_offset)
            self.rects.append(layer_rects)
        
        self.master.update_idletasks()
        self.master.geometry(f"{CANVAS_SIZE}x{total_height}")
    
    def draw(self):
        """绘制更新网格"""
        try:
            self.master.winfo_exists()
        except TclError:
            return
        
        grids = [rendered_grid_1, rendered_grid_2, rendered_grid_3, rendered_grid_4, rendered_grid_5]
        for layer in range(5):
            grid = grids[layer]
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    val = grid[y * GRID_SIZE + x]
                    color = "#FFFFFF" if val == 0 else f"#{min(val*20,255):02x}0000"
                    self.canvas.itemconfig(self.rects[layer][y][x], fill=color)


class GreenIndependentWindow:
    """绿色独立窗口：显示等待分配区"""
    
    def __init__(self, master):
        self.master = master
        self.master.title("等待分配区")
        self.master.configure(bg='white')
        self.master.resizable(False, False)
        
        total_height = CANVAS_SIZE * 5 + 2 * SEPARATOR_WIDTH
        self.main_canvas = tk.Canvas(
            master,
            width=CANVAS_SIZE,
            height=total_height,
            bg='white',
            highlightthickness=0,
            borderwidth=0
        )
        self.main_canvas.pack(padx=0, pady=0)
        
        # 绘制分隔线
        for i in range(1, 5):
            y_line = i * CANVAS_SIZE + (i - 1) * SEPARATOR_WIDTH
            self.main_canvas.create_line(
                0, y_line, CANVAS_SIZE, y_line,
                fill="#DDDDDD", width=SEPARATOR_WIDTH
            )
        
        # 创建5层网格
        self.rects = []
        for grid_idx in range(5):
            y_offset = grid_idx * (CANVAS_SIZE + SEPARATOR_WIDTH)
            grid_rects = create_grid_rectangles(self.main_canvas, 0, y_offset)
            self.rects.append(grid_rects)
        
        self.master.update_idletasks()
        self.master.geometry(f"{CANVAS_SIZE}x{total_height}")
    
    def draw(self):
        """绘制更新网格"""
        try:
            self.master.winfo_exists()
        except TclError:
            return
        
        sources = [light_sources_1, light_sources_2, light_sources_3, light_sources_4, light_sources_5]
        for grid_idx, source in enumerate(sources):
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    idx = y * GRID_SIZE + x
                    item = source[idx]
                    is_brightness_1 = isinstance(item, Point) and item.brightness == 1
                    color = "#00C800" if is_brightness_1 else "#FFFFFF"
                    self.main_canvas.itemconfig(self.rects[grid_idx][y][x], fill=color)


def gui_main():
    """GUI主函数"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建红色堆叠窗口
    top_red = tk.Toplevel(root)
    top_red.protocol("WM_DELETE_WINDOW", lambda: None)
    start_x, start_y = 150, 80
    red_window = RedStackedWindow(top_red)
    top_red.geometry(f"+{start_x}+{start_y}")
    
    # 创建绿色独立窗口
    top_green = tk.Toplevel(root)
    top_green.protocol("WM_DELETE_WINDOW", lambda: None)
    green_y = start_y + CANVAS_SIZE * 5 + WINDOW_SPACING
    green_window = GreenIndependentWindow(top_green)
    top_green.geometry(f"+{start_x}+{green_y}")
    
    def refresh():
        """定时刷新函数"""
        try:
            root.winfo_exists()
            red_window.draw()
            green_window.draw()
            root.after(REFRESH_MS, refresh)
        except TclError:
            return
    
    # 开始刷新
    refresh()
    root.mainloop()


# ==================== 程序入口 ====================
if __name__ == "__main__":
    print("启动神经元网格系统...")
    
    # 启动终端线程
    terminal_thread = threading.Thread(target=terminal_loop, daemon=True)
    terminal_thread.start()
    
    # 启动GUI主线程
    gui_main()
