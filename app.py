# ===================== 1. 初始化32×32的qw列表（统一用你最开始的qw，删掉冗余的pw） =====================





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













# ===================== 4. 核心菱形渲染函数（完全保留你的原逻辑，只做稳定性优化） =====================
def render_diamond_light(pw_list, grid_size=32):
    # 新建渲染缓冲，不破坏原qw里的Point对象，不会渲染一次就把类覆盖成数字
    render_buffer = [0] * (grid_size * grid_size)

    # 遍历整个列表，找所有Point类的光源
    for idx, item in enumerate(pw_list):
        # 核心判断：当前元素是不是Point类，不是就跳过
        if not isinstance(item, Point):
            continue
        
        # 是Point类，自动读取中心位置和亮度，执行渲染
        center_idx = item.center_index
        light_level = item.brightness
        cx = center_idx % grid_size
        cy = center_idx // grid_size

        # 你的原菱形扩散逻辑（曼哈顿距离）完全保留
        for dy in range(-light_level, light_level + 1):
            for dx in range(-light_level, light_level + 1):
                dist = abs(dx) + abs(dy)
                if dist >= light_level:
                    continue
                
                nx = cx + dx
                ny = cy + dy
                # 边界判断，不超出32×32网格
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    target_idx = ny * grid_size + nx
                    # 多光源取最大亮度，想叠加亮度就把max改成+=
                    render_buffer[target_idx] = max(render_buffer[target_idx], light_level - dist)
    
    return render_buffer











# ===================== 5. 执行渲染 + 纵向堆叠打印5个32×32格子 =====================
final_grid1 = render_diamond_light(qw1, GRID_SIZE)
final_grid2 = render_diamond_light(qw2, GRID_SIZE)
final_grid3 = render_diamond_light(qw3, GRID_SIZE)
final_grid4 = render_diamond_light(qw4, GRID_SIZE)
final_grid5 = render_diamond_light(qw5, GRID_SIZE)

print("========== final_grid1 (最底层) ==========")
for i in range(0, 32*32, GRID_SIZE):
    print(final_grid1[i:i+GRID_SIZE])

print("\n========== final_grid2 ==========")
for i in range(0, 32*32, GRID_SIZE):
    print(final_grid2[i:i+GRID_SIZE])

print("\n========== final_grid3 ==========")
for i in range(0, 32*32, GRID_SIZE):
    print(final_grid3[i:i+GRID_SIZE])

print("\n========== final_grid4 ==========")
for i in range(0, 32*32, GRID_SIZE):
    print(final_grid4[i:i+GRID_SIZE])

print("\n========== final_grid5 (最顶层) ==========")
for i in range(0, 32*32, GRID_SIZE):
    print(final_grid5[i:i+GRID_SIZE])