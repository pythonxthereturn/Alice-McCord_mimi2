# Tasks

- [x] Task 1: 新增 `protect_api_rows` 函数 — 强制保护 API 行完整性
  - [x] 遍历第一层索引 0-31：如果非 Point 或非 is_api，重建为 Point(is_api=True)，保留原有亮度
  - [x] 遍历第五层索引 992-1023：同上
  - [x] 接收 `grid_layer_1` 和 `grid_layer_5` 参数，返回修改后的两个网格

- [x] Task 2: 新增 `is_in_normal_region` 辅助函数 — 统一常规区域判断
  - [x] 参数 `(index, grid_layer)`，grid_layer 为 1-5 的整数
  - [x] 第一层：row != 0 返回 True
  - [x] 第五层：row != 31 返回 True
  - [x] 其他层：始终返回 True

- [x] Task 3: 新增 `propagate_to_output_api` 函数 — 第五层 API 输出信号收集
  - [x] 从第五层 row=30 读取每列亮度值
  - [x] 写入对应列 row=31 的 API 节点 brightness
  - [x] 保证目标 API 节点存在（如丢失则重建）
  - [x] 建立永久输入连接记录

- [x] Task 4: 修改 `clear_non_point_brightness` — 使用 `is_in_normal_region` 跳过 API 行
  - [x] 新增 `grid_layer` 参数（默认 None，None 时全区域处理）
  - [x] 在遍历时检查 `is_in_normal_region`

- [x] Task 5: 修改 `detect_active_points` — 使用 `is_in_normal_region` 统一判断
  - [x] 将 `grid[i].is_api == False` 替换为 `is_in_normal_region(i, grid_layer)`

- [x] Task 6: 修改 `diamond_render_single_point` — 使用 `is_in_normal_region` 统一判断
  - [x] 将 `grid[point_index].is_api == True` 替换为 `not is_in_normal_region(point_index, grid_layer)`

- [x] Task 7: 修改 `anneal_and_connect` — 使用 `is_in_normal_region` 统一判断
  - [x] 活跃点遍历时使用 `is_in_normal_region` 替换 `is_api` 检查
  - [x] 连接目标检查时使用 `is_in_normal_region`

- [x] Task 8: 修改 `determine_movement_direction` — 使用 `is_in_normal_region` 统一判断
  - [x] 将 `grid[point_index].is_api == True` 替换为 `not is_in_normal_region(point_index, grid_layer)`

- [x] Task 9: 修改 `preload_next_grid` — 目标层使用 `is_in_normal_region` 检查
  - [x] 在目标单元格更新前检查 `is_in_normal_region`

- [x] Task 10: 修改 `transistor_style_signal_propagation` — 跳过 API 行 brightness 赋值
  - [x] 在修改 `point.brightness` 前检查 `is_in_normal_region(i, current_layer)`

- [x] Task 11: 修改主循环 — 插入 `protect_api_rows` 和 `propagate_to_output_api`
  - [x] 阶段 4（初始渲染）后调用 `protect_api_rows`
  - [x] 阶段 7（移动后重渲染）后调用 `protect_api_rows`
  - [x] 阶段 9（信号传播）后调用 `propagate_to_output_api`，然后调用 `protect_api_rows`
  - [x] 阶段 13（回合清理）后调用 `protect_api_rows`

# Tasks (v2 — 加固)

- [x] Task 12: 升级 `protect_api_rows` 为 `guard_api_rows` — 更激进的 API 行守护
  - [x] 恢复时默认亮度为 9（未破坏时保留原亮度）
  - [x] 在 每个修改网格的操作之后 调用

- [x] Task 13: 修改 `transistor_style_signal_propagation` — API 节点不产生输出信号
  - [x] 在计算 output_signals 时，对 `is_api=True` 的节点直接设 `output_signals[i] = 0` 并 `continue`
  - [x] 不参与 input_signals 收集和 control_triggered 判断

- [x] Task 14: 修改 `set_api_input` — 强制重建 API 节点
  - [x] 无论该位置之前是什么，都替换为全新 Point(is_api=True)
  - [x] 清空所有旧端口，只保留一个永久输入连接

- [x] Task 15: 修改 `execute_movement_phase` — 禁止移动到 API 行
  - [x] Layer1 禁止移动到 row=0
  - [x] Layer5 禁止移动到 row=31

- [x] Task 16: 修改主循环 — 在所有关键位置调用 `guard_api_rows`
  - [x] 阶段 1（clear_non_point_brightness）后调用
  - [x] 阶段 4（render_grid）后调用
  - [x] 阶段 5（anneal_and_connect）后调用
  - [x] 阶段 6（execute_movement_phase）后调用
  - [x] 阶段 7（移动后 render_grid）后调用
  - [x] 阶段 8（preload_next_grid）后调用
  - [x] 阶段 9（transistor_style_signal_propagation + propagate_to_output_api）后调用
  - [x] 阶段 10（check_connection_timeouts）后调用
  - [x] 阶段 13（回合清理）后调用

# Task Dependencies
- Task 4-10 全部依赖 Task 2（需要 `is_in_normal_region` 函数）
- Task 11 依赖 Task 1、Task 3（需要 `protect_api_rows` 和 `propagate_to_output_api`）
- Task 4-10 可并行执行
- Task 12-16 无相互依赖，可并行执行