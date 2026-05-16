# API输入分离 + 渲染Bug修复 + API端口信号定义 修正计划

## 问题分析

用户指出了3个核心问题：

### 问题1：用户输入和API输入共用同一个输入（最关键）

**现状**：主循环中只有一个 `input("input:")` 调用，用户输入的字符串同时被用于：
- 构建随机池（`build_random_pool`）
- 写入API输入端口（`set_api_input`）

**用户要求**：
- 先让用户输入用于随机池/处理逻辑的字符串
- 然后再让用户**单独**输入用于API的二进制字符串
- 两个输入不能共用

**修正方案**：
- 第一个 `input("input:")` → 用于随机池构建（原有逻辑）
- 新增第二个 `input("api_input:")` → 用于API输入端口的32位二进制字符串
- 删除当前 `set_api_input(grid_1, binary_string_list[0])` 这行（不再从binary_string_list取第一个字符）

### 问题2：渲染逻辑有Bug

**现状**：`render_grid` 函数中，活跃点检测只找 `brightness == 9` 的Point。但API输入端口设置brightness为0或9后，brightness=9的端口会被检测为活跃点并参与渲染，而brightness=0的端口不会。这本身逻辑正确。

**但真正的Bug是**：`set_api_input` 在阶段A中调用，此时设置brightness=9的端口，会在阶段B被检测为活跃点，然后在阶段C被渲染。但**退火阶段D**又会把这些brightness=9的API端口的扩散区域全部退火归零。最终阶段E `clear_non_point_brightness` 清理所有非Point位置的数字。

**核心问题**：API输入端口的brightness=9信号在退火后会被清零（因为退火会把扩散区域的Point brightness减回去），导致信号无法传递下去。

**修正方案**：
- API输入端口（grid_1[0~31]）在 `set_api_input` 设置brightness后，需要在每个端口的 `input_ports` 列表中记录信号值
- 退火逻辑不应影响API输入端口本身的brightness（或者需要在退火后恢复API端口的信号）
- 更准确地说：API端口是信号源，它们的brightness应该作为信号传递的起点，不应该被退火清零

**实际修正**：在 `set_api_input` 中，除了设置brightness，还需要在每个端口的 `input_ports` 中添加一条信号记录（单向，不需要双向连接），这样即使brightness被退火修改，信号信息仍然保留在 `input_ports` 中。

### 问题3：API端口Point的input_ports中没有信号记录

**现状**：`set_api_input` 只设置了brightness，没有在Point的 `input_ports` 中记录信号。

**用户要求**：
- API端口Point的 `input_ports` 中需要定义信号（只需要第一个信号）
- API端口是调试用的，不需要双向连接
- 但正常逻辑的Point仍然需要双向连接

**修正方案**：
- 在 `set_api_input` 中，为每个API端口Point的 `input_ports` 添加一条信号记录：
  ```python
  {
      "block_name": "api_input",
      "port_identifier": "input",
      "source_point_index": -1,  # 外部输入，无源Point
      "target_point_index": port_index,
      "signal": signal_value  # 0或9
  }
  ```
- 这是一条单向记录，不需要在对方Point建立反向连接

## 具体修改步骤

### 步骤1：修改主循环 - 分离两个输入

**位置**：主循环阶段A（第601~629行）

**修改内容**：
```python
# 第一个输入：用于随机池构建
user_input_raw = input("input:")
input_character_list = list(user_input_raw)
binary_string_list = []

for i in input_character_list:
    unicode_encoded_bytes = i.encode("utf-8")
    binary_string = ''.join(f'{byte:08b}' for byte in unicode_encoded_bytes)
    padded_binary_string = binary_string.ljust(32, '0')[:32]
    print(f"'{i}' -> {padded_binary_string}")
    binary_string_list.append(padded_binary_string)

# 构建随机池（仅用第一个输入）
random_pool = build_random_pool(binary_string_list)

# 第二个输入：用于API输入端口
api_input_string = input("api_input:")
set_api_input(grid_1, api_input_string)
```

删除原来的 `if len(binary_string_list) > 0: set_api_input(grid_1, binary_string_list[0])`

### 步骤2：修改 set_api_input - 添加input_ports信号记录

**位置**：`set_api_input` 函数（第438~472行）

**修改内容**：
- 在设置brightness的同时，为每个API端口Point的 `input_ports` 添加一条信号记录
- 先清空该Point的 `input_ports`（避免重复添加），然后添加新的信号记录
- 信号记录是单向的，不需要在对方Point建立反向连接

```python
def set_api_input(grid_1, binary_string):
    # ... 参数校验 ...
    for port_index in range(32):
        char = binary_string[port_index]
        if char == '1':
            signal_value = 9
        elif char == '0':
            signal_value = 0
        # ... 错误处理 ...

        if isinstance(grid_1[port_index], Point):
            grid_1[port_index].brightness = signal_value
            # 清空旧的API信号记录，添加新的单向信号记录
            grid_1[port_index].input_ports.clear()
            grid_1[port_index].input_ports.append({
                "block_name": "api_input",
                "port_identifier": "input",
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value
            })
        else:
            grid_1[port_index] = Point(center_index=port_index, brightness=signal_value)
            grid_1[port_index].input_ports.append({
                "block_name": "api_input",
                "port_identifier": "input",
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value
            })
    # ...
```

### 步骤3：修改 set_api_input - 支持任意长度二进制字符串

当前要求必须32位，但用户可能输入不同长度的字符串。应自动补齐或截断到32位。

```python
# 自动补齐到32位
if len(binary_string) < 32:
    binary_string = binary_string.ljust(32, '0')
elif len(binary_string) > 32:
    binary_string = binary_string[:32]
```

### 步骤4：验证渲染逻辑

渲染逻辑本身（`render_grid`）的菱形扩散算法是正确的：
- `manhattan_distance < source_brightness` → 跳过边界外
- `computed_brightness = source_brightness - manhattan_distance` → 正确的亮度衰减
- `max(原亮度, 计算亮度)` → 正确的加法操作
- Point对象只修改brightness，不覆盖 → 正确

渲染的"Bug"实际上是因为API输入端口brightness=9后，在退火阶段被清零，导致信号无法传递。这不是渲染本身的Bug，而是API信号在退火后丢失的问题。通过步骤2在 `input_ports` 中记录信号，可以保证信号信息不丢失。

## 修改文件清单

| 文件 | 修改位置 | 修改内容 |
|------|----------|----------|
| app.py | 主循环阶段A（第611~629行） | 分离为两个input调用，删除从binary_string_list取API输入的逻辑 |
| app.py | set_api_input函数（第438~472行） | 添加input_ports信号记录，支持自动补齐32位 |

## 不修改的部分

- Point类定义
- build_random_pool函数
- detect_active_points函数
- clear_non_point_brightness函数
- diamond_render_single_point函数
- render_grid函数
- anneal_and_connect函数
- preload_next_grid函数
- display_grid函数
- get_api_output函数
- propagate_signals函数
- 全局变量初始化
- 种子点放置
- API端口初始化
- 主循环的阶段B~J（除阶段A外）
