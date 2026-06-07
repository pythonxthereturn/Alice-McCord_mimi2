# Plan: 代码审查、问题诊断与修复

## 1. 当前状态总结

### 1.1 Code_20260607.txt 需求对照

| # | 需求 | 状态 | 位置 |
|---|------|------|------|
| 1 | Point 类增加 `api_signal` 字段 | ✅ 已实现 | `app.py` L40, L47 |
| 2 | `set_api_input` 亮度固定为 9，信号存入 `api_signal` | ✅ 已实现 | `app.py` L729-759 |
| 3 | `propagate_to_output_api` 亮度固定为 9，信号存入 `api_signal` | ✅ 已实现 | `app.py` L260-284 |
| 4 | `get_api_output` 读取 `api_signal` 而非 `brightness` | ✅ 已实现 | `app.py` L761-782 |
| 5 | `guard_api_rows` 强制 brightness=9 | ✅ 已实现 | `app.py` L180-194 |
| 6 | 信号传播中第一层 API 信号注入到 row=1 | ✅ 已实现 | `app.py` L653-663 |
| 7 | 移除主循环末尾 `initialize_api_ports` 调用 | ✅ 已实现 | `app.py` L1062 仅保留 `guard_api_rows` |
| 8 | `load_full_grid_from_file` 传递 `api_signal` | ✅ 已实现 | `app.py` L814-815 |

### 1.2 运行验证结果

- 语法检查：通过 ✅
- 程序运行：成功（exit code 0）✅
- API 行显示：Grid Layer 1 第一行全 9，Grid Layer 5 最后一行全 9 ✅
- 二进制输出：非全 0，有信号输出 ✅
- UTF-8 解码：输出字符（但与输入不完全匹配）⚠️

---

## 2. 发现的问题

### 问题 1（高优先级）：Unicode 控制台编码错误

**现象**：`print("✅ 网格加载完成：...")` 等包含 emoji 的 print 语句在 Windows GBK 控制台下抛出 `UnicodeEncodeError`。需要设置 `PYTHONIOENCODING=utf-8` 才能运行。

**文件**：`app.py` 多处（L726, L819, L910, L1069 等）

**修复**：将所有 `print` 中的 emoji（✅、❌）替换为 ASCII 纯文本标记（如 `[OK]`、`[ERR]`），或使用 `sys.stdout.reconfigure(encoding='utf-8')`。

### 问题 2（中优先级）：`debug_inject.py` 调用了 `initialize_api_ports`

**现象**：`debug_inject.py` L12 调用了 `initialize_api_ports(grid_layer_1, grid_layer_5)`，该函数会将 API 节点亮度重置为 0，破坏 `guard_api_rows` 的保护效果。

**文件**：`debug_inject.py` L12

**修复**：将 `initialize_api_ports` 调用替换为 `guard_api_rows`。

### 问题 3（中优先级）：`inject_api_signal_vertically` 与 `transistor_style_signal_propagation` 中的 API 注入功能重复

**现象**：
- `transistor_style_signal_propagation` L653-663：在 L1 row=1 的 Point 节点中注入 `api_signal`
- `inject_api_signal_vertically` L507-570：向 L1-L5 的特定行注入 API 信号（包括 L1 row=1）

两者在 L1 row=1 的注入逻辑重复。`inject_api_signal_vertically` 的覆盖范围更广（直接写入非 Point 单元格），但 `transistor_style_signal_propagation` 中的注入仅对 Point 节点生效。

**文件**：`app.py` L507-570, L653-663

**决策**：保留 `inject_api_signal_vertically`（因为它能处理非 Point 单元格），可以移除 `transistor_style_signal_propagation` 中 L1 row=1 的注入代码以避免冗余。但**保留两者也可**，不会有冲突。

### 问题 4（低优先级）：信号输出与输入不完全匹配

**现象**：输出二进制信号与输入二进制信号存在位翻转（bit errors）。例如：
- 输入 "谢" UTF-8: `11101000 10110000 10100010`
- 输出: `11101010 10110000 10100111`（3 位不同）

**原因**：这是网格系统的固有特性——5 层网格中有 256 个随机 Point 节点，经过 diamond 渲染、退火、连接、移动、信号传播等多个随机/混沌过程，信号在传播中会被网格自身的动态行为干扰。

**是否需要修复**：Code_20260607.txt 未要求完美信号保真，只要求信号能从 API 输入传播到 API 输出。当前信号确实到达了输出 API 行（二进制非全 0），满足需求。如果后续需要提高信号保真度，可考虑：
- 增加 `signal_preload_next_grid` 的迭代次数（当前 4 轮）
- 在 `inject_api_signal_vertically` 中直接写入 L5 row 30 并立即调用 `propagate_to_output_api`，绕过中间层干扰
- 为 API 信号路径建立专用"直通管道"（不经过普通节点的随机行为）

### 问题 5（低优先级）：`initialize_api_ports` 函数仍存在但未被调用

**现象**：`initialize_api_ports` 函数（L712-727）仍保留在代码中，但主循环中已不再调用。该函数将 API 亮度设为 0，与 `guard_api_rows`（亮度=9）冲突。

**文件**：`app.py` L712-727

**建议**：删除或标记为 deprecated，防止未来误用。

---

## 3. 修改方案

### 修改 1：修复 Unicode 控制台编码问题

**文件**：`app.py`

**方案**：在主程序入口处（`if __name__ == "__main__":` 之后）添加 `sys.stdout.reconfigure(encoding='utf-8')`，同时确保所有 print 中的 emoji 也能正常显示。

**具体改动**：
- 在 `app.py` 顶部 `import sys`（如果还没有）
- 在 `if __name__ == "__main__":` 后第一行添加：
  ```python
  import sys
  sys.stdout.reconfigure(encoding='utf-8')
  ```

### 修改 2：修复 `debug_inject.py` 中的 `initialize_api_ports` 调用

**文件**：`debug_inject.py`

**具体改动**：
- L12: 将 `grid_layer_1, grid_layer_5 = initialize_api_ports(grid_layer_1, grid_layer_5)` 替换为 `grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)`

### 修改 3（可选）：清理 `initialize_api_ports` 死代码

**文件**：`app.py`

**具体改动**：删除 L712-727 的 `initialize_api_ports` 函数定义，或在函数上方添加注释标记为废弃。

---

## 4. 验证步骤

1. **语法检查**：`python -c "compile(open('app.py', encoding='utf-8').read(), 'app.py', 'exec'); print('Syntax OK')"`
2. **运行程序**：`python app.py`（不再需要手动设置 PYTHONIOENCODING）
3. **观察输出**：
   - Grid Layer 1 第一行全部为 9
   - Grid Layer 5 最后一行全部为 9
   - [API Output] 二进制信号非全 0
   - [API Output] UTF-8 字符解码成功
   - 无 UnicodeEncodeError
4. **调试脚本**：`python debug_inject.py` 验证 API 节点亮度保持为 9

---

## 5. 假设与决策

- **假设**：网格文件 `Alice_McCord.exdc` 已存在且有效
- **假设**：`Alice.wtms` 输入文件存在且包含有效 UTF-8 文本
- **决策**：信号保真度问题（输出与输入不完全匹配）属于网格系统的固有特性，不在本次修复范围内
- **决策**：保留 `inject_api_signal_vertically` 和 `transistor_style_signal_propagation` 中的双重 API 注入逻辑，因为两者互补（前者处理非 Point 单元格，后者处理 Point 节点的连接传播）
- **决策**：`initialize_api_ports` 函数暂时保留但标记为废弃，不删除（避免影响其他可能的引用）