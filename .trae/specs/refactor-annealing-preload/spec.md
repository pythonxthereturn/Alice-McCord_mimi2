# 重构退火逻辑与预加载机制 - Product Requirement Document

## Overview
- **Summary**: 修复现有代码的语法错误，重构退火逻辑中的方向连接部分，添加预加载机制，保持原有代码风格和变量命名。
- **Purpose**: 解决语法错误导致的无法运行问题，实现区块间的预加载逻辑。
- **Target Users**: 项目开发团队

## Goals
- 修复 qw1 退火逻辑中的所有语法错误
- 正确实现方向连接记录功能
- 为 qw2-qw5 应用相同的退火和连接逻辑
- 实现 qw1→qw2、qw2→qw3、qw3→qw4、qw4→qw5 的预加载机制
- 保持原有代码风格、变量命名和注释格式

## Non-Goals (Out of Scope)
- 不修改 qw5 的预加载逻辑
- 不修改渲染阶段的现有代码
- 不重构打印显示逻辑

## Background & Context
- 现有代码在 qw1 的退火逻辑（L210-402）存在多处语法错误
- 需要将 qw1 的逻辑（修复后）应用到 qw2-qw5
- 添加预加载机制：每个区块完成后预加载下一区块的内容

## Functional Requirements
- **FR-1**: 修复 qw1 退火逻辑中的语法错误
- **FR-2**: 正确实现方向连接记录功能（上下左右四个方向）
- **FR-3**: 为 qw2-qw5 应用修复后的退火和连接逻辑
- **FR-4**: 实现 qw1 预加载 qw2、qw2 预加载 qw3、qw3 预加载 qw4、qw4 预加载 qw5 的机制

## Non-Functional Requirements
- **NFR-1**: 保持原有的代码风格、缩进、变量命名和注释格式
- **NFR-2**: 原有变量和逻辑结构最大化保留

## Constraints
- **Technical**: Python 3，不引入外部依赖
- **Dependencies**: 现有 Point 类和全局变量结构

## Assumptions
- ax7 的内容会正确提供连接属性
- "预加载前三行"指的是渲染下一区块的前三行（y坐标 0、1、2）
- 预加载逻辑与原有渲染逻辑一致

## Acceptance Criteria

### AC-1: 语法错误修复
- **Given**: app.py 文件
- **When**: 运行 Python 解释器检查语法
- **Then**: 不报错，可以正常执行到输入环节
- **Verification**: `programmatic`

### AC-2: 方向连接记录
- **Given**: 区块中有 Point 实例且满足连接条件
- **When**: 执行退火逻辑后
- **Then**: 连接信息正确记录到两个 Point 的 asd2 列表中
- **Verification**: `programmatic`

### AC-3: qw2-qw5 退火逻辑
- **Given**: qw2-qw5 中有 Point 实例
- **When**: 执行退火逻辑后
- **Then**: 退火逻辑应用与 qw1 一致
- **Verification**: `programmatic`

### AC-4: 预加载机制
- **Given**: 完成一个区块的渲染和退火
- **When**: 执行预加载步骤
- **Then**: 下一区块的前三行被正确预加载
- **Verification**: `programmatic`

## Open Questions
- [ ] ax7 的具体内容和长度是多少？
- [ ] "预加载前三行"的精确逻辑是只处理 y 坐标 < 3 的区域，还是其他？
