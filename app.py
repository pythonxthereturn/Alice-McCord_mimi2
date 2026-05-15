# -*- coding: utf-8 -*-
#!C:/Users/Administrator/Desktop/Alice McCord/app.py python3
import inspect


class Point:
    def __init__(self, center_index, brightness, control_ports=None, input_ports=None, output_ports=None):
        self.center_index = center_index
        self.brightness = brightness
        self.control_ports = [] if control_ports is None else control_ports
        self.input_ports = [] if input_ports is None else input_ports
        self.output_ports = [] if output_ports is None else output_ports


grid_1 = [0] * 1024
grid_2 = [0] * 1024
grid_3 = [0] * 1024
grid_4 = [0] * 1024
grid_5 = [0] * 1024
user_input_raw = 0
input_character_list = 0
unicode_encoded_bytes = 0
binary_string = 0
padded_binary_string = 0
binary_string_list = []
random_pool = []
active_points_grid_1 = []
active_points_grid_2 = []
active_points_grid_3 = []
active_points_grid_4 = []
active_points_grid_5 = []
manhattan_distance = 0
source_brightness = 0
target_flat_index = 0
computed_brightness = 0
block_modified_flag = False
current_binary_string = []
grid_1[400] = Point(center_index=400, brightness=9)
grid_1[399] = Point(center_index=390, brightness=9)

while True:
    active_points_grid_1.clear()
    active_points_grid_2.clear()
    active_points_grid_3.clear()
    active_points_grid_4.clear()
    active_points_grid_5.clear()
    binary_string_list.clear()
    random_pool.clear()

    user_input_raw = input("input:")
    input_character_list = list(user_input_raw)
    binary_string_list = []
    random_pool = []

    for i in input_character_list:
        unicode_encoded_bytes = i.encode("utf-8")
        binary_string = ''.join(f'{byte:08b}' for byte in unicode_encoded_bytes)
        padded_binary_string = binary_string.ljust(32, '0')[:32]
        print(f"'{i}' -> {padded_binary_string}")
        binary_string_list.append(padded_binary_string)

    # Random pool
    for i in range(len(binary_string_list)):
        current_binary_string = binary_string_list[i]
        random_pool.append(int(current_binary_string[int(0)]) + int(current_binary_string[1]) + int(current_binary_string[2]) + int(current_binary_string[3]))
        random_pool.append(int(current_binary_string[4]) + int(current_binary_string[5]) + int(current_binary_string[6]) + int(current_binary_string[7]))
        random_pool.append(int(current_binary_string[8]) + int(current_binary_string[9]) + int(current_binary_string[10]) + int(current_binary_string[11]))
        random_pool.append(int(current_binary_string[12]) + int(current_binary_string[13]) + int(current_binary_string[14]) + int(current_binary_string[15]))
        random_pool.append(int(current_binary_string[16]) + int(current_binary_string[17]) + int(current_binary_string[18]) + int(current_binary_string[19]))
        random_pool.append(int(current_binary_string[20]) + int(current_binary_string[21]) + int(current_binary_string[22]) + int(current_binary_string[23]))

    print("随机池：", random_pool)

    for i in range(len(grid_1)):
        if isinstance(grid_1[i], Point):
            if grid_1[i].brightness == 9:
                active_points_grid_1.append((i, grid_1[i].brightness))

    for i in range(len(grid_2)):
        if isinstance(grid_2[i], Point):
            if grid_2[i].brightness == 9:
                active_points_grid_2.append((i, grid_2[i].brightness))

    for i in range(len(grid_3)):
        if isinstance(grid_3[i], Point):
            if grid_3[i].brightness == 9:
                active_points_grid_3.append((i, grid_3[i].brightness))

    for i in range(len(grid_4)):
        if isinstance(grid_4[i], Point):
            if grid_4[i].brightness == 9:
                active_points_grid_4.append((i, grid_4[i].brightness))

    for i in range(len(grid_5)):
        if isinstance(grid_5[i], Point):
            if grid_5[i].brightness == 9:
                active_points_grid_5.append((i, grid_5[i].brightness))

    # Rendering phase
    # Grid 1
    for point_index, _ in active_points_grid_1:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_1[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_1[target_flat_index], Point):
                        if computed_brightness > grid_1[target_flat_index].brightness:
                            grid_1[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_1[target_flat_index]:
                            grid_1[target_flat_index] = min(computed_brightness, 9)

    # Grid 2
    for point_index, _ in active_points_grid_2:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_2[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_2[target_flat_index], Point):
                        if computed_brightness > grid_2[target_flat_index].brightness:
                            grid_2[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_2[target_flat_index]:
                            grid_2[target_flat_index] = min(computed_brightness, 9)

    # Grid 3
    for point_index, _ in active_points_grid_3:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_3[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_3[target_flat_index], Point):
                        if computed_brightness > grid_3[target_flat_index].brightness:
                            grid_3[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_3[target_flat_index]:
                            grid_3[target_flat_index] = min(computed_brightness, 9)

    # Grid 4
    for point_index, _ in active_points_grid_4:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_4[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_4[target_flat_index], Point):
                        if computed_brightness > grid_4[target_flat_index].brightness:
                            grid_4[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_4[target_flat_index]:
                            grid_4[target_flat_index] = min(computed_brightness, 9)

    # Grid 5
    for point_index, _ in active_points_grid_5:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_5[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_5[target_flat_index], Point):
                        if computed_brightness > grid_5[target_flat_index].brightness:
                            grid_5[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_5[target_flat_index]:
                            grid_5[target_flat_index] = min(computed_brightness, 9)

    # Annealing and binding phase
    for point_index, source_brightness in active_points_grid_1:
        column_x = point_index % 32
        row_y = point_index // 32
        block_modified_flag = False
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = -(source_brightness - manhattan_distance)
                    changed = False
                    if isinstance(grid_1[target_flat_index], Point):
                        if computed_brightness <= grid_1[target_flat_index].brightness:
                            grid_1[target_flat_index].brightness = max(computed_brightness, 0)
                            changed = True
                    else:
                        if computed_brightness <= grid_1[target_flat_index]:
                            grid_1[target_flat_index] = max(computed_brightness, 0)
                            changed = True
                    if changed:
                        block_modified_flag = True
        if block_modified_flag:
            if point_index < len(random_pool) and random_pool[int(point_index)] == 1:
                target_idx = point_index + 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_1[target_idx], Point):
                        if grid_1[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_1[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_1[point_index].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_1[target_idx].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_1[target_idx], Point):
                        if grid_1[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_1[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_1[point_index].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_1[target_idx].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_1[target_idx], Point):
                        if grid_1[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_1[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_1[point_index].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_1[target_idx].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_1[target_idx], Point):
                        if grid_1[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_1[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_1[point_index].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_1[target_idx].output_ports.append({
                                    "block_name": "grid_1",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

    # Preload grid_2 diamond spread into top 3 rows
    for point_index, _ in active_points_grid_2:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_2[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 3:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_2[target_flat_index], Point):
                        if computed_brightness > grid_2[target_flat_index].brightness:
                            grid_2[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_2[target_flat_index]:
                            grid_2[target_flat_index] = min(computed_brightness, 9)

    for point_index, source_brightness in active_points_grid_2:
        column_x = point_index % 32
        row_y = point_index // 32
        block_modified_flag = False
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = -(source_brightness - manhattan_distance)
                    changed = False
                    if isinstance(grid_2[target_flat_index], Point):
                        if computed_brightness <= grid_2[target_flat_index].brightness:
                            grid_2[target_flat_index].brightness = max(computed_brightness, 0)
                            changed = True
                    else:
                        if computed_brightness <= grid_2[target_flat_index]:
                            grid_2[target_flat_index] = max(computed_brightness, 0)
                            changed = True
                    if changed:
                        block_modified_flag = True
        if block_modified_flag:
            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_2[target_idx], Point):
                        if grid_2[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_2[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_2[point_index].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_2[target_idx].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_2[target_idx], Point):
                        if grid_2[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_2[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_2[point_index].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_2[target_idx].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_2[target_idx], Point):
                        if grid_2[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_2[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_2[point_index].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_2[target_idx].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_2[target_idx], Point):
                        if grid_2[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_2[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_2[point_index].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_2[target_idx].output_ports.append({
                                    "block_name": "grid_2",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

    # Preload grid_3 diamond spread into top 3 rows
    for point_index, _ in active_points_grid_3:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_3[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 3:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_3[target_flat_index], Point):
                        if computed_brightness > grid_3[target_flat_index].brightness:
                            grid_3[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_3[target_flat_index]:
                            grid_3[target_flat_index] = min(computed_brightness, 9)

    for point_index, source_brightness in active_points_grid_3:
        column_x = point_index % 32
        row_y = point_index // 32
        block_modified_flag = False
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = -(source_brightness - manhattan_distance)
                    changed = False
                    if isinstance(grid_3[target_flat_index], Point):
                        if computed_brightness <= grid_3[target_flat_index].brightness:
                            grid_3[target_flat_index].brightness = max(computed_brightness, 0)
                            changed = True
                    else:
                        if computed_brightness <= grid_3[target_flat_index]:
                            grid_3[target_flat_index] = max(computed_brightness, 0)
                            changed = True
                    if changed:
                        block_modified_flag = True
        if block_modified_flag:
            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_3[target_idx], Point):
                        if grid_3[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_3[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_3[point_index].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_3[target_idx].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_3[target_idx], Point):
                        if grid_3[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_3[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_3[point_index].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_3[target_idx].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_3[target_idx], Point):
                        if grid_3[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_3[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_3[point_index].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_3[target_idx].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_3[target_idx], Point):
                        if grid_3[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_3[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_3[point_index].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_3[target_idx].output_ports.append({
                                    "block_name": "grid_3",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

    # Preload grid_4 diamond spread into top 3 rows
    for point_index, _ in active_points_grid_4:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_4[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 3:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_4[target_flat_index], Point):
                        if computed_brightness > grid_4[target_flat_index].brightness:
                            grid_4[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_4[target_flat_index]:
                            grid_4[target_flat_index] = min(computed_brightness, 9)

    for point_index, source_brightness in active_points_grid_4:
        column_x = point_index % 32
        row_y = point_index // 32
        block_modified_flag = False
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = -(source_brightness - manhattan_distance)
                    changed = False
                    if isinstance(grid_4[target_flat_index], Point):
                        if computed_brightness <= grid_4[target_flat_index].brightness:
                            grid_4[target_flat_index].brightness = max(computed_brightness, 0)
                            changed = True
                    else:
                        if computed_brightness <= grid_4[target_flat_index]:
                            grid_4[target_flat_index] = max(computed_brightness, 0)
                            changed = True
                    if changed:
                        block_modified_flag = True
        if block_modified_flag:
            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_4[target_idx], Point):
                        if grid_4[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_4[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_4[point_index].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_4[target_idx].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_4[target_idx], Point):
                        if grid_4[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_4[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_4[point_index].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_4[target_idx].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_4[target_idx], Point):
                        if grid_4[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_4[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_4[point_index].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_4[target_idx].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_4[target_idx], Point):
                        if grid_4[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_4[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_4[point_index].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_4[target_idx].output_ports.append({
                                    "block_name": "grid_4",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

    # Preload grid_5 diamond spread into top 3 rows
    for point_index, _ in active_points_grid_5:
        column_x = point_index % 32
        row_y = point_index // 32
        source_brightness = grid_5[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 3:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid_5[target_flat_index], Point):
                        if computed_brightness > grid_5[target_flat_index].brightness:
                            grid_5[target_flat_index].brightness = min(computed_brightness, 9)
                    else:
                        if computed_brightness > grid_5[target_flat_index]:
                            grid_5[target_flat_index] = min(computed_brightness, 9)

    for point_index, source_brightness in active_points_grid_5:
        column_x = point_index % 32
        row_y = point_index // 32
        block_modified_flag = False
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < 32 and 0 <= neighbor_y < 32:
                    target_flat_index = neighbor_y * 32 + neighbor_x
                    computed_brightness = -(source_brightness - manhattan_distance)
                    changed = False
                    if isinstance(grid_5[target_flat_index], Point):
                        if computed_brightness <= grid_5[target_flat_index].brightness:
                            grid_5[target_flat_index].brightness = max(computed_brightness, 0)
                            changed = True
                    else:
                        if computed_brightness <= grid_5[target_flat_index]:
                            grid_5[target_flat_index] = max(computed_brightness, 0)
                            changed = True
                    if changed:
                        block_modified_flag = True
        if block_modified_flag:
            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_5[target_idx], Point):
                        if grid_5[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_5[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_5[point_index].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_5[target_idx].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 32
                if 0 <= target_idx < 1024:
                    if isinstance(grid_5[target_idx], Point):
                        if grid_5[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_5[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_5[point_index].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_5[target_idx].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index - 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_5[target_idx], Point):
                        if grid_5[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_5[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_5[point_index].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_5[target_idx].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

            if point_index < len(random_pool) and random_pool[point_index] == 1:
                target_idx = point_index + 1
                if 0 <= target_idx < 1024:
                    if isinstance(grid_5[target_idx], Point):
                        if grid_5[target_idx].brightness < 9:
                            port_type = 0
                            if len(grid_5[target_idx].control_ports) < 9:
                                pass
                            else:
                                port_label = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_label += 1
                                    elif offset_counter == 3:
                                        break
                                    if port_label == 1:
                                        port_label = "control"
                                    elif port_label == 2:
                                        port_label = "input"
                                    elif port_label == 3:
                                        port_label = "output"
                                grid_5[point_index].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": point_index,
                                    "target_point_index": target_idx,
                                    "signal": 0
                                })
                                grid_5[target_idx].output_ports.append({
                                    "block_name": "grid_5",
                                    "port_identifier": port_label,
                                    "source_point_index": target_idx,
                                    "target_point_index": point_index,
                                    "signal": 0
                                })

    # Display output
    print("====== Grid 1 ======")
    for i in range(0, 32*32, 32):
        row = []
        for j in range(i, i+32):
            if isinstance(grid_1[j], Point):
                row.append(str(grid_1[j].brightness))
            else:
                row.append(str(grid_1[j]))
        print(' '.join(row))

    print("\n====== Grid 2 ======")
    for i in range(0, 32*32, 32):
        row = []
        for j in range(i, i+32):
            if isinstance(grid_2[j], Point):
                row.append(str(grid_2[j].brightness))
            else:
                row.append(str(grid_2[j]))
        print(' '.join(row))

    print("\n====== Grid 3 ======")
    for i in range(0, 32*32, 32):
        row = []
        for j in range(i, i+32):
            if isinstance(grid_3[j], Point):
                row.append(str(grid_3[j].brightness))
            else:
                row.append(str(grid_3[j]))
        print(' '.join(row))

    print("\n====== Grid 4 ======")
    for i in range(0, 32*32, 32):
        row = []
        for j in range(i, i+32):
            if isinstance(grid_4[j], Point):
                row.append(str(grid_4[j].brightness))
            else:
                row.append(str(grid_4[j]))
        print(' '.join(row))

    print("\n====== Grid 5 ======")
    for i in range(0, 32*32, 32):
        row = []
        for j in range(i, i+32):
            if isinstance(grid_5[j], Point):
                row.append(str(grid_5[j].brightness))
            else:
                row.append(str(grid_5[j]))
        print(' '.join(row))