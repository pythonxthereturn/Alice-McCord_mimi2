# 重构 app.py 代码规范性与可读性

## Why
当前 `app.py` 中存在大量无意义变量命名（`qw1`-`qw5`、`qwer1`、`aqw1`-`aqw5` 等）、5 处几乎完全相同的代码块重复、`terminal_loop` 函数职责过多、GUI 类中重复的矩形创建与绘制逻辑。代码可读性极差，维护困难。

## What Changes
- 重命名所有全局列表/变量为有意义的英文名称
- 提取重复的初始化 Pattern 为函数 `create_staggered_points()`
- 提取重复的 brightness=1 过滤逻辑
- 提取重复的终端打印块为函数
- 拆分 `terminal_loop` 为多个小函数
- 提取 GUI 矩形创建公共函数
- 移除 Point 类中未使用的 `asd`/`asd1`/`asd2` 属性（保留不改逻辑 — 它们从未被读取或写入，移除属于清理死代码）
- 移除已定义但从未调用的 `print_grid` 函数
- 常量化魔术数字

## Impact
- Affected specs: 无（无现有 spec）
- Affected code: `app.py`（唯一文件）

## MODIFIED Requirements
### Requirement: 光场网格变量命名
系统 SHALL 使用有意义的英文变量名替代原来 `qw1`-`qw5` 等无意义名称。
- `qw1` → `light_sources_1`（保留 1-5 编号以区分五个独立通道）
- `qwer1` → 循环内局部变量，不保留
- `aqw1`-`aqw5` → 不再作为独立变量存在，由函数返回值替代
- `final_grid1`-`final_grid5` → `rendered_grid_1`-`rendered_grid_5`

### Requirement: 光源分布初始化
系统 SHALL 将 5 组几乎相同的 brightness=1 Point 初始化提取为公共函数 `create_staggered_points(grid_size, step)`，接受 step 参数控制分布间距。

### Requirement: 终端命令处理拆分
系统 SHALL 将 `terminal_loop` 拆分为：
- `handle_terminal_input()` — 读取用户输入并编码
- `collect_brightness_1_positions(source_list)` — 收集 brightness==1 的索引
- `print_positions_block(title, positions, chunk_size)` — 格式化打印位置

### Requirement: GUI 矩形创建提取
系统 SHALL 将 `RedStackedWindow.__init__` 和 `GreenIndependentWindow.__init__` 中重复的 32×32 矩形创建逻辑提取为 `create_grid_rectangles(canvas, origin_x, origin_y)` 公共函数。

### Requirement: 死代码移除
系统 SHALL 移除：
- `Point` 类中从未被使用也从未被赋值的 `asd`/`asd1`/`asd2` 属性
- 已定义但从未调用的 `print_grid` 函数

## REMOVED Requirements
无。
