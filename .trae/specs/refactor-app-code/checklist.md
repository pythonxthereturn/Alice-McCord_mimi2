# Checklist

- [x] 全局变量 `qw1`-`qw5` 已重命名为 `light_sources_1`-`light_sources_5`，所有引用同步更新
- [x] 全局变量 `final_grid1`-`final_grid5` 已重命名为 `rendered_grid_1`-`rendered_grid_5`，所有引用同步更新
- [x] 循环变量 `qwer1`、`qwera1`-`qwera5` 已重命名为有意义名称
- [x] 魔术数字 `200`、`24`、`5`、`30` 等已常量化
- [x] `create_staggered_points()` 函数已定义，5 组 brightness=1 初始化改为函数调用
- [x] `handle_terminal_input()` 函数已从 `terminal_loop` 中提取
- [x] `collect_brightness_1_positions()` 函数已从 `terminal_loop` 中提取
- [x] `print_positions_block()` 函数已从 `terminal_loop` 中提取
- [x] `terminal_loop` 函数行数显著减少，仅负责流程编排
- [x] `create_grid_rectangles()` 公共函数已定义，`RedStackedWindow` 和 `GreenIndependentWindow` 均调用它
- [x] `Point` 类的 `asd`/`asd1`/`asd2` 属性已移除
- [x] `print_grid` 函数已移除
- [x] `python app.py` 语法无错误
- [x] Tkinter 双窗口正常弹出，光场渲染视觉效果与重构前一致
