# Tasks

- [x] Task 1: 删除重复的 `render_diamond_light` 函数定义（第 173-208 行）— 恢复第一个正确定义为唯一版本
  - [x] 删除第 173-208 行的重复函数体
  - [x] 确认唯一版本 `render_diamond_light`（第 28 行）使用 `cx + dx` 方向且截断 `min(new_val, MAX_BRIGHTNESS)`

- [x] Task 2: 新增 `collect_brightness_lt_9_points(source_list)` 函数 — 复用 `collect_brightness_1_positions` 模式，返回 brightness < 9 的 Point 对象列表
  - [x] 定义函数，返回 `[item for item in source_list if isinstance(item, Point) and item.brightness < 9]`

- [x] Task 3: 新增 `render_diamond_release(source_list, grid_size=GRID_SIZE)` 函数
  - [x] 构建渲染缓冲区：Point 位置初始 0，其他为原值
  - [x] 仅遍历 `collect_brightness_lt_9_points(source_list)` 的结果，无需 isinstance 判断
  - [x] 菱形扩散方向 `nx = cx - dx`, `ny = cy - dy`（与 `render_diamond_light` 反向）
  - [x] 不做最小值截断（不调用 `min(new_val, 0)`）

- [x] Task 4: 删除 `terminal_loop` 中旧的释放逻辑块（第 120-164 行），替换为 5 区块循环调用 `render_diamond_release`

- [x] Task 5: 运行验证 — 语法检查 + 导入测试确认所有函数可正常调用

# Task Dependencies
- Task 2 无依赖
- Task 3 依赖 Task 2（使用 `collect_brightness_lt_9_points`）
- Task 1 可与 Task 2-3 并行
- Task 4 依赖 Task 1、Task 3
- Task 5 依赖 Task 1-4
