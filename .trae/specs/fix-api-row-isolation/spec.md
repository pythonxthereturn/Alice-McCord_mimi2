# API 行隔离与信号传递修复 Spec

## Why
第五层 API 输出行整行全 0，因为这些节点从未收到任何输入信号——现有逻辑跳过了 API 行的连接建立，也没有将信号传递给它们。同时第一层 API 输入行部分节点亮度异常是因为渲染/移动阶段没有完全隔离 API 行。需要彻底加固 API 行保护并实现第五层输出 API 的信号收集。

## What Changes
- **新增函数** `protect_api_rows`：强制保证 API 行全是 Point 对象，亮度不变，在所有关键阶段后调用
- **新增函数** `is_in_normal_region`：统一判断索引是否在常规有效区域，替换分散的跳过条件
- **新增函数** `propagate_to_output_api`：将第五层倒数第二行（row=30）的信号传递给 API 输出行（row=31）
- **修改** `clear_non_point_brightness`：使用 `is_in_normal_region` 统一跳过 API 行
- **修改** `detect_active_points`：使用 `is_in_normal_region` 统一判断
- **修改** `diamond_render_single_point`：使用 `is_in_normal_region` 统一判断
- **修改** `anneal_and_connect`：使用 `is_in_normal_region` 统一判断遍历范围
- **修改** `determine_movement_direction`：使用 `is_in_normal_region` 统一判断
- **修改** `preload_next_grid`：目标层使用 `is_in_normal_region` 检查
- **修改** `transistor_style_signal_propagation`：跳过 API 行亮度修改
- **修改** 主循环：在阶段 9 之后插入 `propagate_to_output_api`，在关键阶段后调用 `protect_api_rows`

## Impact
- Affected specs: app-full-rewrite
- Affected code: `app.py`（新增 3 个函数，修改 7 个函数，修改主循环）

## ADDED Requirements

### Requirement: protect_api_rows 强制保护
系统 SHALL 提供 `protect_api_rows(grid_layer_1, grid_layer_5)` 函数，强制保证第一层索引 0-31 和第五层索引 992-1023 的单元格始终是 Point 对象且 `is_api=True`，亮度不变。

#### Scenario: API 行被渲染破坏后自动恢复
- **WHEN** 任何操作意外将 API 行单元格变为普通数值
- **THEN** `protect_api_rows` 将其重建为 Point 对象，保留原有亮度

### Requirement: is_in_normal_region 统一判断
系统 SHALL 提供 `is_in_normal_region(index, grid_layer)` 辅助函数，统一判断索引是否属于可移动/可连接/可渲染的常规区域。

#### Scenario: 第一层 API 行被排除
- **WHEN** `index // GRID_SIDE_LENGTH == 0` 且 `grid_layer == 1`
- **THEN** 返回 `False`

#### Scenario: 第五层 API 行被排除
- **WHEN** `index // GRID_SIDE_LENGTH == 31` 且 `grid_layer == 5`
- **THEN** 返回 `False`

### Requirement: propagate_to_output_api 信号收集
系统 SHALL 提供 `propagate_to_output_api(grid_layer_5)` 函数，在信号传播后、获取输出前，将第五层倒数第二行（row=30）的亮度值按列传递到对应的 API 输出节点（row=31）。

#### Scenario: 信号成功传递到 API 输出行
- **WHEN** 第五层 row=30 的单元格亮度为 5
- **THEN** 对应列 row=31 的 API 节点 brightness 被设置为 `min(5, MAX_BRIGHTNESS)`，并建立永久输入连接记录

## MODIFIED Requirements

### Requirement: 所有常规逻辑使用 is_in_normal_region
以下函数 SHALL 使用 `is_in_normal_region(index, grid_layer)` 替代原有的 API 行跳过条件：
- `clear_non_point_brightness`
- `detect_active_points`
- `diamond_render_single_point`
- `anneal_and_connect`（遍历范围）
- `determine_movement_direction`
- `preload_next_grid`（目标层）

### Requirement: transistor_style_signal_propagation 跳过 API 行
信号传播阶段 SHALL 跳过第一层 API 输入行（索引 0-31）和第五层 API 输出行（索引 992-1023）的 brightness 赋值。

### Requirement: 主循环插入 protect_api_rows 和 propagate_to_output_api
主循环 SHALL 在以下时机调用 `protect_api_rows`：每次渲染后、清除后、移动后。在阶段 9（信号传播）后 SHALL 调用 `propagate_to_output_api`。

## ADDED Requirements (v2 — 加固)

### Requirement: guard_api_rows 更激进的 API 行守护
系统 SHALL 将 `protect_api_rows` 升级为 `guard_api_rows`，在 每个修改网格的操作之后 调用，包括：`clear_non_point_brightness` 后、`render_grid` 后、`anneal_and_connect` 后、`execute_movement_phase` 后、`preload_next_grid` 后、`transistor_style_signal_propagation` 后、`check_connection_timeouts` 后。恢复时默认亮度为 9（而非 0）。

#### Scenario: 连续守护防止 API 节点丢失
- **WHEN** 任何阶段意外将 API 行单元格变为数字
- **THEN** 下一阶段开始前 `guard_api_rows` 立即将其恢复为 Point(is_api=True, brightness=9)

### Requirement: transistor_style_signal_propagation 完全跳过 API 节点
信号传播阶段 SHALL 在计算输出信号时，对 API 节点（`is_api=True`）直接将 `output_signals[i]` 设为 0 并 `continue`，不参与后续任何信号计算和传播。

#### Scenario: API 节点不产生输出信号
- **WHEN** API 节点的 `input_ports` 中有信号
- **THEN** `output_signals[i]` 被设为 0，不影响其他节点

### Requirement: set_api_input 强制重建
`set_api_input` SHALL 无论该位置之前是什么，都强制重建为新的 Point(is_api=True)，清空所有旧端口和连接，只保留一个永久输入连接。

#### Scenario: API 输入节点被完全重建
- **WHEN** `set_api_input` 被调用
- **THEN** 该位置被替换为全新 Point(is_api=True)，亮度由输入决定，旧连接全部清除

### Requirement: execute_movement_phase 禁止移动到 API 行
`execute_movement_phase` SHALL 在移动目标检查中，禁止普通节点移动到第一层 row=0 或第五层 row=31 的位置。

#### Scenario: 普通节点被阻止进入 API 行
- **WHEN** 普通节点移动目标为 row=0（Layer1）或 row=31（Layer5）
- **THEN** 移动被取消

## REMOVED Requirements
无。