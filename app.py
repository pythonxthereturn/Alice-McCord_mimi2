# -*- coding: utf-8 -*-
#!C:/Users/Administrator/Desktop/Alice McCord/app.py python3
import inspect
class Point:
    def __init__(self, center_index, brightness, asd=None, asd1=None, asd2=None):
        self.center_index = center_index
        self.brightness = brightness
        # 修复可变默认参数坑，每个实例独立生成列表
        self.asd = [] if asd is None else asd    # 控制
        self.asd1 = [] if asd1 is None else asd1 # 输入
        self.asd2 = [] if asd2 is None else asd2 # 输出
qw1 = [0] * 1024
qw2 = [0] * 1024
qw3 = [0] * 1024
qw4 = [0] * 1024
qw5 = [0] * 1024
ax1 = 0
ax2 = 0
ax3 = 0
ax4 = 0
ax5 = 0
ax6 = []
ax7 = []
ax8 = []
ax9 = []
ax10 = []
ax11 = []
ax12 = []
ax13 = 0
ax14 = 0
ax15 = 0
ax16 = 0
while True:
    ax1 = input("input:")
    ax2 = list(ax1)
    for i in ax2:
        ax3 = i.encode("utf-8")# 转化为uTF-8
        ax4 = ''.join(f'{byte:08b}' for byte in ax3)# 转化为二进制
        ax5 = ax4.ljust(32, '0')[:32]
        print(f"'{i}' -> {ax5}")
        ax6.append(ax5)# 暂存二进制
    # 随机池
    for i in range(len(ax6)):
        ax7.append(ax6[i][:8])




    # 遍历整个列表，找所有Point类<9的光源
    for i in range(len(qw1)):
        if inspect.isclass(qw1[i]):
            if qw2[i].brightness == 9:
                ax8.append(i)# 记录哪些需要进行渲染
  
            
    for i in range(len(qw2)):
        if inspect.isclass(qw2[i]):
            if qw2[i].brightness == 9:
                ax9.append(i)# 记录哪些需要进行渲染
   
    for i in range(len(qw3)):
        if inspect.isclass(qw3[i]):
            if qw3[i].brightness == 9:
                ax10.append(i)# 记录哪些需要进行渲染
 
            ax10.append(i)
    for i in range(len(qw4)):
        if inspect.isclass(qw4[i]):
            if qw4[i].brightness == 9:
                ax11.append(i)# 记录哪些需要进行渲染

            ax11.append(i)
    for i in range(len(qw5)):
        if inspect.isclass(qw5[i]):
            if qw5[i].brightness == 9:
                ax12.append(i)# 记录哪些需要进行渲染

    #

    # -----------进行渲染--------------
    # qw1
    for i in ax8:
        cx = i % 32
        cy = i // 32
        ax14 = qw1[i].brightness
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 >= ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw1[ax15], Point):
                        if ax16 > qw1[ax15].brightness:
                            qw1[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw1[ax15]:
                            qw1[ax15] = min(ax16, 9)

    # qw2
    for i in ax9:
        cx = i % 32
        cy = i // 32
        ax14 = qw2[i].brightness
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 >= ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw2[ax15], Point):
                        if ax16 > qw2[ax15].brightness:
                            qw2[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw2[ax15]:
                            qw2[ax15] = min(ax16, 9)

    # qw3
    for i in ax10:
        cx = i % 32
        cy = i // 32
        ax14 = qw3[i].brightness
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 >= ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw3[ax15], Point):
                        if ax16 > qw3[ax15].brightness:
                            qw3[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw3[ax15]:
                            qw3[ax15] = min(ax16, 9)

    # qw4
    for i in ax11:
        cx = i % 32
        cy = i // 32
        ax14 = qw4[i].brightness
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 >= ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw4[ax15], Point):
                        if ax16 > qw4[ax15].brightness:
                            qw4[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw4[ax15]:
                            qw4[ax15] = min(ax16, 9)

    # qw5
    for i in ax12:
        cx = i % 32
        cy = i // 32
        ax14 = qw5[i].brightness
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 >= ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw5[ax15], Point):
                        if ax16 > qw5[ax15].brightness:
                            qw5[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw5[ax15]:
                            qw5[ax15] = min(ax16, 9)




        print("======区块一==========")
        for i in range(0, 32*32,32):
            print(qw1[i:i+32])

        print("\n==========区块2==========")
        for i in range(0, 32*32, 32):
            print(qw2[i:i+32])

        print("\n==========区块3==========")
        for i in range(0, 32*32, 32):
            print(qw3[i:i+32])

        print("\n========== 区块4 ==========")
        for i in range(0, 32*32, 32):
            print(qw4[i:i+32])

        print("\n========== 区块5 ==========")
        for i in range(0, 32*32, 32):
            print(qw5[i:i+32])


