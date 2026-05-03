# 修复计划：找出 brightness 值为 1 的位置

## 问题分析

### 根本原因
`qw1` 到 `qw5` 列表初始化时是 `[0] * 1024`，大部分元素是整数 `0`，只有少数位置被赋值为 `Point` 对象。当代码直接访问 `.brightness` 属性时，如果元素是整数就会报错：
```
AttributeError: 'int' object has no attribute 'brightness'
```

### 当前代码状态
- `qw1` 循环：已修复 ✓
- `qw2` 循环：未修复 ✗（缺少 isinstance 检查）
- `qw3` 循环：未修复 ✗（缺少 isinstance 检查，且 append 使用错误）
- `qw4` 循环：未修复 ✗（缺少 isinstance 检查）
- `qw5` 循环：已修复 ✓

## 修复方案

为所有循环添加 `isinstance()` 检查，确保只在元素是 `Point` 对象时才访问 `.brightness` 属性。

### 修改文件
- `app.py` 第 191-215 行

### 修改步骤
1. 在 `qw2` 循环中添加 isinstance 检查
2. 在 `qw3` 循环中添加 isinstance 检查，并修复 `append[int(z3)]` 为 `append(z3)`
3. 在 `qw4` 循环中添加 isinstance 检查

## 预期结果
修复后，代码将正确遍历列表，跳过整数元素，只检查 `Point` 对象，并记录 brightness 值为 1 的位置。