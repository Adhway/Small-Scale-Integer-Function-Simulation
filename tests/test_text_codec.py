import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from text_codec import decode_blocks_to_bytes, decode_text, digits_per_byte, encode_text


def toy_rsa_roundtrip(text: str, modulus: int, public_exponent: int, private_exponent: int) -> None:
    encoded = encode_text(text, modulus)
    assert encoded.blocks
    assert all(0 <= block < modulus for block in encoded.blocks)
    ciphertext = [pow(block, public_exponent, modulus) for block in encoded.blocks]
    recovered_digits = [pow(block, private_exponent, modulus) for block in ciphertext]
    assert recovered_digits == encoded.blocks
    assert decode_blocks_to_bytes(recovered_digits, modulus, encoded.digits_per_byte) == text.encode("utf-8")
    assert decode_text(recovered_digits, modulus, encoded.digits_per_byte) == text


def test_ascii_text_roundtrip_with_n15():
    # N=15 => phi=8; e=d=3 is the demo's valid toy RSA key.
    toy_rsa_roundtrip("HELLO QUANTUM", modulus=15, public_exponent=3, private_exponent=3)


def test_unicode_text_roundtrip_with_n21():
    # N=21 => phi=12; e=5 and d=5 are mutual inverses modulo 12.
    toy_rsa_roundtrip("Café ☕", modulus=21, public_exponent=5, private_exponent=5)


def test_fixed_width_can_represent_all_bytes():
    assert 15 ** digits_per_byte(15) > 255
    assert 21 ** digits_per_byte(21) > 255