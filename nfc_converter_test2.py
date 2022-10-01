import pandas as pd

def test1():
    key = 846677508
    print(f"key = {key}, 0x{key:X}")

    wei = 1146944771
    print(f"{wei} 0x{wei:X}")

    for i in range(20):
        # A = 30
        # top = wei >> A
        # top = top << A
        # cut = wei - top
        # cut = cut >> i
        # print(f"{i} {cut} {top:X} 0x{cut:X}")

        cut = wei >> i
        print(f"{i} {cut} 0x{cut:X}")


    # print()
    # key = 6482599
    # print(f"key = {key}, 0x{key:X}")

    # wei = 829772546
    # # for i in range(20):
    # #     A = 30
    # #     top = wei >> A
    # #     top = top << A
    # #     cut = wei - top
    # #     cut = cut >> i
    # #     print(f"{i} {cut} {top:X} 0x{cut:X}")

    # cut = converter(wei)
    # print(f"{cut} 0x{cut:X}")


def cut_top(val, bits):
    top = val >> bits
    top = top << bits
    cut = val - top
    return cut

def test2():
    df = pd.read_csv('nfc_keys.csv')
    df['usb_hex'] = df['usb_dec'].apply(lambda x: f"{x:X}")
    df['weigand_hex'] = df['weigand_dec'].apply(lambda x: f"{x:X}")
    df['convert1'] = df['weigand_dec'].apply(lambda x: f"{x >> 7:X} {cut_top(x, 7) << 1:0>3b}")
    df['convert2'] = df['weigand_dec'].apply(lambda x: f"{(cut_top(x, 31) >> 7) + ((x&0b10)>>1):X}")

    # # df['convert2'] = df['weigand raw'].apply(lambda x: converter(x))
    # df['inside_hex'] = df['inside'].apply(lambda x: f"{x:X}")
    # df['outside2'] = df['outside'].apply(lambda x: x[4:])
    # df['out_dec'] = df['outside2'].apply(lambda x: int(x, 16))
    # # df['convert2'] = df['weigand raw'].apply(lambda x: f"{x << 1:X} {x >> 7:X} {cut_top(x, 7) << 1:X}")
    # # df['convert2'] = df['weigand raw'].apply(lambda x: f"{x << 1:X}")
    # df['convert2_dec'] = df['convert2'].apply(lambda x: int(x, 16))

    print(df)
    df.to_csv(f'nfc_keys_out.csv')

    # cols = [
    #     'note',
    #     'weigand raw',
    #     'weigand_hex',
    #     'convert',
    #     'convert2',
    #     'inside_hex',
    #     'outside',
    #     'outside2',
    #     'inside',
    #     'out_dec',
    #     'convert2_dec',
    # ]
    # print(df[cols])
    # df[cols].to_csv(f'testing_keys_out.csv')
    pass

def weigand_to_rfid(val: int):
    """
    Converts the decimal string from weigand RFID receiver to the
    decimal string printed on keyfobs and also what USB RFID receiver
    outputs.
    """
    # Remove top bit - doesn't seem to be used
    bits = 31
    top = val >> bits
    top = top << bits
    result = val - top

    # Shift down by 7 - this aligns it correctly and cuts lower bits
    result = result >> 7

    # Extract bit 1 (2nd bit) which is used as bit 0 in final
    result = result + ((val & 0b10) >> 1)

    return result

def old_door_pi_hex_str_to_rfid(hex_str: str):
    """
    Converts the hex string from old doorpi arduino to the
    decimal string printed on keyfobs and also what USB RFID 
    receiver outputs.
    """
    # Chop off the first 4 hex chars (2 bytes). These two dont
    # appear in the hex conversion of the decimal value written
    # on keyfobs and output from USB RFID reader.
    hex_str = hex_str[4:]
    return int(hex_str, 16)

def test3():
    df = pd.read_csv('testing_keys.csv')
    df['outside_converted'] = df['outside'].apply(lambda x: old_door_pi_hex_str_to_rfid(x))
    df['weigand_converted'] = df['weigand raw'].apply(lambda x: weigand_to_rfid(x))
    df['pass'] = (df['inside'] == df['outside_converted']) & (df['inside'] == df['weigand_converted'])

    print(df)
    df.to_csv(f'testing_keys_test3.csv')
    pass


if __name__ == "__main__":
    test1()
    # test2()
    # test3()
