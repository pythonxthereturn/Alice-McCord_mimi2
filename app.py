import inspect
import time
import threading
import tkinter as tk
from tkinter import TclError

GRID_SIZE = 32
TOTAL_CELLS = GRID_SIZE * GRID_SIZE

light_sources_1 = [0] * TOTAL_CELLS
light_sources_2 = [0] * TOTAL_CELLS
light_sources_3 = [0] * TOTAL_CELLS
light_sources_4 = [0] * TOTAL_CELLS
light_sources_5 = [0] * TOTAL_CELLS

MAX_BRIGHTNESS = 9
STAGGERED_POINT_COUNT = 200
POSITIONS_CHUNK_SIZE = 24
TERMINAL_SLEEP_SECONDS = 30

class Point:
    def __init__(self, center_index, brightness):
        self.center_index = center_index
        self.brightness = brightness

light_sources_1[400] = Point(center_index=400, brightness=9)

def render_diamond_light(source_list, grid_size=GRID_SIZE):
    render_buffer = []
    for item in source_list:
        render_buffer.append(0 if isinstance(item, Point) else item)

    for idx, item in enumerate(source_list):
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
                        render_buffer[target_idx] = min(new_val, MAX_BRIGHTNESS)
    return render_buffer

def create_staggered_points(target_list, start, step, count, grid_size=GRID_SIZE):
    idx = start
    for _ in range(count):
        if idx >= grid_size * grid_size:
            break
        target_list[idx] = Point(center_index=idx, brightness=1)
        idx += step

idx = 0
for _ in range(GRID_SIZE // 2):
    light_sources_1[idx] = Point(center_index=idx, brightness=9)
    idx += 2

create_staggered_points(light_sources_1, 31, 4, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_2, 0, 5, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_3, 0, 5, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_4, 0, 5, STAGGERED_POINT_COUNT)
create_staggered_points(light_sources_5, 0, 5, STAGGERED_POINT_COUNT)

rendered_grid_1 = render_diamond_light(light_sources_1, GRID_SIZE)
rendered_grid_2 = render_diamond_light(light_sources_2, GRID_SIZE)
rendered_grid_3 = render_diamond_light(light_sources_3, GRID_SIZE)
rendered_grid_4 = render_diamond_light(light_sources_4, GRID_SIZE)
rendered_grid_5 = render_diamond_light(light_sources_5, GRID_SIZE)

def handle_terminal_input():
    text = input("输入文本: ")
    for char in text:
        encoded = char.encode("utf-8")
        bin_str = ''.join(f'{byte:08b}' for byte in encoded)
        bin_32 = bin_str.ljust(32, '0')[:32]
        print(f"'{char}' -> {bin_32}")
#




def collect_brightness_1_positions(source_list):
    return [idx for idx, item in enumerate(source_list)
        if isinstance(item, Point) and item.brightness == 1]
#
def print_positions_block(title, positions, chunk_size=POSITIONS_CHUNK_SIZE):
    print(f"========== {title} ==========")
    for i in range(0, len(positions), chunk_size):
        print(positions[i:i + chunk_size])
#

def terminal_loop():
    global rendered_grid_1, rendered_grid_2, rendered_grid_3, rendered_grid_4, rendered_grid_5
    all_sources = [light_sources_1, light_sources_2, light_sources_3, light_sources_4, light_sources_5]

    while True:
        try:
            handle_terminal_input()

            for i, src in enumerate(all_sources, start=1):
                positions = collect_brightness_1_positions(src)
                print_positions_block(str(i), positions)

            rendered_grid_1 = render_diamond_light(light_sources_1, GRID_SIZE)
            rendered_grid_2 = render_diamond_light(light_sources_2, GRID_SIZE)
            rendered_grid_3 = render_diamond_light(light_sources_3, GRID_SIZE)
            rendered_grid_4 = render_diamond_light(light_sources_4, GRID_SIZE)
            rendered_grid_5 = render_diamond_light(light_sources_5, GRID_SIZE)
            time.sleep(TERMINAL_SLEEP_SECONDS)
        except Exception as e:
            print(f"终端线程异常: {e}")
            time.sleep(30)

CELL_SIZE = 4
CANVAS_SIZE = GRID_SIZE * CELL_SIZE
REFRESH_MS = 100
WINDOW_SPACING = 20
SEPARATOR_WIDTH = 2

def create_grid_rectangles(canvas, origin_x, origin_y, grid_size=GRID_SIZE, cell_size=CELL_SIZE):
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
            self.canvas.pack(
                padx=0, 
                pady=0
                )
            )

        self.rects = []
        for layer in range(5):
            y_offset = layer * CANVAS_SIZE
            layer_rects = create_grid_rectangles(self.canvas, 0, y_offset)
            self.rects.append(layer_rects)

        self.master.update_idletasks()
        self.master.geometry(f"{CANVAS_SIZE}x{total_height}")

    def draw(self):
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

        for i in range(1, 5):
            y_line = i * CANVAS_SIZE + (i - 1) * SEPARATOR_WIDTH
            self.main_canvas.create_line(
                0, 
                y_line, 
                CANVAS_SIZE, 
                y_line,
                fill="#DDDDDD", width=SEPARATOR_WIDTH
                )

        self.rects = []
        for grid_idx in range(5):
            y_offset = grid_idx * (CANVAS_SIZE + SEPARATOR_WIDTH)
            grid_rects = create_grid_rectangles(self.main_canvas, 0, y_offset)
            self.rects.append(grid_rects)

        self.master.update_idletasks()
        self.master.geometry(f"{CANVAS_SIZE}x{total_height}")

    def draw(self):
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
