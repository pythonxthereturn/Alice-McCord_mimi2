# Checklist

- [x] 重复的 `render_diamond_light` 函数（第 173-208 行）已删除，只剩第 28 行的唯一定义
- [x] `render_diamond_light` 使用 `cx + dx` 方向，截断 `min(new_val, MAX_BRIGHTNESS)`
- [x] `collect_brightness_lt_9_points()` 函数已定义，返回 brightness < 9 的 Point 对象列表
- [x] `render_diamond_release()` 函数已定义
- [x] 释放渲染缓冲区初始化为 Point→0，非 Point→原值
- [x] 释放渲染仅遍历 `collect_brightness_lt_9_points()` 结果，无 isinstance 判断
- [x] 释放渲染菱形方向 `nx = cx - dx`, `ny = cy - dy`
- [x] 释放渲染不做最小值截断（无 `min(new_val, 0)`）
- [x] `terminal_loop` 中旧的释放逻辑块已删除
- [x] `terminal_loop` 对 5 个区块分别调用 `render_diamond_release`
- [x] `python app.py` 语法无错误
- [x] 所有函数可正常导入调用
