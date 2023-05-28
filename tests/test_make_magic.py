import pytest
import wol


@pytest.mark.parametrize(
    'mac_address,secureon,expected',
    [
        ('f' * 12, None, b'\xff' * 6 + b'\xff' * 6 * 16),
        ('ab' * 6, None, b'\xff' * 6 + b'\xab' * 6 * 16),
        ('ab' * 6, 'b' * 12, b'\xff' * 6 + b'\xab' * 6 * 16 + b'\xbb' * 6),
    ],
)
def test_make_magic_packet(mac_address, secureon, expected):
    packet = wol.make_magic(mac_address, secureon)
    assert packet == expected
