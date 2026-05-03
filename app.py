import inspect
import time
import threading
import tkinter as tk
from tkinter import TclError

# ==================== 全局参数与网格 ====================
GRID_SIZE = 32
qw1 = [0] * (GRID_SIZE * GRID_SIZE)
qw2 = [0] * (GRID_SIZE * GRID_SIZE)
qw3 = [0] * (GRID_SIZE * GRID_SIZE)
qw4 = [0] * (GRID_SIZE * GRID_SIZE)
qw5 = [0] * (GRID_SIZE * GRID_SIZE)

# ==================== 光源Point类 ====================
class Point:
    def __init__(self, center_index, brightness, asd=None, asd1=None, asd2=None):
        self.center_index = center_index
        self.brightness = brightness
        self.asd = [] if asd is None else asd
        self.asd1 = [] if asd1 is None else asd1
        self.asd2 = [] if asd2 is None else asd2

qw1[400] = Point(center_index=400, brightness=9)

# ==================== 菱形光场渲染核心函数 ====================
def render_diamond_light(pw_list, grid_size=32):
    render_buffer = []
    for item in pw_list:
        render_buffer.append(0 if isinstance(item, Point) else item)
    
    for idx, item in enumerate(pw_list):
        if not isinstance(item, Point):
            continue
        center_idx = item.center_index
        light_level = item.brightness
        cx = center_idx % grid_size
        cy = center_idx // grid_size

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
                        render_buffer[target_idx] = min(new_val, 9)
    return render_buffer

# ==================== 初始神经元光源分布 ====================
qwer1 = 0
for i in range(32 // 2):
    qw1[qwer1] = Point(center_index=qwer1, brightness=9)
    qwer1 += 2

qwera1 = 31
for i in range(200):
    if qwera1 >= GRID_SIZE * GRID_SIZE:
        break
    qw1[qwera1] = Point(center_index=qwera1, brightness=1)
    qwera1 += 4

qwera2 = 0
for i in range(200):
    if qwera2 >= GRID_SIZE * GRID_SIZE:
        break
    qw2[qwera2] = Point(center_index=qwera2, brightness=1)
    qwera2 += 5

qwera3 = 0
for i in range(200):
    if qwera3 >= GRID_SIZE * GRID_SIZE:
        break
    qw3[qwera3] = Point(center_index=qwera3, brightness=1)
    qwera3 += 5

qwera4 = 0
for i in range(200):
    if qwera4 >= GRID_SIZE * GRID_SIZE:
        break
    qw4[qwera4] = Point(center_index=qwera4, brightness=1)
    qwera4 += 5

qwera5 = 0
for i in range(200):
    if qwera5 >= GRID_SIZE * GRID_SIZE:
        break
    qw5[qwera5] = Point(center_index=qwera5, brightness=1)
    qwera5 += 5

final_grid1 = render_diamond_light(qw1, GRID_SIZE)
final_grid2 = render_diamond_light(qw2, GRID_SIZE)
final_grid3 = render_diamond_light(qw3, GRID_SIZE)
final_grid4 = render_diamond_light(qw4, GRID_SIZE)
final_grid5 = render_diamond_light(qw5, GRID_SIZE)

# ==================== 终端打印辅助函数 ====================
def print_grid(grid, title, grid_size=32):
    print(f"========== {title} ==========")
    for i in range(0, grid_size * grid_size, grid_size):
        print(grid[i:i+grid_size])

# ==================== 后台终端输入线程 ====================
def terminal_loop():
    global final_grid1, final_grid2, final_grid3, final_grid4, final_grid5
    while True:
        try:
            a1 = input("输入文本: ")
            a2 = list(a1)
            for char in a2:
                a1_encoded = char.encode("utf-8")
                bin_str = ''.join(f'{byte:08b}' for byte in a1_encoded)
                bin_32 = bin_str.ljust(32, '0')[:32]
                print(f"'{char}' -> {bin_32}")
            
            aqw1 = [z1 for z1 in range(len(qw1)) if isinstance(qw1[z1], Point) and qw1[z1].brightness == 1]
            aqw2 = [z2 for z2 in range(len(qw2)) if isinstance(qw2[z2], Point) and qw2[z2].brightness == 1]
            aqw3 = [z3 for z3 in range(len(qw3)) if isinstance(qw3[z3], Point) and qw3[z3].brightness == 1]
            aqw4 = [z4 for z4 in range(len(qw4)) if isinstance(qw4[z4], Point) and qw4[z4].brightness == 1]
            aqw5 = [z5 for z5 in range(len(qw5)) if isinstance(qw5[z5], Point) and qw5[z5].brightness == 1]

            print(f"========== 1 ==========")
            for i in range(0, len(aqw1), 24):
                print(aqw1[i:i+24])
            print(f"========== 2 ==========")
            for i in range(0, len(aqw2), 24):
                print(aqw2[i:i+24])
            print(f"========== 3 ==========")
            for i in range(0, len(aqw3), 24):
                print(aqw3[i:i+24])
            print(f"========== 4 ==========")
            for i in range(0, len(aqw4), 24):
                print(aqw4[i:i+24])
            print(f"========== 5 ==========")
            for i in range(0, len(aqw5), 24):
                print(aqw5[i:i+24])
            
            final_grid1 = render_diamond_light(qw1, GRID_SIZE)
            final_grid2 = render_diamond_light(qw2, GRID_SIZE)
            final_grid3 = render_diamond_light(qw3, GRID_SIZE)
            final_grid4 = render_diamond_light(qw4, GRID_SIZE)
            final_grid5 = render_diamond_light(qw5, GRID_SIZE)
            time.sleep(30)
        except Exception as e:
            print(f"终端线程异常: {e}")
            time.sleep(1)

# ==================== GUI 常量配置 ====================
CELL_SIZE = 4
CANVAS_SIZE = GRID_SIZE * CELL_SIZE   # 128
REFRESH_MS = 100
WINDOW_SPACING = 20

# ==================== 红色堆叠光场窗口 ====================
class RedStackedWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("◇ 红色叠层光场 (Grid1 顶 ⇢ Grid5 底)")
        self.master.configure(bg='white')
        self.master.resizable(False, False)

        total_height = CANVAS_SIZE * 5
        self.canvas = tk.Canvas(master, width=CANVAS_SIZE, height=total_height,
                                bg='white', highlightthickness=0, borderwidth=0)
        self.canvas.pack(padx=0, pady=0)

        # 顺序：Grid1 在最顶层 (layer=0)，Grid5 在最底层 (layer=4)
        grids = [final_grid1, final_grid2, final_grid3, final_grid4, final_grid5]
        self.rects = []
        for layer in range(5):
            layer_rects = []
            y_offset = layer * CANVAS_SIZE
            for y in range(GRID_SIZE):
                row_rects = []
                for x in range(GRID_SIZE):
                    rect = self.canvas.create_rectangle(
                        x * CELL_SIZE, y_offset + y * CELL_SIZE,
                        (x+1) * CELL_SIZE, y_offset + (y+1) * CELL_SIZE,
                        fill="#FFFFFF", outline=""
                    )
                    row_rects.append(rect)
                layer_rects.append(row_rects)
            self.rects.append(layer_rects)

        self.master.update_idletasks()
        self.master.geometry(f"{CANVAS_SIZE}x{total_height}")

    def draw(self):
        try:
            self.master.winfo_exists()
        except TclError:
            return
        grids = [final_grid1, final_grid2, final_grid3, final_grid4, final_grid5]
        for layer in range(5):
            grid = grids[layer]
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    val = grid[y * GRID_SIZE + x]
                    color = "#FFFFFF" if val == 0 else f"#{min(val*20,255):02x}0000"
                    self.canvas.itemconfig(self.rects[layer][y][x], fill=color)

# ==================== 绿色独立光场窗口 ====================
class GreenIndependentWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("◎ 绿色独立光场 (Grid1 顶 ⇢ Grid5 底)")
        self.master.configure(bg='white')
        self.master.resizable(False, False)

        total_height = CANVAS_SIZE * 5 + 2 * 4
        self.main_canvas = tk.Canvas(master, width=CANVAS_SIZE, height=total_height,
                                     bg='white', highlightthickness=0, borderwidth=0)
        self.main_canvas.pack(padx=0, pady=0)

        # 浅灰色分割线
        for i in range(1, 5):
            y_line = i * CANVAS_SIZE + (i-1) * 2
            self.main_canvas.create_line(0, y_line, CANVAS_SIZE, y_line,
                                         fill="#DDDDDD", width=2)

        grids = [final_grid1, final_grid2, final_grid3, final_grid4, final_grid5]
        self.rects = []
        for grid_idx in range(5):
            grid_rects = []
            y_offset = grid_idx * (CANVAS_SIZE + 2)
            for y in range(GRID_SIZE):
                row_rects = []
                for x in range(GRID_SIZE):
                    rect = self.main_canvas.create_rectangle(
                        x * CELL_SIZE, y_offset + y * CELL_SIZE,
                        (x+1) * CELL_SIZE, y_offset + (y+1) * CELL_SIZE,
                        fill="#FFFFFF", outline=""
                    )
                    row_rects.append(rect)
                grid_rects.append(row_rects)
            self.rects.append(grid_rects)

        self.master.update_idletasks()
        self.master.geometry(f"{CANVAS_SIZE}x{total_height}")

    def draw(self):
        try:
            self.master.winfo_exists()
        except TclError:
            return
        grids = [final_grid1, final_grid2, final_grid3, final_grid4, final_grid5]
        for grid_idx, grid in enumerate(grids):
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    val = grid[y * GRID_SIZE + x]
                    color = "#00C800" if val >= 1 else "#FFFFFF"
                    self.main_canvas.itemconfig(self.rects[grid_idx][y][x], fill=color)

# ==================== GUI 主程序 ====================
def gui_main():
    root = tk.Tk()
    root.withdraw()

    top_red = tk.Toplevel(root)
    top_red.protocol("WM_DELETE_WINDOW", lambda: None)
    start_x, start_y = 150, 80
    red_window = RedStackedWindow(top_red)
    top_red.geometry(f"+{start_x}+{start_y}")

    top_green = tk.Toplevel(root)
    top_green.protocol("WM_DELETE_WINDOW", lambda: None)
    green_y = start_y + CANVAS_SIZE * 5 + WINDOW_SPACING
    green_window = GreenIndependentWindow(top_green)
    top_green.geometry(f"+{start_x}+{green_y}")

    def refresh():
        try:
            root.winfo_exists()
            red_window.draw()
            green_window.draw()
            root.after(REFRESH_MS, refresh)
        except TclError:
            return

    refresh()
    root.mainloop()

if __name__ == "__main__":
    terminal_thread = threading.Thread(target=terminal_loop, daemon=True)
    terminal_thread.start()
    gui_main()