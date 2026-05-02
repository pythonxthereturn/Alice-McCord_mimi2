import inspect



GRID_SIZE = 32
qw1 = [0] * (GRID_SIZE * GRID_SIZE)  # 一次性初始化1024个0，和你循环append效果完全一致
qw2 = [0] * (GRID_SIZE * GRID_SIZE)
qw3 = [0] * (GRID_SIZE * GRID_SIZE)
qw4 = [0] * (GRID_SIZE * GRID_SIZE)
qw5 = [0] * (GRID_SIZE * GRID_SIZE)

























# ===================== 2. 修复后的Point类（解决默认参数坑，保留你要的所有属性） =====================
class Point:
    def __init__(self, center_index, brightness, asd=None, asd1=None, asd2=None):
        self.center_index = center_index
        self.brightness = brightness
        # 修复可变默认参数坑，每个实例独立生成列表
        self.asd = [] if asd is None else asd    # 控制
        self.asd1 = [] if asd1 is None else asd1 # 输入
        self.asd2 = [] if asd2 is None else asd2 # 输出

# ===================== 3. 给qw添加你要的光源（这里放的Point，渲染函数会100%识别到） =====================
# 你原来的亮度9的核心光源，放在qw[400]
qw1[400] = Point(center_index=400, brightness=9)
# 可以随便加多个光源测试，比如：
# qw[200] = Point(center_index=200, brightness=5)













# ===================== 4. 核心菱形渲染函数（保留原始值，最大不超过9） =====================
def render_diamond_light(pw_list, grid_size=32):
    # 先复制原始值作为基础
    render_buffer = []
    for item in pw_list:
        if isinstance(item, Point):
            render_buffer.append(0)
        else:
            render_buffer.append(item)

    # 遍历整个列表，找所有Point类的光源
    for idx, item in enumerate(pw_list):
        if not isinstance(item, Point):
            continue
        
        center_idx = item.center_index
        light_level = item.brightness
        cx = center_idx % grid_size
        cy = center_idx // grid_size

        # 菱形扩散逻辑
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
                    # 只替换更大的值，但不超过9
                    if new_val > render_buffer[target_idx]:
                        render_buffer[target_idx] = min(new_val, 9)
    
    return render_buffer


qwer1 = 0
for i in range(32 // 2):
    qw1[qwer1] = Point(center_index=qwer1, brightness=9)
    qwer1 += 2







# ===================== 5. 执行渲染并打印所有5个格子 =====================
final_grid1 = render_diamond_light(qw1, GRID_SIZE)
final_grid2 = render_diamond_light(qw2, GRID_SIZE)
final_grid3 = render_diamond_light(qw3, GRID_SIZE)
final_grid4 = render_diamond_light(qw4, GRID_SIZE)
final_grid5 = render_diamond_light(qw5, GRID_SIZE)

def print_grid(grid, title, grid_size=32):
    print(f"========== {title} ==========")
    for i in range(0, grid_size * grid_size, grid_size):
        print(grid[i:i+grid_size])

print_grid(final_grid1, "final_grid1 (最底层)")
print_grid(final_grid2, "final_grid2")
print_grid(final_grid3, "final_grid3")
print_grid(final_grid4, "final_grid4")
print_grid(final_grid5, "final_grid5 (最顶层)")















while True:
    a1 = input("输入文本: ")
    a2 = list(a1)
    for char in a2:
        a1_encoded = char.encode("utf-8")
        bin_str = ''.join(f'{byte:08b}' for byte in a1_encoded)
        bin_32 = bin_str.ljust(32, '0')[:32]
        print(f"'{char}' -> {bin_32}")










