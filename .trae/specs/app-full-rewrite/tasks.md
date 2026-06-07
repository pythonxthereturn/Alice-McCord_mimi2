# Tasks

- [x] Task 1: 修改 Point 类和连接字典结构 — 新增 `is_api` 属性，扩展连接字典字段
  - [x] 添加 `is_api: bool = False` 参数到 `Point.__init__`
  - [x] 确保所有创建连接的位置包含 `last_signal_value: 0` 和 `timeout_counter: 0` 字段
  - [x] 确保所有创建 Point 的位置传递或不破坏 `is_api` 参数

- [x] Task 2: 新增常量和导入 — 添加 `CONNECTION_TIMEOUT_THRESHOLD`、`DEBUG`、`import copy`
  - [x] 添加 `CONNECTION_TIMEOUT_THRESHOLD = 5`
  - [x] 添加 `DEBUG = True`
  - [x] 添加 `import copy`（在 `import numpy as np` 之后）

- [x] Task 3: 实现新增工具函数
  - [x] 实现 `clear_all_connection_signals(grid)` — 遍历所有 Point，清除所有连接的 `signal` 为 0
  - [x] 实现 `validate_grid_integrity(grid)` — 验证 center_index 匹配和连接索引有效性
  - [x] 实现 `check_connection_exists(source_point, target_index)` — 检查正向/反向连接是否已存在

- [x] Task 4: 修改 `detect_active_points` — 排除 `is_api=True` 的 API 节点

- [x] Task 5: 修改 `determine_movement_direction` — API 节点直接返回 -1

- [x] Task 6: 修改 `diamond_render_single_point` — 保护 API 节点和 Point 对象亮度不被修改

- [x] Task 7: 修改 `render_grid` — 先调用 `clear_non_point_brightness`，再渲染，保护 API 节点

- [x] Task 8: 修改 `anneal_and_connect` — 全面重写
  - [x] 退火阶段：只修改非 Point 单元格，不修改 Point 对象亮度
  - [x] 连接建立阶段：调用 `check_connection_exists` 检查重复连接
  - [x] 连接建立阶段：检查 API 节点规则（输入 API 不可作为目标，输出 API 不可建立输出连接）
  - [x] 连接字典包含 `last_signal_value` 和 `timeout_counter`
  - [x] 跳过 `is_api=True` 的活跃点

- [x] Task 9: 修改 `execute_movement_phase` — 添加冲突检测和深拷贝
  - [x] API 节点跳过移动
  - [x] 统计每个目标位置被选中的节点数
  - [x] 过滤出无冲突的移动
  - [x] 使用 `copy.deepcopy` 执行移动
  - [x] 打印冲突日志

- [x] Task 10: 修改 `preload_next_grid` — 先调用 `clear_non_point_brightness` 清除目标网格

- [x] Task 11: 修改 `transistor_style_signal_propagation` — 分两阶段执行，不清除信号值

- [x] Task 12: 实现 `check_connection_timeouts` — 连接超时检查与双向删除

- [x] Task 13: 修改 `initialize_api_ports` — 设置 `is_api=True`，覆盖时打印警告

- [x] Task 14: 修改 `set_api_input` — 清除旧连接，新连接包含 `last_signal_value` 和 `timeout_counter`

- [x] Task 15: 修改 `load_full_grid_from_file` — 添加结构验证和 `FileNotFoundError` 异常处理

- [x] Task 16: 重写主程序 `__main__` — 13 阶段执行流程
  - [x] 阶段 1: 回合初始化（清除非 Point 亮度、清除连接信号、验证网格完整性）
  - [x] 阶段 2: 输入处理（保持不变）
  - [x] 阶段 3: 活跃点检测（保持不变）
  - [x] 阶段 4: 初始渲染（保持不变）
  - [x] 阶段 5: 退火与连接（保持不变）
  - [x] 阶段 6: 节点移动（保持不变）
  - [x] 阶段 7: 移动后重渲染（新增）
  - [x] 阶段 8: 跨层预加载（保持不变）
  - [x] 阶段 9: 信号传播（保持不变）
  - [x] 阶段 10: 连接超时检查与删除（新增）
  - [x] 阶段 11: 显示网格（保持不变）
  - [x] 阶段 12: 输出收集（保持不变）
  - [x] 阶段 13: 回合清理（新增）
  - [x] 添加 try-except 异常包裹
  - [x] 添加 `DEBUG` 条件日志控制

# Task Dependencies
- Task 2 依赖 Task 1（新字段在常量中使用）
- Task 3 依赖 Task 1（新函数使用新字段）
- Task 4-15 依赖 Task 1-3（函数修改依赖于新类/字段/工具函数）
- Task 4-15 可并行执行（互不依赖）
- Task 16 依赖 Task 1-15 全部完成（主程序整合所有修改）