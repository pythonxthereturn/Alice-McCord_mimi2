# Checklist

- [x] 所有 `qw1`-`qw5` 已替换为 `grid_1`-`grid_5`，无遗漏
- [x] Point 类属性 `asd`/`asd1`/`asd2` 已重命名为 `control_ports`/`input_ports`/`output_ports`
- [x] 变量 `ax1`-`ax12` 已全部替换为完整英文单词（无缩写）：`user_input_raw`, `input_character_list`, `unicode_encoded_bytes`, `binary_string`, `padded_binary_string`, `binary_string_list`, `random_pool`, `active_points_grid_1`-`active_points_grid_5`
- [x] 变量 `ax13`-`ax18`、`ax20`-`ax21` 已替换为完整英文单词（无缩写）：`manhattan_distance`, `source_brightness`, `target_flat_index`, `computed_brightness`, `block_modified_flag`, `current_binary_string`, `port_type`, `port_label`
- [x] 未使用变量 `ax19` 已移除
- [x] 循环局部变量 `cx`/`cy`/`nx`/`ny`/`dx`/`dy` 已重命名为完整英文单词：`column_x`/`row_y`/`neighbor_x`/`neighbor_y`/`delta_x`/`delta_y`
- [x] 循环索引 `i`（退火/渲染/预加载用）已重命名为 `point_index`
- [x] 内循环 `a` 已重命名为 `offset_counter`
- [x] 绑定字典键名 `"b"`/`"i"`/`"a1"`/`"a3"` 已替换为完整英文单词：`"block_name"`/`"port_identifier"`/`"source_point_index"`/`"target_point_index"`
- [x] 端口标识符字符串值 `"a1"`/`"a2"`/`"a3"` 已替换为 `"control"`/`"input"`/`"output"`
- [x] 退火四方向绑定逻辑已精简为平铺直叙写法，执行顺序（上→下→左→右）不变
- [x] PW4（grid_4）预加载逻辑完整保留，使用 `neighbor_y < 3`
- [x] PW5（grid_5）预加载逻辑与 PW4 完全一致，使用 `neighbor_y < 3`
- [x] 所有数据流绑定关系保持不变（`binary_string_list` → `random_pool`、`active_points_grid_N` 收集、网格渲染/退火/预加载/绑定流程）
- [x] 未新增任何外部函数，所有逻辑保持内嵌在 while 循环中
- [x] 未删除原有核心功能，未修改代码运行效果
- [x] 中文注释已替换为规范英文注释
- [x] 无意义分隔符和多余空行已清理
- [x] 所有变量名均使用完整英文单词，无任何缩写
- [x] `python -m py_compile app.py` 语法检查通过（exit code 0）
- [x] 无未定义变量引用（NameError）
</</parameter>