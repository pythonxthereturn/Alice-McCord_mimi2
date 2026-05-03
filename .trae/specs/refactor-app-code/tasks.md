# Tasks

- [x] Task 1: 重命名全局变量和常量 — 替换所有无意义变量名为有意义的英文名，保持逻辑不变
  - [x] 重命名 `qw1`-`qw5` → `light_sources_1`-`light_sources_5`
  - [x] 重命名 `final_grid1`-`final_grid5` → `rendered_grid_1`-`rendered_grid_5`
  - [x] 重命名 `qwer1`、`qwera1`-`qwera5` 为有意义的局部变量名
  - [x] 常量化魔术数字：200、24、5、30 等

- [x] Task 2: 提取 `create_staggered_points(grid_size, step, count)` 公共函数 — 消除 5 组重复的 brightness=1 初始化循环
  - [x] 定义函数签名与实现
  - [x] 用函数调用替换第 60-93 行的 5 个重复循环

- [x] Task 3: 拆分 `terminal_loop` 为多个小函数 — 降低单函数复杂度
  - [x] 提取 `handle_terminal_input()` — 读取输入并编码为二进制
  - [x] 提取 `collect_brightness_1_positions(source_list)` — 收集 brightness==1 的 Point 索引列表
  - [x] 提取 `print_positions_block(title, positions, chunk_size)` — 按块打印位置
  - [x] 重构 `terminal_loop` 调用上述函数

- [x] Task 4: 提取 GUI 公共函数 `create_grid_rectangles(canvas, origin_x, origin_y)` — 消除 `RedStackedWindow` 和 `GreenIndependentWindow` 中重复的 32×32 矩形创建代码

- [x] Task 5: 清理死代码 — 移除 `Point.asd`/`asd1`/`asd2` 未使用属性，移除 `print_grid` 未调用函数

- [x] Task 6: 运行验证 — 确认 Python 语法正确、Tkinter GUI 可正常启动

# Task Dependencies
- Task 2 依赖 Task 1（新变量名在函数中使用）
- Task 3 依赖 Task 1（新变量名在函数中使用）
- Task 4 依赖 Task 1
- Task 5 可与 Task 1-4 并行
- Task 6 依赖 Task 1-5 全部完成
