"""
wiegand: 2802361858
key: 0005116237
outside reader: 3F004E114D
"""
import pandas as pd

def converter(weigand):
    A = 30
    top = weigand >> A
    top = top << A
    cut = weigand - top
    cut = cut >> 7
    cut += 1
    return cut

def test1():
    key = 5116237
    print(f"key = {key}, 0x{key:X}")

    wei = 2802361858
    cut = converter(wei)
    print(f"{cut} 0x{cut:X}")
    # for i in range(20):
    #     A = 30
    #     top = wei >> A
    #     top = top << A
    #     cut = wei - top
    #     cut = cut >> i
    #     print(f"{i} {cut} {top:X} 0x{cut:X}")

    # A = 30
    # top = wei >> A
    # top = top << A
    # cut = wei - top
    # cut = cut >> 7
    # print(f"{cut} 0x{cut:X}")


    print()
    key = 6482599
    print(f"key = {key}, 0x{key:X}")

    wei = 829772546
    # for i in range(20):
    #     A = 30
    #     top = wei >> A
    #     top = top << A
    #     cut = wei - top
    #     cut = cut >> i
    #     print(f"{i} {cut} {top:X} 0x{cut:X}")

    cut = converter(wei)
    print(f"{cut} 0x{cut:X}")

def cut_top(val, bits):
    top = val >> bits
    top = top << bits
    cut = val - top
    return cut

def test2():
    df = pd.read_csv('testing_keys.csv')
    # df['convert2'] = df['weigand raw'].apply(lambda x: converter(x))
    df['inside_hex'] = df['inside'].apply(lambda x: f"{x:X}")
    df['outside2'] = df['outside'].apply(lambda x: x[4:])
    df['out_dec'] = df['outside2'].apply(lambda x: int(x, 16))
    df['weigand_hex'] = df['weigand raw'].apply(lambda x: f"{x:X}")
    # df['convert2'] = df['weigand raw'].apply(lambda x: f"{x << 1:X} {x >> 7:X} {cut_top(x, 7) << 1:X}")
    df['convert2'] = df['weigand raw'].apply(lambda x: f"{x >> 7:X} {cut_top(x, 7) << 1:0>3b}")
    df['convert2'] = df['weigand raw'].apply(lambda x: f"{(cut_top(x, 31) >> 7) + ((x&0b10)>>1):X}")
    # df['convert2'] = df['weigand raw'].apply(lambda x: f"{x << 1:X}")
    df['convert2_dec'] = df['convert2'].apply(lambda x: int(x, 16))

    cols = [
        'note',
        'weigand raw',
        'weigand_hex',
        'convert',
        'convert2',
        'inside_hex',
        'outside',
        'outside2',
        'inside',
        'out_dec',
        'convert2_dec',
    ]
    print(df[cols])
    pass

if __name__ == "__main__":
    # test1()
    test2()
