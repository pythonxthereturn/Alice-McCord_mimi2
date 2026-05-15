# 全量变量重命名与代码整洁优化 Spec

## Why
当前 `app.py` 中存在大量无意义乱码变量名（`ax1`-`ax21`、`qw1`-`qw5`），以及重复使用的临时变量名在多个上下文间混用。代码整体可读性极差，普通人无法理解运行逻辑。需要在**不提取外部函数、不拆分原生逻辑、完全保留 while 循环执行顺序**的前提下，将所有变量名替换为完整规范英文单词（严禁任何缩写），并精简冗余嵌套结构。

## What Changes
- 重命名所有全局变量（`qw1`-`qw5` → `grid_1`-`grid_5`）为有意义英文名
- 重命名所有临时变量（`ax1`-`ax21`）为有意义英文名，同一变量名在不同上下文复用则统一为一个通用语义名
- 重命名循环内局部变量（`cx`, `cy`, `nx`, `ny`, `dx`, `dy`, `i`, `a` 等）为完整规范英文单词（如 `column_x`, `row_y`, `neighbor_x`, `neighbor_y`, `delta_x`, `delta_y` 等）
- 将 `Point` 类的 `asd`/`asd1`/`asd2` 属性重命名为 `control_ports`/`input_ports`/`output_ports`
- 精简复杂嵌套结构（如退火四方向重复代码块平铺为平直写法）
- 清理无效注释、多余空行、杂乱分隔符
- 完整保留 PW4 预加载逻辑，确认 PW5 预加载逻辑与 PW4 完全一致（当前已存在）
- **禁止提取外部函数** — 所有逻辑保持内嵌在 while 循环中
- **禁止拆分原生逻辑** — while 循环执行顺序完全不变
- **所有变量名必须使用完整英文单词，严禁使用任何缩写**（如 `identifier` 而非 `id`，`binary_string` 而非 `bin`）

## Impact
- Affected specs: 无（纯代码整洁，不影响功能）
- Affected code: `app.py`（全文约 1200 行）
- 不涉及功能变更、不新增/删除逻辑、不改变运行效果

## MODIFIED Requirements

### Requirement: 网格数组变量命名
系统 SHALL 将 `qw1`-`qw5` 重命名为 `grid_1`-`grid_5`，所有引用处同步更新。

#### Scenario: 网格数组引用
- **WHEN** 代码中需要引用第 N 个光场网格
- **THEN** 使用 `grid_N` 变量名（N ∈ {1, 2, 3, 4, 5}）

### Requirement: 全局辅助变量命名
系统 SHALL 将以下辅助变量重命名为完整英文单词（无缩写）：

| 原变量 | 新变量名 | 语义 |
|--------|----------|------|
| `ax1` | `user_input_raw` | 原始用户输入字符串 |
| `ax2` | `input_character_list` | 输入字符列表 |
| `ax3` | `unicode_encoded_bytes` | Unicode 编码字节 |
| `ax4` | `binary_string` | 二进制字符串 |
| `ax5` | `padded_binary_string` | 补齐至32位的二进制字符串 |
| `ax6` | `binary_string_list` | 二进制字符串暂存列表 |
| `ax7` | `random_pool` | 随机池（4bit组求和结果） |
| `ax8` | `active_points_grid_1` | grid_1 中 brightness==9 的 Point 索引列表 |
| `ax9` | `active_points_grid_2` | grid_2 中 brightness==9 的 Point 索引列表 |
| `ax10` | `active_points_grid_3` | grid_3 中 brightness==9 的 Point 索引列表 |
| `ax11` | `active_points_grid_4` | grid_4 中 brightness==9 的 Point 索引列表 |
| `ax12` | `active_points_grid_5` | grid_5 中 brightness==9 的 Point 索引列表 |
| `ax13` | `manhattan_distance` | 曼哈顿距离（多上下文复用） |
| `ax14` | `source_brightness` | 源 Point 的亮度值（多上下文复用） |
| `ax15` | `target_flat_index` | 目标单元格的展平索引（多上下文复用） |
| `ax16` | `computed_brightness` | 计算得出的亮度值（多上下文复用） |
| `ax17` | `block_modified_flag` | 退火区块是否被修改的标记 |
| `ax18` | `current_binary_string` | 当前处理的二进制字符串 |
| `ax19` | 移除（未使用） | 声明但从未赋值使用 |
| `ax20` | `port_type` | 端口类型标记 |
| `ax21` | `port_label` | 端口标识符字符串 |

#### Scenario: 变量引用一致性
- **WHEN** 代码在多个不同上下文（渲染、退火、绑定）中复用同一变量名
- **THEN** 使用统一的通用语义名，确保每个上下文中语义通顺

### Requirement: Point 类属性命名
系统 SHALL 将 Point 类的端口属性重命名为完整英文单词（无缩写）：
- `asd` → `control_ports`（控制端口列表）
- `asd1` → `input_ports`（输入端口列表）
- `asd2` → `output_ports`（输出端口列表）

所有引用处同步更新。

### Requirement: 循环内局部变量命名
系统 SHALL 将循环内局部变量重命名为完整英文单词（无缩写）：

| 原变量 | 新变量名 | 语义 |
|--------|----------|------|
| `cx` | `column_x` | 源 Point 的列坐标 |
| `cy` | `row_y` | 源 Point 的行坐标 |
| `nx` | `neighbor_x` | 邻居单元格的列坐标 |
| `ny` | `neighbor_y` | 邻居单元格的行坐标 |
| `dx` | `delta_x` | X 方向偏移 |
| `dy` | `delta_y` | Y 方向偏移 |
| `i`（循环主索引） | `point_index` | Point 的展平索引 |
| `a`（内循环） | `offset_counter` | 偏移量计数器 |

### Requirement: PW4 与 PW5 预加载逻辑完整性
系统 SHALL 完整保留 PW4（grid_4）的全部预加载逻辑（菱形亮度扩散，仅作用在顶部 3 行 `row_y < 3`）。系统 SHALL 确认 PW5（grid_5）的预加载逻辑与 PW4 完全一致 — 包含相同的菱形扩散算法、相同的作用范围（`row_y < 3`）、相同的亮度上限（`min(computed_brightness, 9)`）。

#### Scenario: PW4 预加载逻辑保留
- **WHEN** 循环执行到 grid_4 的预加载阶段
- **THEN** 对 `active_points_grid_4` 中每个 Point，按其 brightness 进行菱形扩散到 grid_4 的顶部 3 行（`neighbor_y < 3`）

#### Scenario: PW5 预加载逻辑完整
- **WHEN** 循环执行到 grid_5 的预加载阶段
- **THEN** 对 `active_points_grid_5` 中每个 Point，按其 brightness 进行菱形扩散到 grid_5 的顶部 3 行（`neighbor_y < 3`），逻辑与 PW4 完全一致

### Requirement: 退火四方向绑定逻辑精简
系统 SHALL 将退火后的上/下/左/右四方向绑定逻辑（当前为四个独立 `if` 块，每个约 40 行且内容高度相似）精简为平铺直叙的结构：
- 保留四个方向各自的独立判断条件（基于 `random_pool[point_index]` 的值）
- 保留每个方向各自的上/下/左/右 `target_flat_index` 计算逻辑
- 精简重复的 `port_label` 计算和绑定字典构造，减少冗余嵌套层级
- 四个方向的执行顺序（上→下→左→右）保持不变

#### Scenario: 四方向绑定保留
- **WHEN** 退火后 `block_modified_flag` 为 True
- **THEN** 依次检查上/下/左/右四个方向，每个方向独立判断、独立计算 `target_flat_index`、独立执行绑定，整体逻辑不变

### Requirement: 代码联结关系保留
系统 SHALL 完整保留所有变量间的数据流绑定关系、信号互通交互逻辑、模块互联关联关系：
- `binary_string_list` → `random_pool` 的转换关系不变
- `active_points_grid_N` 的收集逻辑不变
- 网格渲染、退火、预加载、绑定的数据流方向不变
- 所有 `isinstance` 类型检查逻辑不变
- 所有 `min`/`max` 边界裁剪逻辑不变

### Requirement: 清理冗余注释与分隔符
系统 SHALL 清理无效注释、多余空行、杂乱分隔符（如 `# ----`、`# -----------`），保留有意义的区块注释（如 `# 预加载qw2` 改为 `# Preload grid_2 diamond spread into top 3 rows`）。

### Requirement: 字典键值命名规范（完整英文单词无缩写）
系统 SHALL 将绑定记录字典中的键名重命名为完整英文单词：
- `"b"` → `"block_name"`（区块名称标识）
- `"i"` → `"port_identifier"`（端口标识符）
- `"a1"` → `"source_point_index"`（源 Point 索引）
- `"a3"` → `"target_point_index"`（目标 Point 索引）
- `"signal"` 保持不变
</</parameter>