bits = 26
value = 24051360 << 1

# The trailing half of the bits are odd parity (including parity bit).
# Trailing half is what arrives last - the low bits.
count_trailing = 0
for i in range(0, bits//2):
    if (value >> i) & 0x01 == 0x01:
        count_trailing += 1
trailing_parity_odd = (count_trailing % 2 == 1)

# Leading half is even parity (high bits)
count_leading = 0
for i in range(bits//2, bits):
    if (value >> i) & 0x01 == 0x01:
        count_leading += 1
leading_parity_even = (count_leading % 2 == 0)

print(f"{trailing_parity_odd}")
print(f"{leading_parity_even}")

print(f"{value:X}")

if trailing_parity_odd and leading_parity_even:
    # Extract the card value from inner 24-bits (drop first and last parity bits)
    card_id = (value >> 1) & (2**(bits-2)-1)
    print(f"low cut: {(value >> 1):X}")
    print(f"high cut: {card_id:X}")
    print(f"valid: {card_id:X=}")
else:
    print(f"invalid")