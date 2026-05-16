# 修复 Display 输出位置错误，确保退火后显示归零结果 Spec

## Why
当前 `app.py` 中存在两个完全相同的 Display Output 代码块（打印 5 个 Grid 的 32x32 亮度矩阵）。第一个位于 Rendering（渲染）之后、Annealing（退火）之前（第 221-270 行），导致用户看到的输出是渲染后的菱形扩散图案，而非退火归零后的结果。这使得退火逻辑看似完全失效——输出显示仍然是菱形图案，"退了跟没退一样"。

## What Changes
- **删除**第一个 Display Output 代码块（第 221-270 行），该块位于 Rendering 和 Annealing 之间
- **保留**第二个 Display Output 代码块（第 1213-1260 行），该块位于 Annealing 之后，确保显示的是退火归零后的正确结果
- 不修改渲染逻辑、不退火逻辑、不修改绑定逻辑
- 不修改变量名、不提取函数

## Impact
- Affected specs: 无
- Affected code: `app.py` 第 221-270 行（删除5个Grid的打印块 + 中间的空白行）

## REMOVED Requirements

### Requirement: 渲染后立即显示输出
**Reason**: Display 位置错误——输出出现在 Rendering 之后、Annealing 之前，导致用户看到错误状态（渲染菱形图案），误以为退火失效。正确顺序应为 Rendering → Annealing → Display。
**Migration**: 删除该段代码，保留 Annealing 之后的 Display 输出。
</</parameter>