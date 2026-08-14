from typing import List



# 文本编码/解码(text_io)
def encode_text(text:str) -> List[int]:

    # '你' → utf8: [228, 189, 160] → "000228000189000160" → [0,0,0,2,2,8, 0,0,0,1,8,9, 0,0,0,1,6,0]

    digits = []
    for char in text:
        utf8_bytes = char.encode('utf-8')
        for byte in utf8_bytes:
            padded = f"{byte:06d}"
            for d in padded:
                digits.append(int(d))
    return digits


def decode_output(output_values: List[int]) -> str:
    bytes_list = []

    # 每6个一组
    for i in range(0, len(output_values), 6):
        group = output_values[i:i + 6]
        if len(group) < 6:
            break

        # 检查该组是否有信号（任何非零值）
        has_signal = any(v > 0 for v in group)
        if not has_signal:
            continue  # 无信号的组跳过

        # 拼接6位数字为整数值
        byte_val = 0
        for d in group:
            byte_val = byte_val * 10 + d

        # 验证字节值范围
        if 0 <= byte_val <= 255:
            bytes_list.append(byte_val)

    # 按UTF-8规则解码
    result = []
    i = 0
    while i < len(bytes_list):
        b = bytes_list[i]

        # 根据UTF-8首字节确定字符长度
        if b < 128:
            length = 1
        elif b < 224:
            length = 2
        elif b < 240:
            length = 3
        else:
            length = 4

        if i + length <= len(bytes_list):
            try:
                char_bytes = bytes(bytes_list[i:i + length])
                char = char_bytes.decode('utf-8')
                result.append(char)
                i += length
            except (UnicodeDecodeError,ValueError):
                i += 1
        else:
            break

    return ''.join(result)