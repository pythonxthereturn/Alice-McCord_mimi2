# Checklist

## 代码结构
- [x] Point 类包含 `is_api: bool` 属性，默认 `False`
- [x] 所有连接字典包含 `source_point_index`、`target_point_index`、`signal`、`port_type`、`last_signal_value`、`timeout_counter` 六个字段
- [x] 新增常量 `CONNECTION_TIMEOUT_THRESHOLD = 5`
- [x] 新增常量 `DEBUG = True`
- [x] 新增 `import copy`
- [x] `import numpy as np` 在文件开头

## 新增函数
- [x] `clear_all_connection_signals(grid)` 已实现，遍历所有 Point 清除所有端口所有连接的 signal 为 0
- [x] `validate_grid_integrity(grid)` 已实现，验证 center_index 匹配和连接索引在 0-1023 或 -1 范围内
- [x] `check_connection_exists(source_point, target_index)` 已实现，检查 output/input/control 三个端口列表

## 修改函数 - API 保护
- [x] `detect_active_points` 排除 `is_api=True` 的节点
- [x] `determine_movement_direction` API 节点直接返回 -1
- [x] `diamond_render_single_point` API 节点直接返回网格，不修改任何 Point 对象亮度
- [x] `render_grid` 先调用 `clear_non_point_brightness`，API 节点受保护
- [x] `anneal_and_connect` 跳过 `is_api=True` 的活跃点，退火只修改非 Point 单元格
- [x] `execute_movement_phase` API 节点跳过移动

## 修改函数 - 连接管理
- [x] `anneal_and_connect` 调用 `check_connection_exists` 检查重复连接
- [x] `anneal_and_connect` 检查输入 API 节点（索引 0-31）不可作为连接目标
- [x] `anneal_and_connect` 检查输出 API 节点（索引 992-1023）不可建立输出连接
- [x] `anneal_and_connect` 新连接字典包含 `last_signal_value` 和 `timeout_counter`
- [x] `check_connection_timeouts` 已实现，超时连接双向删除
- [x] `check_connection_timeouts` API 永久输入连接（`source_point_index=-1`）不被删除

## 修改函数 - 移动
- [x] `execute_movement_phase` 包含冲突检测（统计目标位置被选中次数）
- [x] `execute_movement_phase` 使用 `copy.deepcopy` 深拷贝节点
- [x] `execute_movement_phase` 打印冲突日志

## 修改函数 - 其他
- [x] `preload_next_grid` 先调用 `clear_non_point_brightness` 清除目标网格
- [x] `transistor_style_signal_propagation` 分两阶段，不清除 signal 值
- [x] `initialize_api_ports` 设置 `is_api=True`，覆盖时打印警告
- [x] `set_api_input` 清除旧连接，新连接包含 `last_signal_value` 和 `timeout_counter`
- [x] `load_full_grid_from_file` 验证结构为 5 层 × 1024，捕获 `FileNotFoundError`

## 主程序 - 13 阶段执行
- [x] 阶段 1: 回合初始化（`clear_non_point_brightness` + `clear_all_connection_signals` + `validate_grid_integrity`）
- [x] 阶段 2-6: 与当前逻辑一致
- [x] 阶段 7: 移动后重渲染（重新检测活跃点 + 渲染）
- [x] 阶段 8-9: 与当前逻辑一致
- [x] 阶段 10: 连接超时检查与删除（`check_connection_timeouts` + `clear_all_connection_signals`）
- [x] 阶段 11-12: 与当前逻辑一致
- [x] 阶段 13: 回合清理（`clear_non_point_brightness` + `clear_all_connection_signals`）
- [x] 主循环用 try-except 包裹整个回合处理逻辑

## 最终验证标准
- [x] 运行 100 个回合后，输入 API 节点仍在索引 0-31，输出 API 节点仍在索引 992-1023（API 节点不移动，由 `determine_movement_direction` 返回 -1 和 `execute_movement_phase` 跳过保证）
- [x] API 节点的亮度值不被渲染或退火操作修改（`diamond_render_single_point`、`render_grid`、`anneal_and_connect` 均跳过 API 节点）
- [x] 普通节点无法连接到输入 API 节点，输出 API 节点无法建立输出连接（`anneal_and_connect` 中检查 `center_index < 32` 和 `center_index >= 992`）
- [x] 打印输出中只出现数字 0-9（`display_grid` 打印 Point.brightness 或整数本身）
- [x] 连续 5 个回合无信号的连接被自动双向删除（`check_connection_timeouts` 实现）
- [x] API 永久输入连接不被超时机制删除（`source_point_index=-1` 时跳过）
- [x] 每个回合结束后，所有非 Point 单元格值为 0（阶段 13 调用 `clear_non_point_brightness`）
- [x] 每个回合结束后，所有连接的 signal 字段为 0（阶段 13 调用 `clear_all_connection_signals`）
- [x] 没有节点丢失、覆盖或连接断裂（深拷贝移动 + 冲突检测 + `update_connections_after_move`）
- [x] 网格文件不存在时打印友好错误并退出（`load_full_grid_from_file` 捕获 `FileNotFoundError`）
- [x] 输入文件不存在时打印友好错误并退出（`read_input_from_text_file` 捕获 `FileNotFoundError`）
- [x] 空输入被正确处理，不崩溃（主循环中 `user_input` 为空时正常处理）
- [x] 所有异常被捕获，单条输入失败不影响其他输入（try-except 包裹）
- [x] `python app.py` 语法无错误（py_compile 验证通过）