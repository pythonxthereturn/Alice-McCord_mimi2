# Plan: API 信号分离与信号注入

## 1. 问题诊断

当前代码有两个核心问题：

1. **API 节点的 brightness 同时承担"显示"和"信号"两个职责**，导致在任何渲染/传播/清理过程中都可能被意外覆盖，显示值不稳定。
2. **信号根本没有从第一层 API 输入行传递到网络中**。API 节点没有输出连接，也没有机制将其 `api_signal` 注入到 row=1 的普通节点，因此后续所有层都接收不到信号，输出始终全 0。

Code_20260607.txt 明确指出：`brightness` 应仅用于显示（永远为 9），真实信号存储在独立的 `api_signal` 字段中。

## 2. 当前代码状态

- `Point` 类: 无 `api_signal` 属性
- `set_api_input`: brightness 随信号变化（0 或 9），无 api_signal
- `propagate_to_output_api`: brightness 动态设置，非 Point 构造方式
- `get_api_output`: 读 brightness 判断输出
- `guard_api_rows`: 保留旧亮度，不强制设为 9
- `transistor_style_signal_propagation`: API 节点跳过，但无信号注入机制
- 主循环末尾: `initialize_api_ports` 将 API 亮度重置为 0，破坏显示
- `load_full_grid_from_file`: 未传递 api_signal

## 3. 修改清单

### 修改 1: Point 类添加 `api_signal` 字段

**文件**: `app.py` Line 33-45

**改前**:
```python
class Point:
    def __init__(self, center_index: int, brightness: int,
                 control_ports: list | None = None,
                 input_ports: list | None = None,
                 output_ports: list | None = None,
                 is_api: bool = False):
        ...
        self.is_api = is_api
```

**改后**:
```python
class Point:
    def __init__(self, center_index: int, brightness: int,
                 control_ports: list | None = None,
                 input_ports: list | None = None,
                 output_ports: list | None = None,
                 is_api: bool = False,
                 api_signal: int = 0):
        ...
        self.is_api = is_api
        self.api_signal = api_signal
```

### 修改 2: `set_api_input` — 亮度固定为 9，信号存入 api_signal

**文件**: `app.py` Line 609-638

**要点**:
- `brightness=ACTIVE_BRIGHTNESS`（永远 9）
- `api_signal=signal`（真实信号 0 或 9）
- 强制重建 Point 对象

### 修改 3: `propagate_to_output_api` — 亮度固定为 9，信号存入 api_signal

**文件**: `app.py` Line 248-270

**要点**:
- 始终用 `Point()` 构造函数重建目标节点
- `brightness=ACTIVE_BRIGHTNESS`（永远 9）
- `api_signal=signal`（来自上一行的真实信号）

### 修改 4: `get_api_output` — 读取 api_signal

**文件**: `app.py` Line 640-661

**要点**:
- `grid_layer_5[port_index].api_signal >= 5` 替代 `brightness >= 5`
- 修复时也使用 `api_signal=0`

### 修改 5: `guard_api_rows` — 强制 brightness=9

**文件**: `app.py` Line 165-183

**要点**:
- 不再保留旧亮度，直接强制设为 `ACTIVE_BRIGHTNESS`
- 新建节点时传入 `api_signal=0`

### 修改 6: `transistor_style_signal_propagation` — 第一层 API 信号注入

**文件**: `app.py` Line 540-553

**关键逻辑**: 在计算 `input_signals` 后，对第一层第 2 行（row=1）的节点，额外读取正上方 API 节点的 `api_signal` 并加入 input_signals。

**插入位置**: 在 `input_signals = []` 收集循环之后，`control_triggered` 检查之前。

**插入代码**:
```python
# 第一层：从 API 行直接注入信号给第二行（row=1）的节点
if current_layer == 1:
    row = i // GRID_SIDE_LENGTH
    if row == 1:
        col = i % GRID_SIDE_LENGTH
        api_idx = col
        if isinstance(grid[api_idx], Point) and grid[api_idx].is_api:
            api_sig = grid[api_idx].api_signal
            if api_sig > 0:
                input_signals.append(api_sig)
```

### 修改 7: 移除主循环末尾的 `initialize_api_ports` 调用

**文件**: `app.py` Line 921

**要点**: 删除 `grid_layer_1, grid_layer_5 = initialize_api_ports(grid_layer_1, grid_layer_5)` 这一行。`guard_api_rows` 已在上一行执行，足够保护 API 行。

### 修改 8: `load_full_grid_from_file` — 传递 api_signal

**文件**: `app.py` Line 687-694

**要点**: 在 Point 重建时添加 `api_signal=getattr(cell, 'api_signal', 0)`

## 4. 信号传输链路验证

修改后的完整信号链路：

1. `set_api_input` → API 节点 `.brightness=9, .api_signal=信号`
2. `transistor_style_signal_propagation` 第一层 → row=1 普通节点直接读 `.api_signal`
3. 普通节点通过连接/预加载将信号向下传递
4. 第五层 row=30 节点亮度在信号传播后更新
5. `propagate_to_output_api` 将 row=30 亮度写入输出 API 的 `.api_signal`
6. `get_api_output` 读 `.api_signal`，非 `.brightness`
7. 所有阶段后 `guard_api_rows` 确保 API 行一直显示为 9

## 5. 验证步骤

1. `python -c "compile(open('app.py', encoding='utf-8').read(), 'app.py', 'exec'); print('Syntax OK')"` — 语法检查
2. `python app.py` — 运行程序，观察：
   - Grid Layer 1 第一行全部为 9
   - Grid Layer 5 最后一行全部为 9
   - [API Output] 二进制信号非全 0
   - [API Output] UTF-8 字符解码成功