import pytest
import wol


@pytest.mark.parametrize(
    'invalid_mac',
    [
        'abcdefabcdef123456789',
        '',
        'abcdefabcdeX',
        None,
        'a:bcdef123456',
        int('abcdefabcdef', 16),
        '_'.join(['aa'] * 6),
    ],
)
def test_invalid_mac_address(invalid_mac):
    with pytest.raises(ValueError):
        wol.clean_mac(invalid_mac)


@pytest.mark.parametrize(
    'in_mac,expected',
    [
        ('a' * 12, 'A' * 12),
        ('A' * 12, 'A' * 12),
        (':'.join(['aa'] * 6), 'A' * 12),
        ('.'.join(['aa'] * 6), 'A' * 12),
        ('-'.join(['aa'] * 6), 'A' * 12),
    ],
)
def test_clean_mac(in_mac, expected):
    assert wol.clean_mac(in_mac) == expected
