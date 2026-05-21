# app.py 全面重写实施计划

## 1. 重写范围

完全重写 [app.py](file:///c:/Users/Administrator/Desktop/Alice%20McCord/app.py)，严格遵循以下规范：
- 所有变量名、函数名、参数名使用英文全称，禁止任何缩写
- 所有魔法数字定义为全局常量
- grid_1~grid_5 改为 grid_layer_1~grid_layer_5
- 所有函数添加类型注解和文档字符串
- 日志格式：`[ModuleName] message`

---

## 2. 全局常量定义

放在文件最顶部（import 之后、Point 类之前）：

```python
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
```

所有代码中用到的魔法数字（32、1024、9、4、3 等）必须替换为对应常量。

---

## 3. Point 类重写

```python
class Point:
    """32x32 grid node class.
    
    Attributes:
        center_index: flat index within grid (0 ~ TOTAL_CELLS-1)
        brightness: current brightness value (0 ~ MAX_BRIGHTNESS)
        control_ports: list of connection dictionaries
        input_ports: list of connection dictionaries
        output_ports: list of connection dictionaries
    """
    def __init__(self, center_index: int, brightness: int,
                 control_ports: list | None = None,
                 input_ports: list | None = None,
                 output_ports: list | None = None):
        self.center_index = center_index
        self.brightness = brightness
        self.control_ports = [] if control_ports is None else control_ports
        self.input_ports = [] if input_ports is None else input_ports
        self.output_ports = [] if output_ports is None else output_ports
```

**端口连接字典格式**（变更为使用 `port_type` 替代原 `port_identifier`，移除 `block_name`）：

```python
{
    "source_point_index": int,   # 源Point索引
    "target_point_index": int,   # 目标Point索引
    "signal": int,               # 信号值
    "port_type": str             # "control" / "input" / "output"
}
```

---

## 4. 函数清单与详细逻辑

### 4.1 `build_random_pool(binary_string_list: list) -> list`
- 输入：每个字符串长度为 GRID_SIDE_LENGTH(32)
- 取每个字符串的前 `RANDOM_POOL_GROUPS × BINARY_GROUP_BITS = 28` 位
- 每组 `BINARY_GROUP_BITS(4)` 位求和，得 0~4 的整数
- 每个字符串产生 `RANDOM_POOL_GROUPS(7)` 个值
- 返回值长度 = `len(binary_string_list) × 7`

### 4.2 `detect_active_points(grid: list) -> list`
- 返回所有 `isinstance(item, Point) and item.brightness == ACTIVE_BRIGHTNESS` 的 `(index, brightness)` 列表

### 4.3 `detect_all_points(grid: list) -> list`
- 返回所有 `isinstance(item, Point)` 的 `(index, brightness)` 列表（不限亮度值）

### 4.4 `clear_non_point_brightness(grid: list) -> list`
- 遍历网格，非 Point 位置置为 0

### 4.5 `diamond_render_single_point(grid: list, point_index: int, source_brightness: int) -> list`
- 以 point_index 为中心，曼哈顿距离 `< source_brightness` 的范围
- `computed_brightness = source_brightness - manhattan_distance`
- Point：`brightness = min(max(原brightness, computed_brightness), MAX_BRIGHTNESS)`
- 非Point：`value = min(max(原value, computed_brightness), MAX_BRIGHTNESS)`
- **绝不覆盖 Point 对象**

### 4.6 `render_grid(grid: list, active_points: list) -> list`
- 对活跃点列表逐一调用 `diamond_render_single_point`

### 4.7 `anneal_and_connect(grid: list, active_points: list, random_pool: list, grid_name: str) -> list`
逐个活跃点处理：
1. **退火减法**：范围 `manhattan_distance <= source_brightness`，`computed_change = -(source_brightness - manhattan_distance)`，修改亮度（≥0），若有变化则设 `block_modified_flag = True`
2. **连接建立**（仅 `block_modified_flag==True`）：
   - 四个方向（下 +32、上 -32、左 -1、右 +1）
   - 条件：`random_pool[point_index] == 1`
   - 累加连续3个 `random_pool[point_index + k] < 4` 的次数（k=0,1,2）：
     - **1** → **信号连接（signal）**：主动端加 `output_ports`，目标端加 `input_ports`（双向）
     - **2** → **控制连接（control）**：主动端加 `output_ports`，目标端加 `control_ports`（双向）
     - 其他 → 默认 control
   - 双方对应端口数 `< MAX_PORTS_PER_TYPE(9)` 才建立
   - 连接字典包含：`source_point_index`, `target_point_index`, `signal=0`, `port_type`
3. **连接后检查**：若三种端口数均 `== MAX_PORTS_PER_TYPE(9)`，设 `brightness = ACTIVE_BRIGHTNESS(9)`
4. **重渲染**：若 `brightness > 0`，调用 `diamond_render_single_point`

### 4.8 `preload_next_grid(source_grid: list, target_grid: list, active_points: list) -> list`
- 菱形扩散到目标网格前3行（`row_y < 3`），逻辑同渲染（加法、max、cap 9）

### 4.9 `determine_movement_direction(grid: list, point_index: int) -> int`
**重要变更**：逻辑与当前实现不同。
1. 获取自身 brightness：`self_brightness = grid[point_index].brightness`
2. 检查四个方向邻居信号强度：
   - 邻居为 Point → 取 `neighbor.brightness`
   - 邻居为数字 → 取该数字值
   - 越界 → 跳过
   - 目标位置已有 Point → 跳过
3. 在可移动方向中选出信号值最大的
4. 若 `max_signal > self_brightness` → 返回目标索引，否则 -1
5. 多方向相同信号：按优先级 下 > 右 > 上 > 左

### 4.10 `update_connections_after_move(grid: list, grid_name: str, old_index: int, new_index: int) -> None`
- 遍历网格中所有 Point 的所有端口列表，更新引用 `old_index` 的 `source_point_index` 或 `target_point_index`

### 4.11 `execute_movement_phase(grid_layer_1: list, grid_layer_2: list, grid_layer_3: list, grid_layer_4: list, grid_layer_5: list) -> tuple`
- 5层依次处理，每层：`detect_all_points` → 逐索引遍历 → 判定方向 → 移动 → 更新连接
- `moved_to_indices` 集合防重处理

### 4.12 `transistor_style_signal_propagation(grid_layer_1~5) -> tuple`
**核心变更**：替代原 `propagate_signals`，全新的三极管式信号传导。
- **严格顺序**：`grid_layer_1 → grid_layer_2 → grid_layer_3 → grid_layer_4 → grid_layer_5`
- **层内顺序**：从上到下、从左到右（索引 0→1023）
- **仅处理 Point 对象**
- 对每个 Point 执行 7 步：

| 步骤 | 操作 |
|------|------|
| 1 | 收集 `input_ports` 中 `signal > 0` 的值 |
| 2 | 检查 `control_ports` 中是否有 `signal > CONTROL_SIGNAL_THRESHOLD(1)`；若有 → 清零 control 信号 → 清零 input 信号 → **直接跳到下一个节点** |
| 3 | 若无控制信号，取输入信号最大值 → `output_signal`；遍历 `output_ports`，设 `signal = output_signal`；找到目标节点对应接收端口（input 或 control），更新 signal；同步目标 brightness = `min(max(原brightness, output_signal), MAX_BRIGHTNESS)` |
| 4 | 清零自身 `output_ports` 中所有 signal |
| 5 | 清零自身 `control_ports` 中所有 signal |
| 6 | 清零自身 `input_ports` 中所有 signal |
| - | **绝不删除节点连接** |

### 4.13 `initialize_api_ports(grid_layer_1: list, grid_layer_5: list) -> tuple`
- `grid_layer_1[0:32]`：创建 brightness=0 的 Point
- `grid_layer_5[992:1024]`：创建 brightness=0 的 Point

### 4.14 `set_api_input(grid_layer_1: list, binary_string: str) -> bool`
- 写入32位二进制到 grid_layer_1 第一行
- input_ports 添加记录：`source=-1, target=port_index, signal=9/0, port_type="input"`
- 设 brightness = signal_value

### 4.15 `get_api_output(grid_layer_5: list) -> str`
- 读取末行，brightness>=5→1，<5→0，拼32位二进制
- 每8位字节解码 UTF-8，失败返回二进制串

### 4.16 `display_grid(grid: list, grid_name: str) -> None`
- 按 32×32 打印，Point 打 brightness，非 Point 打数字值

---

## 5. 全局变量初始化

```python
grid_layer_1 = [0] * TOTAL_CELLS
grid_layer_2 = [0] * TOTAL_CELLS
grid_layer_3 = [0] * TOTAL_CELLS
grid_layer_4 = [0] * TOTAL_CELLS
grid_layer_5 = [0] * TOTAL_CELLS
```

**种子点**（索引30~39放10个 brightness=4 的Point，center_index = i+30）：
```python
for i in range(10):
    grid_layer_1[i + 30] = Point(center_index=i + 30, brightness=SEED_BRIGHTNESS)
# ... grid_layer_2~5 同理
```

**API端口**：调用 `initialize_api_ports(grid_layer_1, grid_layer_5)`

---

## 6. 主循环阶段顺序

```
阶段A: 输入处理 → build_random_pool + set_api_input（两份相同的二进制副本）
阶段B: 活跃点检测 → detect_active_points ×5
阶段C: 菱形渲染 → render_grid ×5
阶段D: 退火+连接 → anneal_and_connect ×5
阶段E: 清理非Point亮度 → clear_non_point_brightness ×5
阶段F: 跨层预加载 → preload_next_grid (1→2, 2→3, 3→4, 4→5)
阶段G: 节点移动 → execute_movement_phase
阶段H: 信号传导 → transistor_style_signal_propagation
阶段I: 显示网格 → display_grid ×5
阶段J: API输出 → get_api_output
阶段K: 循环下一轮
```

**关键顺序变更**：移动(G)在信号传导(H)之前，信号传导后所有signal归零。

---

## 7. 输入处理（阶段A）详细

1. `user_input = input("input:")`
2. 逐字符：`character.encode("utf-8")` → 8位二进制拼接 → `ljust(32, '0')[:32]`
3. 生成两份相同的二进制副本：
   - 一份全量 `binary_string_list` → `build_random_pool(binary_string_list)`
   - 取第一份 `binary_string_list[0]` → `set_api_input(grid_layer_1, api_input_string)`

---

## 8. 需要删除/移除的内容

- 删除 `import inspect`（不再需要）
- 删除原 `propagate_signals` 函数
- 删除 `/ ====================================================` 空行占位
- 删除主循环中 `for i in range(len(grid_1)): if inspect.isclass(...)` 调试代码
- 移除所有连接字典中的 `block_name` 字段
- 将 `port_identifier` 改为 `port_type`

---

## 9. 文件最终结构

```
# -*- coding: utf-8 -*-
# 全局常量 (10个)
# Point 类定义
# build_random_pool
# detect_active_points
# detect_all_points
# update_connections_after_move (移到这里，因为execute需要引用)
# determine_movement_direction
# clear_non_point_brightness
# diamond_render_single_point
# render_grid
# anneal_and_connect
# preload_next_grid
# execute_movement_phase
# transistor_style_signal_propagation
# initialize_api_ports
# set_api_input
# get_api_output
# display_grid
# 全局变量初始化
# 种子点放置
# API端口初始化
# 主循环
```

**注意**：`update_connections_after_move` 必须在 `execute_movement_phase` 之前定义，`determine_movement_direction` 也必须在 `execute_movement_phase` 之前。

---

## 10. 实施步骤

### 步骤1：定义全局常量
### 步骤2：重写 Point 类
### 步骤3：实现 build_random_pool（7组）
### 步骤4：实现 detect_active_points
### 步骤5：实现 detect_all_points
### 步骤6：实现 clear_non_point_brightness
### 步骤7：实现 diamond_render_single_point
### 步骤8：实现 render_grid
### 步骤9：实现 anneal_and_connect（新连接类型映射：1→signal, 2→control）
### 步骤10：实现 preload_next_grid
### 步骤11：实现 determine_movement_direction（新逻辑：比较自身亮度）
### 步骤12：实现 update_connections_after_move
### 步骤13：实现 execute_movement_phase
### 步骤14：实现 transistor_style_signal_propagation（全新，替代原propagate_signals）
### 步骤15：实现 initialize_api_ports
### 步骤16：实现 set_api_input（使用 port_type 替代 port_identifier）
### 步骤17：实现 get_api_output
### 步骤18：实现 display_grid
### 步骤19：全局变量初始化 + 种子点 + API端口初始化
### 步骤20：主循环（阶段A~K新顺序）
### 步骤21：语法验证