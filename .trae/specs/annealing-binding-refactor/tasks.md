# Tasks

- [x] Task 1: 重构 Point 类数据结构
  - 新增信号强度字段 `signal_strength`
  - 新增控制信号字段 `control_signal`（默认0）
  - 新增输出值字段 `output_value`（默认0）
  - 修改绑定记录格式为结构化字典：`{"block": 区块号, "index": 类序号, "port": "端口类型", "target_port": "目标端口类型", "signal": 信号强度}`

- [x] Task 2: 实现端口合规性检查函数
  - 实现 `check_port_compliance(source_port_type, target_port_type)` 函数
  - 规则：输出→控制/输入；输入/控制→输出
  - 返回布尔值

- [x] Task 3: 实现控制端口→输入端口的数值检测函数
  - 实现 `check_input_value_overflow(target_point)` 函数
  - 检测目标类 asd1 列表内的数值是否>9
  - 若>9返回True（跳过绑定）

- [x] Task 4: 实现双向绑定记录函数
  - 实现 `create_bidirectional_binding(source_point, source_port, target_point, target_port, source_block, target_block, signal_strength)` 函数
  - 双方列表均添加记录
  - 记录含：区块号、类序号、端口类型、对方端口类型、信号强度（3+1个键值）

- [x] Task 5: 实现逐区块退火与回火主循环
  - 重构 `process_annealing_and_binding` 为逐区块、逐类处理
  - 对每个类：退火(anneal) → 绑定 → 回火(re-anneal)
  - 仅对当前类单独渲染，非整体渲染
  - 完成当前区块后切换到下一区块

- [x] Task 6: 实现信号强度转换与分发
  - 实现 `convert_binary_to_signal(bin_str_32)` 函数
  - 1→10，0→5
  - 实现 `distribute_signal_to_first_block(signal_list)` 函数
  - 按顺序分发给区块1的索引0-31共32个类的输入端口

- [x] Task 7: 实现第一区块32类输入端口独立控制接口
  - 实现 `get_block1_class_value(class_index)` 函数
  - 仅查询数值和信号强度，不影响正常运行

- [x] Task 8: 实现信号逐级传递逻辑
  - 实现 `propagate_signal_through_bindings()` 函数
  - 从区块1第一行开始，通过绑定关系逐级传递
  - 实现 `erase_initial_signal()` 函数
  - 抹除第一条信号记录（归0），保留连接关系

- [x] Task 9: 实现三极管控制逻辑
  - 实现 `apply_transistor_control(point)` 函数
  - control_signal > 0：停止输出
  - control_signal < 0：允许输出
  - control_signal == 0：输出永久0

- [x] Task 10: 实现距离计算衰减逻辑
  - 实现 `apply_distance_decay()` 函数
  - 在第五区块底部执行，覆盖全部32类
  - 替换原30秒sleep

- [x] Task 11: 实现输出结果UTF-8拼接打印
  - 实现 `collect_and_print_output()` 函数
  - 收集所有类输出值，拼接转UTF-8，打印

- [x] Task 12: 实现输入输出信号取最大值规则
  - 实现 `get_max_input_signal(point)` 函数
  - 有输入才有输出，取输入信号最大值

- [x] Task 13: 实现硬件暂缓2秒停顿
  - 在主循环末尾添加 `time.sleep(2)`

# Task Dependencies
- Task 2, 3, 4 依赖 Task 1（数据结构先行）
- Task 5 依赖 Task 2, 3, 4, 9
- Task 8 依赖 Task 4, 5（需要绑定关系）
- Task 10 依赖 Task 5, 8（在所有核心逻辑后执行）
- Task 11 依赖 Task 8, 9, 10
- Task 6, 7 可并行于 Task 5-8
- Task 12 可并行（纯函数）
- Task 13 为最后一步
