# 释放退还逻辑 Spec

## Why
当前 `terminal_loop` 中有一段 "释放退还逻辑"（第 120-164 行），存在以下问题：
1. 只处理 `light_sources_1`，未覆盖 5 个区块
2. `min(new_val, 0)` 将所有值截断为 ≤0，逻辑有误
3. 存在两个重复的 `render_diamond_light` 函数定义（函数重载导致第一个被覆盖）
4. 释放时对所有 Point 遍历，未过滤 — 节省开销

需要修复并完善释放逻辑，使其正确作用于 5 个区块。

## What Changes
- 将覆盖掉的第一个 `render_diamond_light` 合并恢复（原第 173 行的重复函数是修改过的释放版本，需清理）
- 新增 `collect_brightness_lt_9_points(source_list)` — 收集 brightness < 9 的 Point（复用 `collect_brightness_1_positions` 的模式但返回 Point 对象而非索引）
- 新增 `render_diamond_release(source_list)` — 菱形释放渲染，逻辑与 `render_diamond_light` 对称但方向相反（`cx - dx`），且不做 `<0` 截断
- 在 `terminal_loop` 中对 5 个区块循环调用释放逻辑
- 移除释放逻辑中冗余的 isinstance 识别过滤（由 `collect_brightness_lt_9_points` 预处理，无需在渲染中再判）

## Impact
- Affected specs: refactor-app-code（关联但不冲突）
- Affected code: `app.py` 第 120-208 行（释放逻辑块 + 重复函数定义）

## ADDED Requirements
### Requirement: 收集 brightness < 9 的 Point
系统 SHALL 提供 `collect_brightness_lt_9_points(source_list)` 函数，返回所有 brightness < 9 的 Point 对象列表。

#### Scenario: 过滤非满亮度光源
- **WHEN** 调用 `collect_brightness_lt_9_points(light_sources_1)`
- **THEN** 返回仅包含 brightness 为 1~8 的 Point 对象列表，跳过 brightness == 9 和整数 0

### Requirement: 菱形释放渲染
系统 SHALL 提供 `render_diamond_release(source_list, grid_size=GRID_SIZE)` 函数，以菱形扩散模式执行亮度释放。

- 渲染缓冲区初始值：每个格子若为 Point 则为 0，否则为原值
- 扩散方向：`nx = cx - dx`, `ny = cy - dy`（与 `render_diamond_light` 的 `cx + dx` 方向相反）
- 新亮度值：`light_level - dist`
- 不做最小值截断（不调用 `min(new_val, 0)`）
- 遍历仅限 `collect_brightness_lt_9_points` 的结果，不做 isinstance 判断

#### Scenario: 释放一个 brightness=5 的光源
- **WHEN** 对含单个 brightness=5 Point 的 source_list 调用释放渲染
- **THEN** 以该点为中心菱形扩散，各格子值为 `5 - distance`，不做 <0 截断

### Requirement: 5 区块统一释放
系统 SHALL 在 `terminal_loop` 中对 5 个 `light_sources_1` ~ `light_sources_5` 分别执行释放逻辑。

## REMOVED Requirements
### Requirement: 重复的 render_diamond_light 函数定义
**Reason**: 第 173-208 行的重复 `render_diamond_light` 是修改过的释放版本，覆盖了第 28 行的正确定义。需删除重复定义，用专门的 `render_diamond_release` 替代。
**Migration**: 将释放逻辑从重复函数中提取到新的 `render_diamond_release`。
