# -*- coding: utf-8 -*-
"""Debug script to test API signal injection."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from app import *

# Override to only process first input
input_list = read_input_from_text_file()
if input_list:
    input_list = input_list[:1]
    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = load_full_grid_from_file()
    grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
    
    user_input = input_list[0]
    print(f'Processing: {user_input}')
    
    grid_layer_1 = clear_non_point_brightness(grid_layer_1, 1)
    grid_layer_2 = clear_non_point_brightness(grid_layer_2, 2)
    grid_layer_3 = clear_non_point_brightness(grid_layer_3, 3)
    grid_layer_4 = clear_non_point_brightness(grid_layer_4, 4)
    grid_layer_5 = clear_non_point_brightness(grid_layer_5, 5)
    for g in [grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5]:
        clear_all_connection_signals(g)
    
    input_character_list = list(user_input)
    padded_binary_string_list = []
    binary_string_list = []
    for character in input_character_list:
        unicode_encoded_bytes = character.encode('utf-8')
        binary_string = ''.join(f'{byte:08b}' for byte in unicode_encoded_bytes)
        padded_binary_string = binary_string.ljust(GRID_SIDE_LENGTH, '0')[:GRID_SIDE_LENGTH]
        padded_binary_string_list.append(padded_binary_string)
        binary_string_list.append(padded_binary_string)
    random_pool = build_random_pool(binary_string_list)
    api_input_string = padded_binary_string_list[0]
    print(f'API input binary: {api_input_string}')
    set_api_input(grid_layer_1, api_input_string)
    grid_layer_1, grid_layer_5 = guard_api_rows(grid_layer_1, grid_layer_5)
    
    # Check API row state
    print('API row api_signal values (non-zero):')
    for i in range(32):
        p = grid_layer_1[i]
        if isinstance(p, Point) and p.api_signal > 0:
            print(f'  [{i}] brightness={p.brightness} api_signal={p.api_signal}')
    
    # Check row 1 Point cells
    print('Row 1 Point cells:')
    for i in range(32, 64):
        cell = grid_layer_1[i]
        if isinstance(cell, Point):
            print(f'  [{i}] Point brightness={cell.brightness}')
    
    # Run signal propagation
    grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5 = transistor_style_signal_propagation(
        grid_layer_1, grid_layer_2, grid_layer_3, grid_layer_4, grid_layer_5
    )
    propagate_to_output_api(grid_layer_5)
    
    # Check row 1 after propagation
    print('Row 1 after propagation (non-zero brightness):')
    for i in range(32, 64):
        cell = grid_layer_1[i]
        if isinstance(cell, Point) and cell.brightness > 0:
            print(f'  [{i}] Point brightness={cell.brightness}')
    
    # Check if any row 1 node got signal
    print('Row 1 after propagation (all):')
    for i in range(32, 64):
        cell = grid_layer_1[i]
        if isinstance(cell, Point):
            print(f'  [{i}] brightness={cell.brightness}')
        else:
            print(f'  [{i}] {type(cell).__name__} = {cell}')
    
    # Check output API
    print('Output API row (non-zero api_signal):')
    for i in range(TOTAL_CELLS - API_PORT_COUNT, TOTAL_CELLS):
        p = grid_layer_5[i]
        if isinstance(p, Point) and p.api_signal > 0:
            print(f'  [{i}] brightness={p.brightness} api_signal={p.api_signal}')
    
    binary_output, utf8_output = get_api_output(grid_layer_5)
    print(f'Output: {binary_output} -> {utf8_output}')