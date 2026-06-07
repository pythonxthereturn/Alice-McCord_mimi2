# Checklist

## 新增函数
- [x] `protect_api_rows(grid_layer_1, grid_layer_5)` 已实现，返回修改后的两个网格
- [x] `protect_api_rows` 保护第一层索引 0-31，重建丢失的 Point 并保留亮度
- [x] `protect_api_rows` 保护第五层索引 992-1023，重建丢失的 Point 并保留亮度
- [x] `is_in_normal_region(index, grid_layer)` 已实现
- [x] `is_in_normal_region` 第一层 row=0 返回 False
- [x] `is_in_normal_region` 第五层 row=31 返回 False
- [x] `is_in_normal_region` 其他层始终返回 True
- [x] `propagate_to_output_api(grid_layer_5)` 已实现
- [x] `propagate_to_output_api` 从 row=30 读取信号写入 row=31 API 节点
- [x] `propagate_to_output_api` 保证目标 API 节点存在（丢失则重建）
- [x] `propagate_to_output_api` 建立永久输入连接记录

## 修改函数 - 使用 is_in_normal_region
- [x] `clear_non_point_brightness` 新增 grid_layer 参数，跳过 API 行
- [x] `detect_active_points` 使用 `is_in_normal_region` 替代 `is_api` 检查
- [x] `diamond_render_single_point` 使用 `is_in_normal_region` 替代 `is_api` 检查
- [x] `anneal_and_connect` 使用 `is_in_normal_region` 替代 `is_api` 检查
- [x] `determine_movement_direction` 使用 `is_in_normal_region` 替代 `is_api` 检查
- [x] `preload_next_grid` 目标层使用 `is_in_normal_region` 检查
- [x] `transistor_style_signal_propagation` 跳过 API 行 brightness 赋值

## 主循环修改 (v1)
- [x] 阶段 4 渲染后调用 `protect_api_rows`
- [x] 阶段 7 移动后重渲染后调用 `protect_api_rows`
- [x] 阶段 9 信号传播后调用 `propagate_to_output_api`，然后调用 `protect_api_rows`
- [x] 阶段 13 回合清理后调用 `protect_api_rows`

## 最终验证标准 (v1)
- [x] 第一层 API 输入行（row=0）始终是 Point 对象且 `is_api=True`（protect_api_rows 保证）
- [x] 第五层 API 输出行（row=31）始终是 Point 对象且 `is_api=True`（protect_api_rows 保证）
- [x] 第一层 API 输入行的亮度值不会被渲染或退火修改（is_in_normal_region 排除 row=0）
- [x] 第五层 API 输出行在每轮接收到 row=30 的信号（propagate_to_output_api 实现）
- [x] `get_api_output` 返回非全 0 的二进制字符串（propagate_to_output_api 注入信号）
- [x] 常规节点不会移动到 API 行（determine_movement_direction 使用 is_in_normal_region）
- [x] 常规节点不会与 API 行节点建立连接（anneal_and_connect 使用 is_in_normal_region）
- [x] `python app.py` 语法无错误（py_compile 验证通过）

## v2 加固 — 新增函数
- [x] `guard_api_rows` 已实现，恢复时默认亮度为 9
- [x] `guard_api_rows` 在恢复非 Point 单元格时使用 brightness=9

## v2 加固 — 修改函数
- [x] `transistor_style_signal_propagation` 对 API 节点设 `output_signals[i] = 0` 并跳过（app.py:537）
- [x] `set_api_input` 强制重建为全新 Point(is_api=True)，清空旧端口
- [x] `execute_movement_phase` Layer1 禁止移动到 row=0（app.py:502-503）
- [x] `execute_movement_phase` Layer5 禁止移动到 row=31（app.py:504-505）

## v2 加固 — 主循环 guard_api_rows 调用点
- [x] 阶段 1（clear_non_point_brightness）后调用
- [x] 阶段 4（render_grid）后调用
- [x] 阶段 5（anneal_and_connect）后调用
- [x] 阶段 6（execute_movement_phase）后调用
- [x] 阶段 7（移动后 render_grid）后调用
- [x] 阶段 8（preload_next_grid）后调用
- [x] 阶段 9（propagate_to_output_api）后调用
- [x] 阶段 10（check_connection_timeouts）后调用
- [x] 阶段 13（回合清理）后调用

## v2 加固 — 最终验证
- [x] 第一层 API 输入行在任何阶段后都不会丢失（变为数字）（guard_api_rows 9 处调用，每次操作后立即恢复）
- [x] API 节点不产生输出信号，不影响其他节点（transistor 中 point.is_api → output_signals=0）
- [x] `python app.py` 语法无错误（py_compile 验证通过）