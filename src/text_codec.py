"""Educational text-to-block codec for tiny textbook-RSA moduli.

UTF-8 bytes are represented as fixed-width base-N digits. Every digit is in
[0, N-1], so it can be encrypted with the demo's tiny RSA modulus. This is a
teaching encoding only; it is not padding and does not provide secure RSA.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EncodedText:
    text: str
    utf8_bytes: bytes
    blocks: list[int]
    digits_per_byte: int


def digits_per_byte(modulus: int) -> int:
    """Return the fixed number of base-modulus digits needed for one byte."""
    if modulus < 2:
        raise ValueError("Modulus must be at least 2.")
    width = 1
    while modulus ** width <= 255:
        width += 1
    return width


def encode_text(text: str, modulus: int) -> EncodedText:
    """Encode UTF-8 text into base-modulus digits suitable for toy RSA blocks."""
    width = digits_per_byte(modulus)
    raw = text.encode("utf-8")
    blocks: list[int] = []
    for byte_value in raw:
        digit_group = [0] * width
        remaining = byte_value
        for index in range(width - 1, -1, -1):
            digit_group[index] = remaining % modulus
            remaining //= modulus
        if remaining:
            raise ValueError("The chosen modulus cannot encode a UTF-8 byte.")
        blocks.extend(digit_group)
    return EncodedText(text=text, utf8_bytes=raw, blocks=blocks, digits_per_byte=width)


def decode_blocks_to_bytes(blocks: list[int], modulus: int, width: int) -> bytes:
    """Rebuild the original byte sequence from decrypted base-modulus digits."""
    if width < 1 or len(blocks) % width != 0:
        raise ValueError("The decrypted digit count is not a whole number of byte groups.")
    raw = bytearray()
    for start in range(0, len(blocks), width):
        value = 0
        for digit in blocks[start:start + width]:
            if not 0 <= digit < modulus:
                raise ValueError(f"Digit {digit} is outside the base-{modulus} range.")
            value = value * modulus + digit
        if value > 255:
            raise ValueError(f"Digit group reconstructed invalid byte value {value}.")
        raw.append(value)
    return bytes(raw)


def decode_text(blocks: list[int], modulus: int, width: int) -> str:
    """Decode decrypted base-modulus digits back into UTF-8 text."""
    return decode_blocks_to_bytes(blocks, modulus, width).decode("utf-8")


def group_digits(blocks: list[int], width: int) -> list[list[int]]:
    """Group base-modulus digits, one group per original UTF-8 byte."""
    if width < 1 or len(blocks) % width != 0:
        raise ValueError("The digit count must be divisible by the group width.")
    return [blocks[index:index + width] for index in range(0, len(blocks), width)]
