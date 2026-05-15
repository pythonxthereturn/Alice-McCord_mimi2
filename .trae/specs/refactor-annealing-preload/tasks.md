# 重构退火逻辑与预加载机制 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 修复 qw1 退火逻辑语法错误
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 修复字典键值对缺少逗号的问题
  - 修复 `elif == 2:` 语法错误（应为 `elif ax21 == 2:`）
  - 修复 `asd2.append = (...)` 语法错误（应为 `qw1[...].asd2.append(...)`）
  - 去掉无意义的 `if i < ax8:` 检查
  - 修复 ax15 的使用：应该使用当前索引 i 而不是循环变量的最后值
  - 修复重复赋值同一个 Point 的问题，改为分别在当前点和对方点记录连接
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: Python 语法检查通过（`python -m py_compile app.py`）
  - `human-judgement` TR-1.2: 代码结构与原代码风格一致
- **Notes**: ax15 应该替换为当前索引 i，方向偏移分别为 ±1（左右）和 ±32（上下）

## [ ] Task 2: 完善 qw1 的方向连接记录逻辑
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 修复连接字典结构：`{"b": "qw1", "i": ax21, "a1": 当前位置, "a3": 对方位置, "signal": 0}`
  - signal 默认为 0
  - 正确计算四个方向的对方位置（上: i-32, 下: i+32, 左: i-1, 右: i+1）
  - 分别在当前点和对方点的 asd2 列表中添加连接记录
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 连接字典包含所有必要的键（b, i, a1, a3, signal）
  - `programmatic` TR-2.2: 连接记录被正确添加到两个 Point 的 asd2 列表
- **Notes**: 保持原有的 ax21 计算逻辑

## [ ] Task 3: 将 qw1 的逻辑应用到 qw2-qw5
- **Priority**: P1
- **Depends On**: Task 2
- **Description**: 
  - 为 qw2 应用修复后的退火和连接逻辑（将 qw1 替换为 qw2，ax8 替换为 ax9）
  - 为 qw3 应用修复后的退火和连接逻辑（将 qw1 替换为 qw3，ax8 替换为 ax10）
  - 为 qw4 应用修复后的退火和连接逻辑（将 qw1 替换为 qw4，ax8 替换为 ax11）
  - 为 qw5 应用修复后的退火和连接逻辑（将 qw1 替换为 qw5，ax8 替换为 ax12）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: qw2-qw5 的退火逻辑与 qw1 结构一致
  - `human-judgement` TR-3.2: 变量替换正确，没有遗漏

## [ ] Task 4: 实现预加载机制
- **Priority**: P1
- **Depends On**: Task 3
- **Description**: 
  - 在 qw1 退火逻辑后添加预加载 qw2 的逻辑
  - 在 qw2 退火逻辑后添加预加载 qw3 的逻辑
  - 在 qw3 退火逻辑后添加预加载 qw4 的逻辑
  - 在 qw4 退火逻辑后添加预加载 qw5 的逻辑
  - 预加载逻辑：处理下一区块中 y 坐标 < 3 的区域（即索引 0-95）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 预加载逻辑在正确的位置被调用
  - `programmatic` TR-4.2: 预加载只处理下一区块的前三行（y < 3）
- **Notes**: 预加载逻辑与原有渲染逻辑一致，但只应用于指定区域

## [ ] Task 5: 整体测试和验证
- **Priority**: P0
- **Depends On**: Task 4
- **Description**: 
  - 运行完整程序测试语法和逻辑
  - 验证退火逻辑正常工作
  - 验证预加载机制正常工作
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 程序可以正常启动并接受用户输入
  - `human-judgement` TR-5.2: 输出符合预期
