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
ax17 = False
ax18 = 0
ax19 = 0
qw1[400] = Point(center_index=400, brightness=9)
qw1[399] = Point(center_index=390, brightness=9)







while True:
    # 修改1：每次循环开始清空所有待处理列表，防止累积
    ax8.clear()
    ax9.clear()
    ax10.clear()
    ax11.clear()
    ax12.clear()
    ax6.clear()
    ax7.clear()
    
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
        ax18 = list[ax6[i]]
        ax7.append(ax18[0] + ax18[1] + ax18[2] + ax18[3])
        ax7.append(ax18[4] + ax18[5] + ax18[6] + ax18[7])
        ax7.append(ax18[8] + ax18[9] + ax18[10] + ax18[11])
        ax7.append(ax18[12] + ax18[13] + ax18[14] + ax18[15])
        ax7.append(ax18[16] + ax18[17] + ax18[18] + ax18[19])
        ax7.append(ax18[20] + ax18[21] + ax18[22] + ax18[23])
        ax18 =+ 1
    
    # 遍历整个列表，找所有brightness == 9的Point实例
    for i in range(len(qw1)):
        if isinstance(qw1[i], Point):
            if qw1[i].brightness == 9:
                # 修改2：保存索引和原始亮度，防止退火时互相覆盖
                ax8.append( (i, qw1[i].brightness) )
  
            
    for i in range(len(qw2)):
        if isinstance(qw2[i], Point):
            if qw2[i].brightness == 9:
                ax9.append( (i, qw2[i].brightness) )
   
    for i in range(len(qw3)):
        if isinstance(qw3[i], Point):
            if qw3[i].brightness == 9:
                ax10.append( (i, qw3[i].brightness) )
 
    for i in range(len(qw4)):
        if isinstance(qw4[i], Point):
            if qw4[i].brightness == 9:
                ax11.append( (i, qw4[i].brightness) )
    for i in range(len(qw5)):
        if isinstance(qw5[i], Point):
            if qw5[i].brightness == 9:
                ax12.append( (i, qw5[i].brightness) )
    #
    # -----------进行渲染--------------
    # qw1
    for i, _ in ax8:
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
    for i, _ in ax9:
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
    for i, _ in ax10:
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
    for i, _ in ax11:
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
    for i, _ in ax12:
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
                    # ----
       
    # ------------------退火-----------------
    for i, ax14 in ax8:  # 直接使用保存的原始亮度
        cx = i % 32
        cy = i // 32
        block_modified = False  # 每个区块开头重新初始化，绝对独立
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 > ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = -(ax14 - ax13)
                    changed = False
                    if isinstance(qw1[ax15], Point):
                        # 修改3：把 < 改成 <=，彻底清除残留的1
                        if ax16 <= qw1[ax15].brightness:
                            qw1[ax15].brightness = max(ax16, 0)
                            changed = True
                    else:
                        # 同样改成 <=
                        if ax16 <= qw1[ax15]:
                            qw1[ax15] = max(ax16, 0)
                            changed = True
                    if changed:
                        block_modified = True
        if block_modified:  # ax8 ax18 ax7
            # 上下左右
            # 1 2 3 4
            if ax7[i] == 1:  # 上
                target_idx = i + 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw1[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw1[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw1[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw1[i].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw1[target_idx].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
                        
            if ax7[i] == 1:  # 下
                target_idx = i - 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw1[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw1[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw1[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw1[i].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw1[target_idx].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 左
                target_idx = i - 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw1[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw1[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw1[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw1[i].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw1[target_idx].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 右
                target_idx = i + 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw1[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw1[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw1[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw1[i].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw1[target_idx].asd2.append({
                                    "b": "qw1",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
    # 预加载qw2
    for i, _ in ax9:
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
                if 0 <= nx < 32 and 0 <= ny < 3:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw2[ax15], Point):
                        if ax16 > qw2[ax15].brightness:
                            qw2[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw2[ax15]:
                            qw2[ax15] = min(ax16, 9)
    # -----------
    # qw2
    for i, ax14 in ax9:  # 直接使用保存的原始亮度
        cx = i % 32
        cy = i // 32
        block_modified = False  # 每个区块开头重新初始化，绝对独立
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 > ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = -(ax14 - ax13)
                    changed = False
                    if isinstance(qw2[ax15], Point):
                        # 修改3：把 < 改成 <=，彻底清除残留的1
                        if ax16 <= qw2[ax15].brightness:
                            qw2[ax15].brightness = max(ax16, 0)
                            changed = True
                    else:
                        # 同样改成 <=
                        if ax16 <= qw2[ax15]:
                            qw2[ax15] = max(ax16, 0)
                            changed = True
                    if changed:
                        block_modified = True
        if block_modified:  # ax8 ax18 ax7
            # 上下左右
            # 1 2 3 4
            if ax7[i] == 1:  # 上
                target_idx = i + 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw2[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw2[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw2[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw2[i].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw2[target_idx].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
                        
            if ax7[i] == 1:  # 下
                target_idx = i - 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw2[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw2[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw2[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw2[i].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw2[target_idx].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 左
                target_idx = i - 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw2[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw2[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw2[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw2[i].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw2[target_idx].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 右
                target_idx = i + 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw2[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw2[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw2[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw2[i].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw2[target_idx].asd2.append({
                                    "b": "qw2",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
    # 预加载qw3
    for i, _ in ax10:
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
                if 0 <= nx < 32 and 0 <= ny < 3:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw3[ax15], Point):
                        if ax16 > qw3[ax15].brightness:
                            qw3[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw3[ax15]:
                            qw3[ax15] = min(ax16, 9)
    # -----------
    # qw3
    for i, ax14 in ax10:  # 直接使用保存的原始亮度
        cx = i % 32
        cy = i // 32
        block_modified = False  # 每个区块开头重新初始化，绝对独立
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 > ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = -(ax14 - ax13)
                    changed = False
                    if isinstance(qw3[ax15], Point):
                        # 修改3：把 < 改成 <=，彻底清除残留的1
                        if ax16 <= qw3[ax15].brightness:
                            qw3[ax15].brightness = max(ax16, 0)
                            changed = True
                    else:
                        # 同样改成 <=
                        if ax16 <= qw3[ax15]:
                            qw3[ax15] = max(ax16, 0)
                            changed = True
                    if changed:
                        block_modified = True
        if block_modified:  # ax8 ax18 ax7
            # 上下左右
            # 1 2 3 4
            if ax7[i] == 1:  # 上
                target_idx = i + 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw3[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw3[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw3[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw3[i].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw3[target_idx].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
                        
            if ax7[i] == 1:  # 下
                target_idx = i - 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw3[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw3[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw3[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw3[i].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw3[target_idx].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 左
                target_idx = i - 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw3[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw3[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw3[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw3[i].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw3[target_idx].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 右
                target_idx = i + 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw3[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw3[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw3[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw3[i].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw3[target_idx].asd2.append({
                                    "b": "qw3",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
    # 预加载qw4
    for i, _ in ax11:
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
                if 0 <= nx < 32 and 0 <= ny < 3:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw4[ax15], Point):
                        if ax16 > qw4[ax15].brightness:
                            qw4[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw4[ax15]:
                            qw4[ax15] = min(ax16, 9)
    # -----------
    # qw4
    for i, ax14 in ax11:  # 直接使用保存的原始亮度
        cx = i % 32
        cy = i // 32
        block_modified = False  # 每个区块开头重新初始化，绝对独立
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 > ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = -(ax14 - ax13)
                    changed = False
                    if isinstance(qw4[ax15], Point):
                        # 修改3：把 < 改成 <=，彻底清除残留的1
                        if ax16 <= qw4[ax15].brightness:
                            qw4[ax15].brightness = max(ax16, 0)
                            changed = True
                    else:
                        # 同样改成 <=
                        if ax16 <= qw4[ax15]:
                            qw4[ax15] = max(ax16, 0)
                            changed = True
                    if changed:
                        block_modified = True
        if block_modified:  # ax8 ax18 ax7
            # 上下左右
            # 1 2 3 4
            if ax7[i] == 1:  # 上
                target_idx = i + 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw4[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw4[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw4[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw4[i].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw4[target_idx].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
                        
            if ax7[i] == 1:  # 下
                target_idx = i - 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw4[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw4[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw4[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw4[i].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw4[target_idx].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 左
                target_idx = i - 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw4[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw4[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw4[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw4[i].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw4[target_idx].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 右
                target_idx = i + 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw4[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw4[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw4[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw4[i].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw4[target_idx].asd2.append({
                                    "b": "qw4",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
    # 预加载qw5
    for i, _ in ax12:
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
                if 0 <= nx < 32 and 0 <= ny < 3:
                    ax15 = ny * 32 + nx
                    ax16 = ax14 - ax13
                    if isinstance(qw5[ax15], Point):
                        if ax16 > qw5[ax15].brightness:
                            qw5[ax15].brightness = min(ax16, 9)
                    else:
                        if ax16 > qw5[ax15]:
                            qw5[ax15] = min(ax16, 9)
    # -----------
    # qw5
    for i, ax14 in ax12:  # 直接使用保存的原始亮度
        cx = i % 32
        cy = i // 32
        block_modified = False  # 每个区块开头重新初始化，绝对独立
        for dy in range(-ax14, ax14 + 1):
            for dx in range(-ax14, ax14 + 1):
                ax13 = abs(dx) + abs(dy)
                if ax13 > ax14:
                    continue
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < 32 and 0 <= ny < 32:
                    ax15 = ny * 32 + nx
                    ax16 = -(ax14 - ax13)
                    changed = False
                    if isinstance(qw5[ax15], Point):
                        # 修改3：把 < 改成 <=，彻底清除残留的1
                        if ax16 <= qw5[ax15].brightness:
                            qw5[ax15].brightness = max(ax16, 0)
                            changed = True
                    else:
                        # 同样改成 <=
                        if ax16 <= qw5[ax15]:
                            qw5[ax15] = max(ax16, 0)
                            changed = True
                    if changed:
                        block_modified = True
        if block_modified:  # ax8 ax18 ax7
            # 上下左右
            # 1 2 3 4
            if ax7[i] == 1:  # 上
                target_idx = i + 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw5[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw5[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw5[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw5[i].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw5[target_idx].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
                        
            if ax7[i] == 1:  # 下
                target_idx = i - 32
                if 0 <= target_idx < 1024:
                    if isinstance(qw5[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw5[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw5[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw5[i].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw5[target_idx].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 左
                target_idx = i - 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw5[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw5[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw5[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw5[i].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw5[target_idx].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
            if ax7[i] == 1:  # 右
                target_idx = i + 1
                if 0 <= target_idx < 1024:
                    if isinstance(qw5[target_idx], Point):  # 连接逻辑看是否适合连接
                        if qw5[target_idx].brightness < 9:  # 检查他是否为一个类
                            ax20 = 0  # 控制 输入 输出
                            if len(qw5[target_idx].asd) < 9:
                                pass  #  1   2    3 类型对方的也要记录时前面加上个a1
                            else:  # 因为是向上，所以应该是输入        
                                ax21 = 0                   
                                for a in range(3):
                                    if ax7[i + a] < 4:
                                        ax21 += 1
                                    elif a == 3:
                                        break
                                    if ax21 == 1:
                                        ax21 = "a1"
                                    elif ax21 == 2:
                                        ax21 = "a2"
                                    elif ax21 == 3:
                                        ax21 = "a3"
                                qw5[i].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": i,
                                    "a3": target_idx,
                                    "signal": 0
                                })
                                qw5[target_idx].asd2.append({
                                    "b": "qw5",
                                    "i": ax21,
                                    "a1": target_idx,
                                    "a3": i,
                                    "signal": 0
                                })
    # -----------
 
    # ----------------打印显示逻辑------------
    print("======区块一==========")
    for i in range(0, 32*32, 32):
            row = []
            for j in range(i, i+32):
                if isinstance(qw1[j], Point):
                    row.append(str(qw1[j].brightness))
                else:
                    row.append(str(qw1[j]))
            print(' '.join(row))
    print("\n==========区块2==========")
    for i in range(0, 32*32, 32):
            row = []
            for j in range(i, i+32):
                if isinstance(qw2[j], Point):
                    row.append(str(qw2[j].brightness))
                else:
                    row.append(str(qw2[j]))
            print(' '.join(row))
    print("\n==========区块3==========")
    for i in range(0, 32*32, 32):
            row = []
            for j in range(i, i+32):
                if isinstance(qw3[j], Point):
                    row.append(str(qw3[j].brightness))
                else:
                    row.append(str(qw3[j]))
            print(' '.join(row))
    print("\n========== 区块4 ==========")
    for i in range(0, 32*32, 32):
                row = []
                for j in range(i, i+32):
                    if isinstance(qw4[j], Point):
                        row.append(str(qw4[j].brightness))
                    else:
                        row.append(str(qw4[j]))
                print(' '.join(row))
    print("\n========== 区块5 ==========")
    for i in range(0, 32*32, 32):
                row = []
                for j in range(i, i+32):
                    if isinstance(qw5[j], Point):
                        row.append(str(qw5[j].brightness))
                    else:
                        row.append(str(qw5[j]))
                print(' '.join(row))