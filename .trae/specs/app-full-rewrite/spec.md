# app.py 完整重写 Spec

## Why
当前 `app.py` 缺少 `Code_20260607.txt` 中定义的多个关键功能：API 节点标识与保护机制、连接超时自动删除、回合初始化/清理阶段、节点移动冲突检测、深拷贝移动、移动后重渲染、连接存在性检查、网格完整性验证、异常处理等。13 个执行阶段的顺序和内容与规范存在多处偏差，需完整重写以确保系统正确性、稳定性和防御式编程。

## What Changes
- **Point 类**：新增 `is_api: bool` 属性，用于区分 API 节点与普通节点
- **连接字典**：新增 `last_signal_value` 和 `timeout_counter` 字段
- **新增常量**：`CONNECTION_TIMEOUT_THRESHOLD = 5`、`DEBUG = True`
- **新增导入**：`import copy`
- **新增函数**（6 个）：`clear_all_connection_signals`、`validate_grid_integrity`、`check_connection_exists`、`check_connection_timeouts`、冲突检测逻辑（嵌入 `execute_movement_phase`）、回合初始化/清理逻辑
- **修改函数**（15 个）：几乎所有现有函数都需修改以适配 API 保护、新连接字典字段、超时机制等
- **执行流程**：从 10 阶段扩展为 13 阶段，新增阶段 1（回合初始化）、阶段 7（移动后重渲染）、阶段 10（连接超时检查与删除）、阶段 13（回合清理）
- **主程序**：添加 try-except 异常包裹、`validate_grid_integrity` 调用、`DEBUG` 条件日志
- **ax.py**：无需修改（网格生成器保持不变）

## Impact
- Affected specs: 无直接依赖
- Affected code: `app.py`（完全重写）

## ADDED Requirements

### Requirement: API 节点标识
系统 SHALL 在 Point 类中增加 `is_api: bool` 属性，默认为 `False`。API 节点（`is_api=True`）在渲染、退火、移动、连接建立等操作中受到特殊保护。

#### Scenario: API 节点不可移动
- **WHEN** `determine_movement_direction` 遇到 `is_api=True` 的节点
- **THEN** 直接返回 -1，不计算移动方向

#### Scenario: API 节点亮度不被渲染修改
- **WHEN** `diamond_render_single_point` 或 `render_grid` 遇到 `is_api=True` 的节点
- **THEN** 跳过该节点，不修改其亮度

#### Scenario: API 节点亮度不被退火修改
- **WHEN** `anneal_and_connect` 遇到 `is_api=True` 的节点
- **THEN** 跳过该节点，不执行退火和连接建立

### Requirement: 连接字典扩展
系统 SHALL 在所有连接字典中包含 `last_signal_value`（初始 0）和 `timeout_counter`（初始 0）字段。

#### Scenario: 连接字典结构
- **WHEN** 创建任何连接（包括 API 永久输入连接）
- **THEN** 连接字典包含 `source_point_index`、`target_point_index`、`signal`、`port_type`、`last_signal_value`、`timeout_counter` 六个字段

### Requirement: 连接超时自动删除
系统 SHALL 在每个回合检查所有连接的超时状态，连续 `CONNECTION_TIMEOUT_THRESHOLD`（5）个回合无信号的连接将被双向删除。

#### Scenario: 超时连接被删除
- **WHEN** 某连接连续 5 个回合 `signal=0`
- **THEN** 从源节点的 `output_ports` 和目标节点的对应端口列表中双向删除该连接

#### Scenario: API 永久输入连接不被删除
- **WHEN** 连接 `source_point_index=-1`（API 永久输入）
- **THEN** 跳过超时检查，永不删除

### Requirement: 连接存在性检查
系统 SHALL 在建立连接前调用 `check_connection_exists` 检查源节点与目标节点之间是否已存在任何连接（正向或反向）。

#### Scenario: 重复连接被阻止
- **WHEN** 源节点与目标节点之间已存在 output/input/control 任一方向的连接
- **THEN** 不建立新连接

### Requirement: 回合初始化
系统 SHALL 在每个回合开始时执行回合初始化：清除所有非 Point 单元格亮度值、清除所有连接信号值、重置临时变量、验证网格完整性。

#### Scenario: 回合从干净状态开始
- **WHEN** 进入新回合
- **THEN** 所有非 Point 单元格值为 0，所有连接 `signal=0`，网格完整性验证通过

### Requirement: 移动后重渲染
系统 SHALL 在节点移动后重新执行一次完整的渲染流程（与阶段 4 相同）。

#### Scenario: 移动后信号场更新
- **WHEN** 节点移动完成
- **THEN** 重新检测活跃点并执行菱形渲染

### Requirement: 节点移动冲突检测
系统 SHALL 在移动阶段统计每个目标位置被选中的节点数，仅当目标位置只被一个节点选中时执行移动。

#### Scenario: 多节点竞争同一目标
- **WHEN** 两个节点都选择移动到同一目标位置
- **THEN** 两个节点都不移动，打印冲突日志

### Requirement: 深拷贝移动
系统 SHALL 使用 `copy.deepcopy` 复制节点到新位置，而非浅赋值。

#### Scenario: 节点深拷贝移动
- **WHEN** 节点移动到新位置
- **THEN** 使用 `copy.deepcopy` 创建副本，更新 `center_index`，原位置置 0

### Requirement: 回合清理
系统 SHALL 在每个回合结束时执行回合清理：清除所有非 Point 单元格亮度值、清除所有连接信号值。

#### Scenario: 回合结束清理
- **WHEN** 当前回合所有阶段执行完毕
- **THEN** 所有非 Point 单元格值为 0，所有连接 `signal=0`

### Requirement: 异常处理
系统 SHALL 用 try-except 包裹整个回合处理逻辑，单条输入处理失败不影响其他输入。

#### Scenario: 单条输入异常不中断程序
- **WHEN** 某条输入处理过程中发生异常
- **THEN** 打印异常信息，继续处理下一条输入

### Requirement: 网格完整性验证
系统 SHALL 在回合初始化和网格加载后验证网格完整性。

#### Scenario: 验证失败立即退出
- **WHEN** `validate_grid_integrity` 发现 `center_index` 不匹配或连接索引越界
- **THEN** 打印错误信息并退出程序

### Requirement: DEBUG 条件日志
系统 SHALL 通过 `DEBUG` 常量控制调试日志输出。`DEBUG=True` 时打印所有调试信息，`DEBUG=False` 时只打印必要信息。

## MODIFIED Requirements

### Requirement: 执行流程顺序
系统 SHALL 按以下 13 阶段顺序执行：回合初始化 → 输入处理 → 活跃点检测 → 初始渲染 → 退火与连接 → 节点移动 → 移动后重渲染 → 跨层预加载 → 信号传播 → 连接超时检查与删除 → 显示网格 → 输出收集 → 回合清理

### Requirement: detect_active_points 排除 API 节点
`detect_active_points` SHALL 排除 `is_api=True` 的节点，仅返回普通节点的活跃点。

### Requirement: anneal_and_connect 保护 Point 对象和 API 节点
退火阶段 SHALL 只修改非 Point 单元格的亮度值，不修改任何 Point 对象（包括 API 节点）的亮度。连接建立阶段 SHALL 检查 `check_connection_exists`、API 节点规则、端口容量。

### Requirement: transistor_style_signal_propagation 不清除信号
信号传播阶段 SHALL 不清除连接的 `signal` 值，留待超时检查阶段处理。

### Requirement: initialize_api_ports 设置 is_api
`initialize_api_ports` SHALL 设置 `is_api=True`，并覆盖已有非 API 节点时打印警告。

### Requirement: set_api_input 清除旧连接
`set_api_input` SHALL 清空 API 节点的 `input_ports` 后添加新的永久输入连接，连接字典包含 `last_signal_value` 和 `timeout_counter`。

### Requirement: load_full_grid_from_file 结构验证
`load_full_grid_from_file` SHALL 验证加载的网格结构为 5 层 × 1024 单元格，捕获 `FileNotFoundError`。

### Requirement: render_grid 先清除后渲染
`render_grid` SHALL 先调用 `clear_non_point_brightness` 清除所有非 Point 单元格亮度，再执行渲染。

### Requirement: preload_next_grid 先清除目标网格
`preload_next_grid` SHALL 先调用 `clear_non_point_brightness` 清除目标网格的非 Point 单元格亮度，再执行预加载。

## REMOVED Requirements
无。