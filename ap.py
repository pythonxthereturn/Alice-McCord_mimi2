def index_to_xy(index: int, grid_size: int = 32, start_from: int = 1) -> tuple[int, int]:
    if start_from == 1:
        index = index - 1  # 转换成0基索引方便计算
    row = index // grid_size  # 行号（y轴）
    col = index % grid_size   # 列号（x轴）
    return col, row


def manhattan_step(xy1: tuple[int, int], xy2: tuple[int, int]) -> int:
    """计算四向移动的最短步数（曼哈顿距离）"""
    x1, y1 = xy1
    x2, y2 = xy2
    return abs(x1 - x2) + abs(y1 - y2)


def chebyshev_step(xy1: tuple[int, int], xy2: tuple[int, int]) -> int:
    """计算八向移动的最短步数（切比雪夫距离）"""
    x1, y1 = xy1
    x2, y2 = xy2
    return max(abs(x1 - x2), abs(y1 - y2))


# -------------- 测试你的需求 --------------
if __name__ == "__main__":
    GRID_SIZE = 32
    # 你的两个序号
    idx1 = 23
    idx2 = 64

    # 转换坐标
    xy1 = index_to_xy(idx1, GRID_SIZE)
    xy2 = index_to_xy(idx2, GRID_SIZE)

    # 计算步数
    step_4dir = manhattan_step(xy1, xy2)
    step_8dir = chebyshev_step(xy1, xy2)

    # 输出结果
    print(f"序号{idx1}的网格坐标: {xy1}")
    print(f"序号{idx2}的网格坐标: {xy2}")
    print(f"四向移动（上下左右）最短步数: {step_4dir}")
    print(f"八向移动（可斜走）最短步数: {step_8dir}")