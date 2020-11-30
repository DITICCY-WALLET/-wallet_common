

def hex_to_int(h):
    if h.startswith('0x') and len(h) == 2:
        h = h + '0'
    elif len(h) == 0:
        h = '0'
    return int(h, base=16)


def int_to_hex(i, has_0x=True):
    if has_0x:
        offset = 0
    else:
        offset = 2
    return hex(i)[offset:]


def add_0x(h: str):
    if h.startswith('0x'):
        return h
    return '0x' + h


def del_0x(h: str):
    if h.startswith('0x'):
        return h[2:]
    return h


def is_number(value: str) -> bool:
    value_split = value.split('.')
    if len(value_split) > 2:
        return False
    for digit in value_split:
        if not digit.isdigit():
            return False
    return True



