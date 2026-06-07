# Plan: 代码审查、验证与跨层传播修复

## 1. 当前状态总结

经过对 `app.py` 与 `Code_20260607.txt` 的逐项比对，**Code_20260607.txt 要求的 8 项修改已全部实现**：

| # | 修改项 | 状态 |
|---|--------|------|
| 1 | Point 类增加 `api_signal` 字段 | 已完成 (L39-40, L47) |
| 2 | `set_api_input` 使用 `api_signal`，brightness 固定为 9 | 已完成 (L636-649) |
| 3 | `propagate_to_output_api` 使用 `api_signal`，brightness 固定为 9 | 已完成 (L247-271) |
| 4 | `get_api_output` 读取 `api_signal` | 已完成 (L654-675) |
| 5 | `guard_api_rows` 强制 brightness=9 | 已完成 (L167-181) |
| 6 | 信号传播中注入 API 信号到 L1 row=1 | 已完成 (L546-557) |
| 7 | 移除主循环末尾 `initialize_api_ports` 调用 | 已完成 (L949 仅保留 guard) |
| 8 | `load_full_grid_from_file` 传递 `api_signal` | 已完成 (L706-708) |

## 2. 发现的问题

### 2.1 跨层信号传播机制存在断层（高优先级）

**问题描述**：当前的多轮传播循环（L902-915）依赖 `preload_next_grid` 将信号跨层传递，但该函数只写入**非 Point 单元格**的数字亮度值，而 `detect_active_points` 只检测 **Point 对象**。这意味着：

- L1 的激活 Point 节点 → preload 到 L2 的非 Point 单元格 → 这些数字值不会被 `detect_active_points` 检测到 → 无法继续 preload 到 L3
- 信号链在 L2 处断裂

**影响**：API 输入信号可能无法到达 L5 输出 API 行，导致输出始终为全 0。

### 2.2 `ax.py` 的 Point 类缺少 `api_signal`（低优先级）

`ax.py` L18-30 的 Point 类没有 `api_signal` 参数。当前由 `load_full_grid_from_file` 中的 `getattr(cell, 'api_signal', 0)` 兜底，不影响运行。但如果重新生成网格，新 Point 对象没有此属性。

### 2.3 numpy 安装失败（阻塞性）

`pip_install_output.txt` 显示 numpy 安装因权限问题失败。需要先解决环境问题才能运行程序。

## 3. 修改方案

### 修改 1: 修复跨层信号传播——在 preload 后检测所有非零单元格（不仅是 Point）

**文件**: `app.py`

**思路**: 新增一个 `detect_active_cells` 函数，检测所有亮度 > 0 的单元格（包括 Point 和非 Point 数字），用于跨层 preload 的源信号检测。

**具体改动**:

在 `detect_active_points` 函数之后新增：

```python
def detect_active_cells(grid: list, grid_layer: int) -> list:
    """检测所有亮度>0的单元格（Point对象 + 非Point数字），用于跨层传播"""
    active_cells = []
    for i in range(len(grid)):
        if not is_in_normal_region(i, grid_layer):
            continue
        if isinstance(grid[i], Point):
            if grid[i].brightness > 0:
                active_cells.append((i, grid[i].brightness))
        elif isinstance(grid[i], (int, float)) and grid[i] > 0:
            active_cells.append((i, int(grid[i])))
    return active_cells
```

修改多轮传播循环（L902-915），将 `detect_active_points` 替换为 `detect_active_cells`：

```python
for _ in range(4):
    ap1 = detect_active_cells(grid_layer_1, 1)
    ap2 = detect_active_cells(grid_layer_2, 2)
    ap3 = detect_active_cells(grid_layer_3, 3)
    ap4 = detect_active_cells(grid_layer_4, 4)
    grid_layer_2 = preload_next_grid(grid_layer_1, grid_layer_2, ap1, 2)
    grid_layer_3 = preload_next_grid(grid_layer_2, grid_layer_3, ap2, 3)
    grid_layer_4 = preload_next_grid(grid_layer_3, grid_layer_4, ap3, 4)
    grid_layer_5 = preload_next_grid(grid_layer_4, grid_layer_5, ap4, 5)
    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = transistor_style_signal_propagation(
        grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
    )
    propagate_to_output_api(grid_layer_5)
    grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
```

### 修改 2: 同步 `ax.py` 的 Point 类

**文件**: `ax.py`

在 Point 类构造函数中添加 `api_signal` 参数，保持与 `app.py` 一致。

### 修改 3: 首次传播前也做一轮 preload

**文件**: `app.py` L896-900

在首次 `transistor_style_signal_propagation` 之前，先做一轮跨层 preload（使用 `detect_active_cells`），确保 API 注入的信号在首次传播时就能被后续层感知。

## 4. 验证步骤

1. **语法检查**: `python -c "compile(open('app.py', encoding='utf-8').read(), 'app.py', 'exec'); print('Syntax OK')"`
2. **环境修复**: 以管理员权限安装 numpy: `pip install numpy --user` 或使用 `--break-system-packages`
3. **运行程序**: `python app.py`
4. **观察输出**:
   - Grid Layer 1 第一行全部为 9
   - Grid Layer 5 最后一行全部为 9
   - [API Output] 二进制信号非全 0
   - [API Output] UTF-8 字符解码成功（应输出中文）
5. **调试脚本**: 如输出仍为全 0，运行 `python debug_inject.py` 逐步排查

## 5. 假设与决策

- **假设**: 网格文件 `Alice_McCord.exdc` 已存在且有效，每层有 256 个随机 Point 节点
- **假设**: `Alice.wtms` 输入文件存在且包含有效的 UTF-8 中文文本
- **决策**: 使用 `detect_active_cells`（检测所有非零单元格）而非 `detect_active_points`（仅检测 Point）作为跨层 preload 的源，确保非 Point 的数字亮度也能传递到下一层
- **决策**: 保留现有的 4 轮多轮传播，但将检测函数改为 `detect_active_cells`