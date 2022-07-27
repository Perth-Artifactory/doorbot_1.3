"""
wiegand: 2802361858
key: 0005116237
outside reader: 3F004E114D
"""

def converter(weigand):
    A = 30
    top = weigand >> A
    top = top << A
    cut = weigand - top
    cut = cut >> 7
    cut += 1
    return cut

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
