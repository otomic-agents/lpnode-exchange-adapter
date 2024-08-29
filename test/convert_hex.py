import base58
import binascii

def base58_to_hex(base58_str):
    byte_str = base58.b58decode(base58_str)
    hex_str = binascii.hexlify(byte_str).decode()
    return hex_str
# Test
base58_str = "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"
hex_str = base58_to_hex(base58_str)
print(hex_str)