# Point移动与连接更新实施计划

## 1. 概述

在5个独立Grid网格中，新增"Point移动"阶段。核心流程：
1. 遍历全网格找出**所有Point对象**（不限brightness是否等于9或大于9，全部罗列）
2. 对每个Point，依据其上下左右四方邻居的信号数值做直观对比，判定移动方向
3. 将Point完整复制到目标新位置，同步清空原位置
4. **同步更新所有绑定旧位置的输入/输出/控制逻辑参数**（包括自身端口和对方端口中对旧索引的引用）
5. 按顺序逐格逐单元依次执行，确保5个区块全部完成

### 用户强调的关键点
> "之前那个旧的控制输入输出列表中存有对方的相应数据，对方也存储了他的相应数据。当他移动的时候，对方和他自己还存着旧的数据，这些都要进行更新"

即：Point A移动时，不仅要更新A自身端口中`source_point_index`的引用，还要更新**所有其他Point**端口中引用了A旧索引的`target_point_index`（和`source_point_index`）。

---

## 2. 新增函数

### 2.1 `detect_all_points(grid)` — 检测全部Point

```python
def detect_all_points(grid):
    """遍历网格找出所有Point对象，不限亮度值。
    返回: [(point_index, brightness), ...] 按索引升序排列
    """
```

与现有`detect_active_points`的区别：
- 现有函数仅收集`brightness == 9`的Point
- 新函数收集**所有**Point，无论brightness为0、4、9还是其他值

### 2.2 `determine_movement_direction(grid, point_index)` — 判定移动方向

```python
def determine_movement_direction(grid, point_index):
    """依据目标格上下左右四方信号数值做直观对比，判定移动方向。
    返回: 目标位置索引(int)，若无需移动返回-1
    """
```

**判定逻辑**：
1. 获取四个方向的邻居索引：
   - 上: `point_index - 32`
   - 下: `point_index + 32`
   - 左: `point_index - 1`（需检查左边界：`point_index % 32 == 0`时无效）
   - 右: `point_index + 1`（需检查右边界：`point_index % 32 == 31`时无效）

2. 获取每个方向邻居的信号值：
   - 若邻居是Point对象 → 信号值 = `neighbor.brightness`
   - 若邻居是数字 → 信号值 = 该数字
   - 若越界 → 信号值 = -1（标记为不可移动）

3. 可移动性检查：
   - 目标位置已有Point对象 → 该方向不可移动（信号值保留用于对比，但标记为阻塞）
   - 目标位置越界 → 该方向不可移动

4. 对比判定：
   - 在**可移动**的方向中，选取信号值最大的方向
   - 若所有可移动方向的信号值均 ≤ 0，则不移动（返回-1）
   - 若多个方向信号值相同且均为最大，按优先级：下 > 右 > 上 > 左

### 2.3 `update_connections_after_move(grid, grid_name, old_index, new_index)` — 更新全部连接引用

```python
def update_connections_after_move(grid, grid_name, old_index, new_index):
    """Point从old_index移动到new_index后，更新同一网格内所有Point的端口连接引用。
    遍历网格中所有Point的control_ports/input_ports/output_ports，
    将引用old_index的source_point_index或target_point_index更新为new_index。
    """
```

**更新规则**（核心逻辑）：

遍历网格中**每一个Point**的**每一个端口列表**（control_ports, input_ports, output_ports）中的**每一条连接记录**：

| 条件 | 更新操作 |
|------|----------|
| `connection["source_point_index"] == old_index` 且 `connection["block_name"] == grid_name` | → 更新为 `new_index` |
| `connection["target_point_index"] == old_index` 且 `connection["block_name"] == grid_name` | → 更新为 `new_index` |

这覆盖了以下场景：
- **移动Point自身的端口**：自身记录中`source_point_index`指向自己的旧索引 → 更新
- **其他Point的端口**：对方记录中`target_point_index`指向移动Point的旧索引 → 更新
- **API输入端口**：`target_point_index`指向API Point的旧索引 → 更新
- **反向引用**：若其他Point的`source_point_index`因某种原因引用了旧索引 → 也更新

### 2.4 `execute_movement_phase(all_grids)` — 执行全部5个网格的移动阶段

```python
def execute_movement_phase(grid_1, grid_2, grid_3, grid_4, grid_5):
    """对5个网格依次执行Point移动阶段。
    每个网格内：先收集所有Point原始位置，再按索引升序逐个处理。
    返回: (grid_1, grid_2, grid_3, grid_4, grid_5)
    """
```

**执行流程**（每个网格独立执行）：

1. **收集阶段**：调用`detect_all_points(grid)`获取所有Point的原始位置列表
2. **逐个处理**：按原始位置索引升序遍历
   - 检查该位置是否仍有Point（可能被前序移动覆盖）
   - 调用`determine_movement_direction(grid, point_index)`判定方向
   - 若方向有效（返回值≠-1）：
     a. 将Point对象完整复制到目标新位置：`grid[new_index] = grid[old_index]`
     b. 更新Point的`center_index`为新索引：`grid[new_index].center_index = new_index`
     c. 清空原位置：`grid[old_index] = 0`
     d. 调用`update_connections_after_move(grid, grid_name, old_index, new_index)`更新全部连接
3. **下一网格**：重复上述流程

**防重处理**：维护一个`moved_to_indices`集合，记录本轮已移动到的目标位置。遍历时若当前索引在集合中，跳过（避免对已移动的Point重复处理）。

---

## 3. 主循环集成

在现有主循环中，于**阶段G（信号传播）之后、阶段H（显示输出）之前**插入新阶段：

```
阶段A: 清空并处理输入
阶段B: 活跃点检测
阶段C: 菱形渲染（加法）
阶段D: 退火（减法）+ 连接建立
阶段E: 退火后清理
阶段F: 预加载
阶段G: 信号传播
阶段G+: Point移动与连接更新  ← 新增
阶段H: 显示输出
阶段I: API输出
阶段J: 调试信息
```

插入位置选择理由：
- 信号传播已完成，Point的brightness和端口signal值均为最新状态
- 移动后的新位置将在显示阶段呈现
- 移动后的连接更新在下一轮信号传播时生效

---

## 4. 连接更新详细逻辑

### 4.1 连接记录结构回顾

当前每条连接记录的格式：
```python
{
    "block_name": "grid_1",          # 所属网格名
    "port_identifier": "control",    # 端口类型
    "source_point_index": 100,       # 源Point索引
    "target_point_index": 132,       # 目标Point索引
    "signal": 0                      # 信号值
}
```

### 4.2 移动场景示例

**场景**：Grid_1中，Point A从索引100移动到索引132（向下移动一行）

**Point A自身的端口**（移动前）：
```python
# A.control_ports 中可能有：
{"source_point_index": 100, "target_point_index": 132, ...}  # A→B
# A.input_ports 中可能有：
{"source_point_index": 100, "target_point_index": 99, ...}   # A→C (API输入)
```

**Point B（索引132）的端口**（移动前）：
```python
# B.control_ports 中可能有：
{"source_point_index": 132, "target_point_index": 100, ...}  # B→A
```

**更新后**：
- A自身端口：`source_point_index: 100 → 132`
- B的端口：`target_point_index: 100 → 132`
- 所有引用了索引100的连接记录均更新为132

### 4.3 API端口特殊处理

API输入端口（grid_1[0:31]）的连接记录格式：
```python
{"source_point_index": -1, "target_point_index": 5, ...}
```

若API端口Point移动，`target_point_index`也需要更新。`source_point_index`为-1不受影响。

---

## 5. 边界情况处理

| 情况 | 处理方式 |
|------|----------|
| Point在网格边缘（第0行/最后1行/第0列/最后1列） | 越界方向的信号值设为-1，不作为候选方向 |
| 目标位置已有Point | 该方向标记为阻塞，不移动到该位置 |
| 所有方向信号值≤0或全部阻塞 | 不移动，返回-1 |
| 多个方向信号值相同 | 按优先级选择：下 > 右 > 上 > 左 |
| Point移动后新位置被后续遍历到 | 通过`moved_to_indices`集合跳过 |
| 原位置Point已被前序移动覆盖 | 检查`isinstance(grid[old_index], Point)`，若非Point则跳过 |
| API端口Point（grid_1[0:31], grid_5[992:1023]） | 正常参与移动逻辑，连接更新同样适用 |

---

## 6. 实施步骤

### 步骤1：新增`detect_all_points`函数
- 位置：app.py 工具函数区域（`detect_active_points`函数之后）
- 逻辑：遍历grid，收集所有`isinstance(item, Point)`的索引和亮度

### 步骤2：新增`determine_movement_direction`函数
- 位置：app.py 工具函数区域
- 逻辑：四方信号对比 + 可移动性检查 + 方向选择

### 步骤3：新增`update_connections_after_move`函数
- 位置：app.py 工具函数区域
- 逻辑：遍历同一网格所有Point的所有端口，更新引用旧索引的连接记录

### 步骤4：新增`execute_movement_phase`函数
- 位置：app.py 工具函数区域
- 逻辑：5个网格依次执行 → 每个网格内收集Point → 逐个判定移动 → 执行移动+连接更新

### 步骤5：主循环集成
- 位置：app.py 主循环，阶段G之后
- 添加调用：`grid_1, grid_2, grid_3, grid_4, grid_5 = execute_movement_phase(grid_1, grid_2, grid_3, grid_4, grid_5)`
- 添加调试打印

### 步骤6：验证
- 运行程序，输入测试数据
- 检查Point是否按预期移动
- 检查连接记录中的索引是否正确更新
- 检查5个网格是否全部执行完毕
