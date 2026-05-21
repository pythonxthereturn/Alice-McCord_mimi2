# -*- coding: utf-8 -*-
#!C:/Users/Administrator/Desktop/Alice McCord/app.py python3

# ===========================================================================
# Global Constants
# ===========================================================================
GRID_SIDE_LENGTH = 32
TOTAL_CELLS = 1024
MAX_BRIGHTNESS = 9
ACTIVE_BRIGHTNESS = 9
SEED_BRIGHTNESS = 4
MAX_PORTS_PER_TYPE = 9
API_PORT_COUNT = 32
CONTROL_SIGNAL_THRESHOLD = 1
BINARY_GROUP_BITS = 4
RANDOM_POOL_GROUPS = 7


# ===========================================================================
# Point Class
# ===========================================================================
class Point:
    """32x32 grid node class.

    Attributes:
        center_index: flat index within grid (0 ~ TOTAL_CELLS-1)
        brightness: current brightness value (0 ~ MAX_BRIGHTNESS)
        control_ports: list of connection dictionaries
        input_ports: list of connection dictionaries
        output_ports: list of connection dictionaries
    """

    def __init__(self, center_index: int, brightness: int,
                 control_ports: list | None = None,
                 input_ports: list | None = None,
                 output_ports: list | None = None):
        self.center_index = center_index
        self.brightness = brightness
        self.control_ports = [] if control_ports is None else control_ports
        self.input_ports = [] if input_ports is None else input_ports
        self.output_ports = [] if output_ports is None else output_ports


# ===========================================================================
# Utility Functions
# ===========================================================================
def build_random_pool(binary_string_list: list) -> list:
    """Build a random pool from a list of 32-bit binary strings.

    Takes the first RANDOM_POOL_GROUPS * BINARY_GROUP_BITS = 28 bits
    from each binary string, splits into groups of BINARY_GROUP_BITS bits,
    and sums each group to produce an integer in 0~4.

    Args:
        binary_string_list: list of binary strings, each of length
                            GRID_SIDE_LENGTH (32)

    Returns:
        list: random pool containing integers in range 0~4
    """
    random_pool = []
    for i in range(len(binary_string_list)):
        current_binary_string = binary_string_list[i]
        random_pool.append(int(current_binary_string[0]) + int(current_binary_string[1]) + int(current_binary_string[2]) + int(current_binary_string[3]))
        random_pool.append(int(current_binary_string[4]) + int(current_binary_string[5]) + int(current_binary_string[6]) + int(current_binary_string[7]))
        random_pool.append(int(current_binary_string[8]) + int(current_binary_string[9]) + int(current_binary_string[10]) + int(current_binary_string[11]))
        random_pool.append(int(current_binary_string[12]) + int(current_binary_string[13]) + int(current_binary_string[14]) + int(current_binary_string[15]))
        random_pool.append(int(current_binary_string[16]) + int(current_binary_string[17]) + int(current_binary_string[18]) + int(current_binary_string[19]))
        random_pool.append(int(current_binary_string[20]) + int(current_binary_string[21]) + int(current_binary_string[22]) + int(current_binary_string[23]))
        random_pool.append(int(current_binary_string[24]) + int(current_binary_string[25]) + int(current_binary_string[26]) + int(current_binary_string[27]))
    return random_pool


def detect_active_points(grid: list) -> list:
    """Detect all active Points with brightness equal to ACTIVE_BRIGHTNESS.

    Args:
        grid: list of length TOTAL_CELLS

    Returns:
        list: [(point_index, brightness), ...] for Points where
              brightness == ACTIVE_BRIGHTNESS
    """
    active_points = []
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            if grid[i].brightness == ACTIVE_BRIGHTNESS:
                active_points.append((i, grid[i].brightness))
    return active_points


def detect_all_points(grid: list) -> list:
    """Detect all Point objects in the grid regardless of brightness.

    Args:
        grid: list of length TOTAL_CELLS

    Returns:
        list: [(point_index, brightness), ...] for every Point in the grid
    """
    all_points = []
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            all_points.append((i, grid[i].brightness))
    return all_points


def update_connections_after_move(grid: list, grid_name: str,
                                   old_index: int, new_index: int) -> None:
    """Update all port connection references after a Point moves.

    Traverses every Point in the grid and updates any connection entry
    whose source_point_index or target_point_index references the old
    index to point to the new index.

    Args:
        grid: list of length TOTAL_CELLS
        grid_name: name string of the grid layer, e.g. "grid_layer_1"
        old_index: the index the Point moved from
        new_index: the index the Point moved to
    """
    for i in range(len(grid)):
        if isinstance(grid[i], Point):
            point = grid[i]
            for port_list in [point.control_ports, point.input_ports, point.output_ports]:
                for connection in port_list:
                    if connection.get("source_point_index") == old_index:
                        connection["source_point_index"] = new_index
                    if connection.get("target_point_index") == old_index:
                        connection["target_point_index"] = new_index


def determine_movement_direction(grid: list, point_index: int) -> int:
    """Determine the movement direction for a Point based on neighbor signals.

    Compares the Point's own brightness against the signal strength
    of its four orthogonal neighbors. A neighbor's signal is the
    numeric value stored at that cell (only empty cells are considered
    since occupied cells cannot be moved into).
    The direction with the highest neighbor signal is chosen.
    Movement occurs only if the highest neighbor signal exceeds the
    Point's own brightness.

    Priority for equal signals: down > right > up > left.

    Args:
        grid: list of length TOTAL_CELLS
        point_index: flat index of the Point to evaluate

    Returns:
        int: target index to move to, or -1 if no move should occur
    """
    self_brightness = grid[point_index].brightness
    direction_offsets = [
        ("down", 32),
        ("right", 1),
        ("up", -32),
        ("left", -1),
    ]
    candidates = []
    for direction_name, offset in direction_offsets:
        target_index = point_index + offset
        if target_index < 0 or target_index >= TOTAL_CELLS:
            continue
        if direction_name == "left" and point_index % GRID_SIDE_LENGTH == 0:
            continue
        if direction_name == "right" and point_index % GRID_SIDE_LENGTH == GRID_SIDE_LENGTH - 1:
            continue
        if isinstance(grid[target_index], Point):
            continue
        neighbor_signal = grid[target_index]
        candidates.append((neighbor_signal, direction_name, target_index))
    if not candidates:
        return -1
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_signal = candidates[0][0]
    if best_signal > self_brightness:
        return candidates[0][2]
    return -1


def clear_non_point_brightness(grid: list) -> list:
    """Reset all non-Point cells in the grid to zero.

    Args:
        grid: list of length TOTAL_CELLS

    Returns:
        list: the modified grid
    """
    for i in range(len(grid)):
        if not isinstance(grid[i], Point):
            grid[i] = 0
    return grid


def diamond_render_single_point(grid: list, point_index: int,
                                 source_brightness: int) -> list:
    """Perform a single diamond brightness diffusion (additive) from one Point.

    Diffuses brightness outward within Manhattan distance < source_brightness.
    Brightness = source_brightness - Manhattan distance.
    For Point objects only modifies the brightness attribute, never overwrites
    the Point object itself. Uses max() for accumulation, capped at
    MAX_BRIGHTNESS.

    Args:
        grid: list of length TOTAL_CELLS
        point_index: flat index of the source Point
        source_brightness: brightness value of the source Point

    Returns:
        list: the modified grid
    """
    column_x = point_index % GRID_SIDE_LENGTH
    row_y = point_index // GRID_SIDE_LENGTH
    for delta_y in range(-source_brightness, source_brightness + 1):
        for delta_x in range(-source_brightness, source_brightness + 1):
            manhattan_distance = abs(delta_x) + abs(delta_y)
            if manhattan_distance >= source_brightness:
                continue
            neighbor_x = column_x + delta_x
            neighbor_y = row_y + delta_y
            if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < GRID_SIDE_LENGTH:
                target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                computed_brightness = source_brightness - manhattan_distance
                if isinstance(grid[target_flat_index], Point):
                    if computed_brightness > grid[target_flat_index].brightness:
                        grid[target_flat_index].brightness = min(computed_brightness, MAX_BRIGHTNESS)
                else:
                    if computed_brightness > grid[target_flat_index]:
                        grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return grid


# ===========================================================================
# Render Function
# ===========================================================================
def render_grid(grid: list, active_points: list) -> list:
    """Perform diamond brightness diffusion for all active Points.

    Iterates over all active Points and calls diamond_render_single_point
    for each one. The render is additive: new brightness = max(old, computed),
    capped at MAX_BRIGHTNESS.

    Args:
        grid: list of length TOTAL_CELLS
        active_points: list of (point_index, brightness) tuples

    Returns:
        list: the modified grid
    """
    for point_index, _ in active_points:
        source_brightness = grid[point_index].brightness
        column_x = point_index % GRID_SIDE_LENGTH
        row_y = point_index // GRID_SIDE_LENGTH
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < GRID_SIDE_LENGTH:
                    target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(grid[target_flat_index], Point):
                        if computed_brightness > grid[target_flat_index].brightness:
                            grid[target_flat_index].brightness = min(computed_brightness, MAX_BRIGHTNESS)
                    else:
                        if computed_brightness > grid[target_flat_index]:
                            grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return grid


# ===========================================================================
# Annealing and Connection Functions
# ===========================================================================
def anneal_and_connect(grid: list, active_points: list,
                        random_pool: list, grid_name: str) -> list:
    """Perform annealing (subtractive) and establish port connections.

    Annealing is the inverse of rendering: using subtraction.
    Range: manhattan_distance <= source_brightness (one more ring than render).

    Connection logic:
    - Only executed if annealing modified any cell (block_modified_flag).
    - For each of four directions, if random_pool condition is met,
      the connection type is determined by summing 3 consecutive
      random_pool values that are < 4:
        * count == 1 -> signal connection: output <-> input (bidirectional)
        * count == 2 -> control connection: output <-> control (bidirectional)
        * otherwise  -> default to control connection
    - Both sides must have < MAX_PORTS_PER_TYPE ports for the target type.
    - After connection, if all three port types reach MAX_PORTS_PER_TYPE,
      set brightness to ACTIVE_BRIGHTNESS.
    - After connection, re-render the active Point if brightness > 0.

    Args:
        grid: list of length TOTAL_CELLS
        active_points: list of (point_index, brightness) tuples
        random_pool: list of random integers used for connection decisions
        grid_name: name string of the grid layer

    Returns:
        list: the modified grid
    """
    for point_index, source_brightness in active_points:
        column_x = point_index % GRID_SIDE_LENGTH
        row_y = point_index // GRID_SIDE_LENGTH
        block_modified_flag = False

        print(f"[Anneal] grid={grid_name}, index={point_index}, brightness={source_brightness}")

        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance > source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < GRID_SIDE_LENGTH:
                    target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                    computed_change = -(source_brightness - manhattan_distance)
                    changed = False
                    if isinstance(grid[target_flat_index], Point):
                        new_brightness = grid[target_flat_index].brightness + computed_change
                        if new_brightness < 0:
                            new_brightness = 0
                        if new_brightness != grid[target_flat_index].brightness:
                            grid[target_flat_index].brightness = new_brightness
                            changed = True
                    else:
                        new_brightness = grid[target_flat_index] + computed_change
                        if new_brightness < 0:
                            new_brightness = 0
                        if new_brightness != grid[target_flat_index]:
                            grid[target_flat_index] = new_brightness
                            changed = True
                    if changed:
                        block_modified_flag = True

        if block_modified_flag:
            for direction_offset in [32, -32, -1, 1]:
                if point_index < len(random_pool) and random_pool[point_index] == 1:
                    target_index = point_index + direction_offset
                    if 0 <= target_index < TOTAL_CELLS:
                        if isinstance(grid[target_index], Point):
                            if grid[target_index].brightness < MAX_BRIGHTNESS:
                                port_type_accumulator = 0
                                for offset_counter in range(3):
                                    if point_index + offset_counter < len(random_pool) and random_pool[point_index + offset_counter] < 4:
                                        port_type_accumulator += 1

                                connection_established = False

                                if port_type_accumulator == 1:
                                    if len(grid[target_index].input_ports) < MAX_PORTS_PER_TYPE and len(grid[point_index].output_ports) < MAX_PORTS_PER_TYPE:
                                        source_connection = {
                                            "source_point_index": point_index,
                                            "target_point_index": target_index,
                                            "signal": 0,
                                            "port_type": "output"
                                        }
                                        target_connection = {
                                            "source_point_index": target_index,
                                            "target_point_index": point_index,
                                            "signal": 0,
                                            "port_type": "input"
                                        }
                                        grid[point_index].output_ports.append(source_connection)
                                        grid[target_index].input_ports.append(target_connection)
                                        connection_established = True
                                        print(f"[Connect] grid={grid_name}, type=signal(output->input), source={point_index}, target={target_index}")

                                elif port_type_accumulator == 2:
                                    if len(grid[target_index].control_ports) < MAX_PORTS_PER_TYPE and len(grid[point_index].output_ports) < MAX_PORTS_PER_TYPE:
                                        source_connection = {
                                            "source_point_index": point_index,
                                            "target_point_index": target_index,
                                            "signal": 0,
                                            "port_type": "output"
                                        }
                                        target_connection = {
                                            "source_point_index": target_index,
                                            "target_point_index": point_index,
                                            "signal": 0,
                                            "port_type": "control"
                                        }
                                        grid[point_index].output_ports.append(source_connection)
                                        grid[target_index].control_ports.append(target_connection)
                                        connection_established = True
                                        print(f"[Connect] grid={grid_name}, type=control(output->control), source={point_index}, target={target_index}")

                                else:
                                    if len(grid[target_index].control_ports) < MAX_PORTS_PER_TYPE and len(grid[point_index].output_ports) < MAX_PORTS_PER_TYPE:
                                        source_connection = {
                                            "source_point_index": point_index,
                                            "target_point_index": target_index,
                                            "signal": 0,
                                            "port_type": "output"
                                        }
                                        target_connection = {
                                            "source_point_index": target_index,
                                            "target_point_index": point_index,
                                            "signal": 0,
                                            "port_type": "control"
                                        }
                                        grid[point_index].output_ports.append(source_connection)
                                        grid[target_index].control_ports.append(target_connection)
                                        connection_established = True
                                        print(f"[Connect] grid={grid_name}, type=control(default), source={point_index}, target={target_index}")

                                if connection_established:
                                    if (len(grid[point_index].control_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[point_index].input_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[point_index].output_ports) == MAX_PORTS_PER_TYPE):
                                        grid[point_index].brightness = ACTIVE_BRIGHTNESS
                                    if (len(grid[target_index].control_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[target_index].input_ports) == MAX_PORTS_PER_TYPE and
                                        len(grid[target_index].output_ports) == MAX_PORTS_PER_TYPE):
                                        grid[target_index].brightness = ACTIVE_BRIGHTNESS

                                    if grid[point_index].brightness > 0:
                                        grid = diamond_render_single_point(grid, point_index, grid[point_index].brightness)
                                        print(f"[Re-render] grid={grid_name}, index={point_index}")

    return grid


# ===========================================================================
# Preload Function
# ===========================================================================
def preload_next_grid(source_grid: list, target_grid: list,
                       active_points: list) -> list:
    """Preload diamond diffusion from source grid to the first 3 rows of target.

    Only applies diffusion to cells with row_y < 3 in the target grid.
    Logic is the same as rendering: additive, max accumulation, capped at
    MAX_BRIGHTNESS.

    Args:
        source_grid: list of length TOTAL_CELLS
        target_grid: list of length TOTAL_CELLS
        active_points: list of (point_index, brightness) from source grid

    Returns:
        list: the modified target grid
    """
    for point_index, _ in active_points:
        column_x = point_index % GRID_SIDE_LENGTH
        row_y = point_index // GRID_SIDE_LENGTH
        source_brightness = source_grid[point_index].brightness
        for delta_y in range(-source_brightness, source_brightness + 1):
            for delta_x in range(-source_brightness, source_brightness + 1):
                manhattan_distance = abs(delta_x) + abs(delta_y)
                if manhattan_distance >= source_brightness:
                    continue
                neighbor_x = column_x + delta_x
                neighbor_y = row_y + delta_y
                if 0 <= neighbor_x < GRID_SIDE_LENGTH and 0 <= neighbor_y < 3:
                    target_flat_index = neighbor_y * GRID_SIDE_LENGTH + neighbor_x
                    computed_brightness = source_brightness - manhattan_distance
                    if isinstance(target_grid[target_flat_index], Point):
                        if computed_brightness > target_grid[target_flat_index].brightness:
                            target_grid[target_flat_index].brightness = min(computed_brightness, MAX_BRIGHTNESS)
                    else:
                        if computed_brightness > target_grid[target_flat_index]:
                            target_grid[target_flat_index] = min(computed_brightness, MAX_BRIGHTNESS)
    return target_grid


# ===========================================================================
# Movement Phase Functions
# ===========================================================================
def execute_movement_phase(grid_layer_1: list, grid_layer_2: list,
                            grid_layer_3: list, grid_layer_4: list,
                            grid_layer_5: list) -> tuple:
    """Execute Point movement across all five grid layers.

    For each layer: detect all Points, evaluate movement direction
    for each, move the Point if applicable, and update all connection
    references. Uses a moved_to_indices set to prevent re-processing
    Points that have already been moved into new positions.

    Args:
        grid_layer_1 ~ grid_layer_5: five grid layers

    Returns:
        tuple: (grid_layer_1, ..., grid_layer_5) after movement
    """
    grids = [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]
    grid_names = ["grid_layer_1", "grid_layer_2", "grid_layer_3", "grid_layer_4", "grid_layer_5"]
    for grid_index in range(len(grids)):
        grid = grids[grid_index]
        grid_name = grid_names[grid_index]
        all_points = detect_all_points(grid)
        moved_to_indices = set()
        for original_index, _ in all_points:
            if original_index in moved_to_indices:
                continue
            if not isinstance(grid[original_index], Point):
                continue
            new_index = determine_movement_direction(grid, original_index)
            if new_index == -1:
                continue
            grid[new_index] = grid[original_index]
            grid[new_index].center_index = new_index
            grid[original_index] = 0
            update_connections_after_move(grid, grid_name, original_index, new_index)
            moved_to_indices.add(new_index)
            print(f"[Move] grid={grid_name}, old_index={original_index} -> new_index={new_index}")
    return grids[0], grids[1], grids[2], grids[3], grids[4]


# ===========================================================================
# Signal Propagation Function
# ===========================================================================
def transistor_style_signal_propagation(grid_layer_1: list,
                                         grid_layer_2: list,
                                         grid_layer_3: list,
                                         grid_layer_4: list,
                                         grid_layer_5: list) -> tuple:
    """Propagate signals through all five layers in transistor style.

    Strict processing order: grid_layer_1 -> grid_layer_2 -> ... ->
    grid_layer_5. Within each layer, top-to-bottom, left-to-right
    (index 0 -> TOTAL_CELLS-1). Only Point objects are processed.

    For each Point:
    1. Collect input_ports signals > 0.
    2. If any control_ports has signal > CONTROL_SIGNAL_THRESHOLD,
       clear control signals, clear input signals, skip to next node.
    3. Take max input signal as output_signal. Traverse output_ports,
       set signal = output_signal. Find target node's receiving port
       (input or control), update signal, sync target brightness.
    4. Clear own output_ports signals.
    5. Clear own control_ports signals.
    6. Clear own input_ports signals.

    Connections are never deleted.

    Args:
        grid_layer_1 ~ grid_layer_5: five grid layers

    Returns:
        tuple: (grid_layer_1, ..., grid_layer_5) after signal propagation
    """
    all_grids = [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]

    for grid in all_grids:
        for i in range(len(grid)):
            if not isinstance(grid[i], Point):
                continue
            point = grid[i]

            input_signals = []
            for input_connection in point.input_ports:
                signal_value = input_connection.get("signal", 0)
                if signal_value > 0:
                    input_signals.append(signal_value)

            control_triggered = False
            for control_connection in point.control_ports:
                if control_connection.get("signal", 0) > CONTROL_SIGNAL_THRESHOLD:
                    control_triggered = True
                    break

            if control_triggered:
                for control_connection in point.control_ports:
                    control_connection["signal"] = 0
                for input_connection in point.input_ports:
                    input_connection["signal"] = 0
                continue

            output_signal = max(input_signals) if input_signals else 0

            for output_connection in point.output_ports:
                output_connection["signal"] = output_signal
                target_index = output_connection.get("target_point_index", -1)
                if 0 <= target_index < TOTAL_CELLS and isinstance(grid[target_index], Point):
                    target_point = grid[target_index]
                    for receiving_connection in target_point.input_ports:
                        if receiving_connection.get("target_point_index") == i:
                            receiving_connection["signal"] = output_signal
                    for receiving_connection in target_point.control_ports:
                        if receiving_connection.get("target_point_index") == i:
                            receiving_connection["signal"] = output_signal
                    target_point.brightness = min(max(target_point.brightness, output_signal), MAX_BRIGHTNESS)

            for output_connection in point.output_ports:
                output_connection["signal"] = 0
            for control_connection in point.control_ports:
                control_connection["signal"] = 0
            for input_connection in point.input_ports:
                input_connection["signal"] = 0

    return grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5


# ===========================================================================
# Display Function
# ===========================================================================
def display_grid(grid: list, grid_name: str) -> None:
    """Print the grid in 32x32 matrix format.

    Prints brightness for Point objects and the numeric value otherwise.

    Args:
        grid: list of length TOTAL_CELLS
        grid_name: display name for the grid
    """
    print(f"====== {grid_name} ======")
    for i in range(0, TOTAL_CELLS, GRID_SIDE_LENGTH):
        row = []
        for j in range(i, i + GRID_SIDE_LENGTH):
            if isinstance(grid[j], Point):
                row.append(str(grid[j].brightness))
            else:
                row.append(str(grid[j]))
        print(' '.join(row))
    print()


# ===========================================================================
# API Functions
# ===========================================================================
def initialize_api_ports(grid_layer_1: list, grid_layer_5: list) -> tuple:
    """Initialize API input and output port Points.

    Creates 32 brightness=0 Points in grid_layer_1 first row (index 0~31)
    as API input ports, and 32 in grid_layer_5 last row (index 992~1023)
    as API output ports.

    Args:
        grid_layer_1: grid layer 1
        grid_layer_5: grid layer 5

    Returns:
        tuple: (grid_layer_1, grid_layer_5) with API ports initialized
    """
    for port_index in range(API_PORT_COUNT):
        grid_layer_1[port_index] = Point(center_index=port_index, brightness=0)

    for port_index in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        grid_layer_5[port_index] = Point(center_index=port_index, brightness=0)

    return grid_layer_1, grid_layer_5


def set_api_input(grid_layer_1: list, binary_string: str) -> bool:
    """Write a 32-bit binary string to grid_layer_1 first row API ports.

    '1' -> brightness=9, signal=9; '0' -> brightness=0, signal=0.
    Adds a one-way input_ports record with source=-1, target=port_index,
    signal=9/0, port_type="input". Short input is zero-padded to 32,
    long input is truncated to 32.

    Args:
        grid_layer_1: grid layer 1
        binary_string: binary string, e.g. "01001000..."

    Returns:
        bool: True on success, False on invalid character
    """
    if len(binary_string) < API_PORT_COUNT:
        binary_string = binary_string.ljust(API_PORT_COUNT, '0')
    elif len(binary_string) > API_PORT_COUNT:
        binary_string = binary_string[:API_PORT_COUNT]

    for port_index in range(API_PORT_COUNT):
        character = binary_string[port_index]
        if character == '1':
            signal_value = ACTIVE_BRIGHTNESS
        elif character == '0':
            signal_value = 0
        else:
            print(f"[API] Error: binary_string position {port_index} is not 0 or 1, received '{character}'")
            return False

        if isinstance(grid_layer_1[port_index], Point):
            grid_layer_1[port_index].brightness = signal_value
            grid_layer_1[port_index].input_ports.clear()
            grid_layer_1[port_index].input_ports.append({
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value,
                "port_type": "input"
            })
        else:
            grid_layer_1[port_index] = Point(center_index=port_index, brightness=signal_value)
            grid_layer_1[port_index].input_ports.append({
                "source_point_index": -1,
                "target_point_index": port_index,
                "signal": signal_value,
                "port_type": "input"
            })

    print(f"[API] set_api_input: wrote 32-bit binary -> {binary_string}")
    return True


def get_api_output(grid_layer_5: list) -> str:
    """Read grid_layer_5 last row API ports and convert to UTF-8 character.

    Reads 32 Points at indices 992~1023. brightness >= 5 -> '1', < 5 -> '0'.
    Concatenates into 32-bit binary, splits into 4 bytes of 8 bits,
    decodes as UTF-8. Returns the raw binary string on decode failure.

    Args:
        grid_layer_5: grid layer 5

    Returns:
        str: UTF-8 decoded character, or raw binary string on failure
    """
    binary_output = ""
    for port_index in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        if isinstance(grid_layer_5[port_index], Point):
            if grid_layer_5[port_index].brightness >= 5:
                binary_output += "1"
            else:
                binary_output += "0"
        else:
            binary_output += "0"

    try:
        byte_list = []
        for byte_index in range(0, API_PORT_COUNT, 8):
            byte_string = binary_output[byte_index:byte_index + 8]
            byte_value = int(byte_string, 2)
            byte_list.append(byte_value)
        byte_data = bytes(byte_list)
        utf8_character = byte_data.decode("utf-8")
        return utf8_character
    except (ValueError, UnicodeDecodeError):
        return binary_output


# ===========================================================================
# Global Variable Initialization
# ===========================================================================
grid_layer_1 = [0] * TOTAL_CELLS
grid_layer_2 = [0] * TOTAL_CELLS
grid_layer_3 = [0] * TOTAL_CELLS
grid_layer_4 = [0] * TOTAL_CELLS
grid_layer_5 = [0] * TOTAL_CELLS

active_points_grid_layer_1 = []
active_points_grid_layer_2 = []
active_points_grid_layer_3 = []
active_points_grid_layer_4 = []
active_points_grid_layer_5 = []

binary_string_list = []
random_pool = []

# ===========================================================================
# Seed Point Placement: indices 30~39, brightness=SEED_BRIGHTNESS
# ===========================================================================
for i in range(10):
    grid_layer_1[i + 30] = Point(center_index=i + 30, brightness=SEED_BRIGHTNESS)
for i in range(10):
    grid_layer_2[i + 30] = Point(center_index=i + 30, brightness=SEED_BRIGHTNESS)
for i in range(10):
    grid_layer_3[i + 30] = Point(center_index=i + 30, brightness=SEED_BRIGHTNESS)
for i in range(10):
    grid_layer_4[i + 30] = Point(center_index=i + 30, brightness=SEED_BRIGHTNESS)
for i in range(10):
    grid_layer_5[i + 30] = Point(center_index=i + 30, brightness=SEED_BRIGHTNESS)

# ===========================================================================
# API Port Initialization
# ===========================================================================
grid_layer_1, grid_layer_5 = initialize_api_ports(grid_layer_1, grid_layer_5)

# ===========================================================================
# Main Loop
# ===========================================================================
while True:
    # ===== Stage A: Input Processing =====
    active_points_grid_layer_1.clear()
    active_points_grid_layer_2.clear()
    active_points_grid_layer_3.clear()
    active_points_grid_layer_4.clear()
    active_points_grid_layer_5.clear()
    binary_string_list.clear()
    random_pool.clear()

    user_input_raw = input("input:")
    input_character_list = list(user_input_raw)
    binary_string_list = []
    padded_binary_string_list = []

    for character in input_character_list:
        unicode_encoded_bytes = character.encode("utf-8")
        binary_string = ''.join(f'{byte:08b}' for byte in unicode_encoded_bytes)
        padded_binary_string = binary_string.ljust(GRID_SIDE_LENGTH, '0')[:GRID_SIDE_LENGTH]
        print(f"'{character}' -> {padded_binary_string}")
        padded_binary_string_list.append(padded_binary_string)
        binary_string_list.append(padded_binary_string)

    random_pool = build_random_pool(binary_string_list)
    print(f"[Debug] random_pool length: {len(random_pool)}")

    api_input_string = padded_binary_string_list[0]
    set_api_input(grid_layer_1, api_input_string)

    # ===== Stage B: Active Point Detection =====
    active_points_grid_layer_1 = detect_active_points(grid_layer_1)
    active_points_grid_layer_2 = detect_active_points(grid_layer_2)
    active_points_grid_layer_3 = detect_active_points(grid_layer_3)
    active_points_grid_layer_4 = detect_active_points(grid_layer_4)
    active_points_grid_layer_5 = detect_active_points(grid_layer_5)

    print(f"[Debug] active_points count - Layer1:{len(active_points_grid_layer_1)}, Layer2:{len(active_points_grid_layer_2)}, Layer3:{len(active_points_grid_layer_3)}, Layer4:{len(active_points_grid_layer_4)}, Layer5:{len(active_points_grid_layer_5)}")

    # ===== Stage C: Diamond Render (Additive) =====
    grid_layer_1 = render_grid(grid_layer_1, active_points_grid_layer_1)
    grid_layer_2 = render_grid(grid_layer_2, active_points_grid_layer_2)
    grid_layer_3 = render_grid(grid_layer_3, active_points_grid_layer_3)
    grid_layer_4 = render_grid(grid_layer_4, active_points_grid_layer_4)
    grid_layer_5 = render_grid(grid_layer_5, active_points_grid_layer_5)

    # ===== Stage D: Anneal (Subtractive) + Connection Establishment =====
    grid_layer_1 = anneal_and_connect(grid_layer_1, active_points_grid_layer_1, random_pool, "grid_layer_1")
    grid_layer_2 = anneal_and_connect(grid_layer_2, active_points_grid_layer_2, random_pool, "grid_layer_2")
    grid_layer_3 = anneal_and_connect(grid_layer_3, active_points_grid_layer_3, random_pool, "grid_layer_3")
    grid_layer_4 = anneal_and_connect(grid_layer_4, active_points_grid_layer_4, random_pool, "grid_layer_4")
    grid_layer_5 = anneal_and_connect(grid_layer_5, active_points_grid_layer_5, random_pool, "grid_layer_5")

    # ===== Stage E: Clear Non-Point Brightness =====
    grid_layer_1 = clear_non_point_brightness(grid_layer_1)
    grid_layer_2 = clear_non_point_brightness(grid_layer_2)
    grid_layer_3 = clear_non_point_brightness(grid_layer_3)
    grid_layer_4 = clear_non_point_brightness(grid_layer_4)
    grid_layer_5 = clear_non_point_brightness(grid_layer_5)

    # ===== Stage F: Cross-Layer Preload =====
    grid_layer_2 = preload_next_grid(grid_layer_1, grid_layer_2, active_points_grid_layer_1)
    grid_layer_3 = preload_next_grid(grid_layer_2, grid_layer_3, active_points_grid_layer_2)
    grid_layer_4 = preload_next_grid(grid_layer_3, grid_layer_4, active_points_grid_layer_3)
    grid_layer_5 = preload_next_grid(grid_layer_4, grid_layer_5, active_points_grid_layer_4)

    # ===== Stage G: Node Movement =====
    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = execute_movement_phase(
        grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
    )

    # ===== Stage H: Transistor-Style Signal Propagation =====
    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = transistor_style_signal_propagation(
        grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
    )

    # ===== Stage I: Display Grids =====
    display_grid(grid_layer_1, "Grid Layer 1")
    display_grid(grid_layer_2, "Grid Layer 2")
    display_grid(grid_layer_3, "Grid Layer 3")
    display_grid(grid_layer_4, "Grid Layer 4")
    display_grid(grid_layer_5, "Grid Layer 5")

    # ===== Stage J: API Output =====
    api_output_character = get_api_output(grid_layer_5)
    print(f"[API Output] UTF-8 character: {api_output_character}")

    # ===== Stage K: Next Round =====