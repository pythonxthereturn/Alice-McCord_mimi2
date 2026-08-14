from typing import List, Optional, Tuple
# 全局随机池模块

class RandomPool:
    # 方向映射
    # 1 2 3 4
    # 上 下 左 右
    DIRECTION_MAP = {
        1: (0, -1),     # 上
        2: (0, 1),      # 下
        3: (-1, 0),     # 左
        4: (1, 0),      # 右
    }

    # 连接类型映射：1~2=输入端, 3~4=输出端, 5~6=控制端
    CONN_TYPE_MAP = {
        1: 'input',
        2: 'input',
        3: 'output',
        4: 'output',
        5: 'control',
        6: 'control',
    }

    def __init__(self):
        # 初始化随机池，空池，指针指向0
        self._pool: List[int] = []
        self._pointer: int = 0

    @property
    def size(self) -> int:
        # 随机池大小
        return len(self._pool)

    @property
    def is_empty(self) -> bool:
        # 随机池是否为空
        return len(self._pool) == 0

    def add_values(self, values: List[int]):
        # 向随机池追加数值
        self._pool.extend(values)

    def add_parsed_input(self, input_str: str, delimiter: str = ','):
    
        # 输入拆分存入随机池
        parts = input_str.split(delimiter)
        values = []

        for part in parts:
            part = part.strip()
            if not part:
                continue
            try:
                num = int(part)
            except ValueError:
                continue

            if num > 6:
                while num > 6:
                    values.append(6)
                    num -= 6
                values.append(num)
            else:
                values.append(num)

        self._pool.extend(values)

    def next(self) -> Optional[int]:
        # 共用全局指针
        # 指针复位，防止内存泄漏
        if self.is_empty:
            return None

        value = self._pool[self._pointer]
        self._pointer += 1
        if self._pointer >= len(self._pool):
            self._pointer = 0
        return value

    def next_direction(self) -> Optional[Tuple[int, int]]:
        #映射为方向偏移量

        value = self.next()
        if value is None:
            return None
        # 仅1~4映射为方向，非1~4的值取模映射
        key = ((value - 1) % 4) + 1
        return self.DIRECTION_MAP[key]

    def next_conn_type(self) -> Optional[str]:
        
        # 映射为连接类型
        value = self.next()
        if value is None:
            return None
        key = ((value - 1) % 6) + 1
        return self.CONN_TYPE_MAP[key]

    def peek(self) -> Optional[int]:
        # 指针检测偏移量
        if self.is_empty:
            return None
        return self._pool[self._pointer]

    def reset_pointer(self):
        # 指针复位
        self._pointer = 0

    def clear(self):
        # 清空随机池和指针
        self._pool.clear()
        self._pointer = 0

    def get_remaining_count(self) -> int:
        # 获取从当前指针到末尾的剩余可取值数量
        if self.is_empty:
            return 0
        return len(self._pool) - self._pointer

    def __repr__(self) -> str:
        return (f"RandomPool(size={len(self._pool)}, "
                f"pointer={self._pointer}, "
                f"next={self.peek()})")