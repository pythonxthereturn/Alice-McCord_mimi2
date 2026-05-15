# Tasks

- [x] Task 1: 重命名全局网格数组 — 将 `qw1`-`qw5` 全文替换为 `grid_1`-`grid_5`，覆盖变量声明、所有引用、字符串中包含的 "qw1"-"qw5"
  - [x] 替换变量声明 `qw1`-`qw5` → `grid_1`-`grid_5`
  - [x] 替换所有 `isinstance(qwN[...], Point)` → `isinstance(grid_N[...], Point)`
  - [x] 替换所有 `qwN[i].brightness` → `grid_N[i].brightness`
  - [x] 替换所有 `qwN[i].asd`/`.asd1`/`.asd2` → `grid_N[i].control_ports`/`.input_ports`/`.output_ports`
  - [x] 替换绑定记录字典中 `"b": "qwN"` → `"block_name": "grid_N"`
  - [x] 替换所有 `qwN[target_flat_index]` 形式的引用

- [x] Task 2: 重命名 Point 类属性 — `asd`/`asd1`/`asd2` → `control_ports`/`input_ports`/`output_ports`
  - [x] 修改 Point.__init__ 参数名和属性名
  - [x] 全文替换 `len(grid_N[...].asd)` → `len(grid_N[...].control_ports)`
  - [x] 全文替换 `.asd1` → `.input_ports`
  - [x] 全文替换 `.asd2` → `.output_ports`

- [x] Task 3: 重命名全局辅助变量 `ax1`-`ax12` → 完整英文单词（无缩写）
  - [x] `ax1` → `user_input_raw`
  - [x] `ax2` → `input_character_list`
  - [x] `ax3` → `unicode_encoded_bytes`
  - [x] `ax4` → `binary_string`
  - [x] `ax5` → `padded_binary_string`
  - [x] `ax6` → `binary_string_list`
  - [x] `ax7` → `random_pool`
  - [x] `ax8` → `active_points_grid_1`
  - [x] `ax9` → `active_points_grid_2`
  - [x] `ax10` → `active_points_grid_3`
  - [x] `ax11` → `active_points_grid_4`
  - [x] `ax12` → `active_points_grid_5`

- [x] Task 4: 重命名全局复用变量 `ax13`-`ax18`、`ax20`-`ax21` → 完整英文单词（无缩写）
  - [x] `ax13` → `manhattan_distance`
  - [x] `ax14` → `source_brightness`
  - [x] `ax15` → `target_flat_index`
  - [x] `ax16` → `computed_brightness`
  - [x] `ax17` → `block_modified_flag`
  - [x] `ax18` → `current_binary_string`
  - [x] `ax19` → 移除声明
  - [x] `ax20` → `port_type`
  - [x] `ax21` → `port_label`

- [x] Task 5: 重命名循环内局部变量 — `cx`/`cy`/`nx`/`ny`/`dx`/`dy`/`i`/`a`
  - [x] `cx` → `column_x`
  - [x] `cy` → `row_y`
  - [x] `dx` → `delta_x`
  - [x] `dy` → `delta_y`
  - [x] `nx` → `neighbor_x`
  - [x] `ny` → `neighbor_y`
  - [x] `i` → `point_index`（渲染/退火/预加载循环）
  - [x] `a` → `offset_counter`

- [x] Task 6: 重命名绑定字典键名 — `"b"`/`"i"`/`"a1"`/`"a3"` → 完整英文单词
  - [x] `"b":` → `"block_name":`
  - [x] `"i":` → `"port_identifier":`
  - [x] `"a1":` → `"source_point_index":`
  - [x] `"a3":` → `"target_point_index":`
  - [x] 端口标识符字符串值 `"a1"`/`"a2"`/`"a3"` → `"control"`/`"input"`/`"output"`

- [x] Task 7: 精简退火四方向绑定逻辑 — 减少冗余嵌套，保持执行顺序和逻辑不变

- [x] Task 8: 确认 PW4 和 PW5 预加载逻辑完整且一致
  - [x] grid_4 预加载段存在且使用 `neighbor_y < 3`
  - [x] grid_5 预加载段存在且使用 `neighbor_y < 3`
  - [x] 两段逻辑的菱形扩散算法完全一致

- [x] Task 9: 清理冗余注释、分隔符、多余空行

- [x] Task 10: 运行验证
  - [x] `python -m py_compile app.py` exit code 0
  - [x] 无未定义变量引用

# Task Dependencies
- Task 2 depends on Task 1
- Task 6 depends on Task 1, 2
- Task 7 depends on Task 3, 4, 5, 6
- Task 8 depends on Task 1, 3
- Task 10 depends on Task 1-9
</</parameter>