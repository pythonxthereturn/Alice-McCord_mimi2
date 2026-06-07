# 修复 app.py 小 bug 与缩进问题 Spec

## Why
当前 `app.py` 经过之前的多轮重构后，存在少量遗留问题：一处重复变量初始化、潜在的缩进不一致等。需要在**不动核心逻辑、不新增/删除功能**的前提下，精准修复这些问题，确保代码整洁且运行逻辑完全不变。

## What Changes
- 删除第 527 行重复的 `binary_string_list = []`（第 523 行已初始化）
- 检查并修复所有缩进不一致（如 tab/空格混用）
- 验证所有函数间空行、代码块缩进符合 PEP 8 基本规范
- 确认 `anneal_and_connect` 中四方向循环的缩进层级正确
- **不动任何业务逻辑、不动任何变量命名、不动任何函数签名**

## Impact
- Affected specs: 无
- Affected code: `app.py`（仅修复性问题，非功能性变更）

## MODIFIED Requirements

### Requirement: 移除重复变量初始化
系统 SHALL 移除 while 循环内第 527 行重复的 `binary_string_list = []` 声明，该变量已在第 523 行初始化。

#### Scenario: 变量初始化唯一性
- **WHEN** Stage A 输入处理阶段开始
- **THEN** `binary_string_list` 仅在声明区初始化一次，后续代码中不再出现冗余的重新赋空列表

### Requirement: 缩进一致性
系统 SHALL 确保整个 `app.py` 文件中所有缩进使用统一的 4 空格（no tabs），所有代码块层级关系清晰且一致。

#### Scenario: tab/空格检查
- **WHEN** 用 `python -m tabnanny` 或类似工具检查文件
- **THEN** 不报告任何 tab/空格混用问题

### Requirement: 逻辑完整性保持不变
系统 SHALL 确保修复后程序的行为与修复前完全一致。

#### Scenario: 运行结果不变
- **WHEN** 用相同的输入文件执行程序
- **THEN** 控制台输出（打印字符、调试信息）与修复前完全一致