import pytest

from wol import (
    GroupConfig,
    parse_config_dict,
    Config,
    DefaultConfig,
    MacAddress,
    parse_mac,
    merge_cli_and_config,
)

parse_config_args = [
    (
        {'default': {'ip': '123.123.123.123'}},
        Config(
            default=DefaultConfig(ip='123.123.123.123'),
            groups=set(),
        ),
    ),
    (
        {
            'default': {
                'ip': '123.123.123.123',
                'port': 9,
                'repeat': 16,
                'interface': '127.0.0.2',
                'macs': [
                    'ab:ab:ab:ab:ab:ab',
                    'ba:ba:ba:ba:ba:ba',
                    'cd:cd:cd:cd:cd:cd/ab:ab:ab:ab:ab:ab',
                ],
                'groups': [],
            }
        },
        Config(
            default=DefaultConfig(
                ip='123.123.123.123',
                port=9,
                repeat=16,
                interface='127.0.0.2',
                macs={
                    MacAddress('ab:ab:ab:ab:ab:ab'),
                    MacAddress('ba:ba:ba:ba:ba:ba'),
                    MacAddress('cd:cd:cd:cd:cd:cd', 'ab:ab:ab:ab:ab:ab'),
                },
                groups=set(),
            ),
            groups=set(),
        ),
    ),
    (
        {
            'default': {
                'ip': '123.123.123.123',
                'port': 9,
                'repeat': 16,
                'interface': '127.0.0.2',
                'macs': [
                    'ab:ab:ab:ab:ab:ab',
                    'ba:ba:ba:ba:ba:ba',
                    'cd:cd:cd:cd:cd:cd/ab:ab:ab:ab:ab:ab',
                ],
                'groups': ['group one'],
            },
            'groups': [
                {
                    'name': 'group one',
                    'macs': [
                        'bc:bc:bc:bc:bc:bc',
                        'fe-fe-fe-fe-fe-fe',
                    ],
                },
                {
                    'name': 'group two',
                    'macs': [
                        'de:de:de:de:de:de',
                        '12-12-12-12-12-12',
                    ],
                    'also': ['group one'],
                },
            ],
        },
        Config(
            default=DefaultConfig(
                ip='123.123.123.123',
                port=9,
                repeat=16,
                interface='127.0.0.2',
                macs={
                    MacAddress('ab:ab:ab:ab:ab:ab'),
                    MacAddress('ba:ba:ba:ba:ba:ba'),
                    MacAddress('cd:cd:cd:cd:cd:cd', 'ab:ab:ab:ab:ab:ab'),
                },
                groups={'group one'},
            ),
            groups={
                GroupConfig(
                    name='group one',
                    macs={
                        MacAddress('bc:bc:bc:bc:bc:bc'),
                        MacAddress('fe-fe-fe-fe-fe-fe'),
                    },
                ),
                GroupConfig(
                    name='group two',
                    macs={
                        MacAddress('de:de:de:de:de:de'),
                        MacAddress('12-12-12-12-12-12'),
                    },
                    also={'group one'},
                ),
            },
        ),
    ),
]


def test_group_config_eq():
    cfg_1 = GroupConfig(name='a', ip='123')
    cfg_2 = GroupConfig(name='b', ip='123')
    cfg_3 = GroupConfig(name='a', ip='abc')

    assert cfg_1 == cfg_3
    assert cfg_1 != cfg_2


def test_group_config_hash():
    cfg_1 = GroupConfig(name='a', ip='123')
    cfg_2 = GroupConfig(name='b', ip='123')
    cfg_3 = GroupConfig(name='a', ip='abc')

    assert len({cfg_1, cfg_2, cfg_3}) == 2


@pytest.mark.parametrize('test_input,expected', parse_config_args)
def test_parse_config(test_input, expected):
    result = parse_config_dict(test_input)
    assert result == expected


@pytest.mark.parametrize(
    'input_mac,expected',
    [
        ('ab:ab:ab:ab:ab:ab', MacAddress('ab:ab:ab:ab:ab:ab')),
        ('AB-AB-AB-AB-AB-AB', MacAddress('AB-AB-AB-AB-AB-AB')),
        ('ABABABABABAB', MacAddress('ABABABABABAB')),
        (
            'ab:ab:ab:ab:ab:ab/ba:ba:ba:ba:ba:ba',
            MacAddress('ab:ab:ab:ab:ab:ab', 'ba:ba:ba:ba:ba:ba'),
        ),
    ],
)
def test_parse_mac(input_mac, expected):
    result = parse_mac(input_mac)
    assert result == expected


@pytest.mark.parametrize(
    'cli,config,expected',
    [
        (
            DefaultConfig(),
            DefaultConfig(),
            DefaultConfig(),
        ),
        (
            DefaultConfig(interface='127.0.0.2'),
            DefaultConfig(),
            DefaultConfig(interface='127.0.0.2'),
        ),
        (
            DefaultConfig(interface='127.0.0.2'),
            DefaultConfig(interface='0.0.0.0'),
            DefaultConfig(interface='127.0.0.2'),
        ),
        (
            DefaultConfig(
                interface='127.0.0.2', macs={MacAddress('ab:ab:ab:ab:ab:ab')}
            ),
            DefaultConfig(interface='0.0.0.0', ip='123.123.123.123'),
            DefaultConfig(
                ip='123.123.123.123',
                interface='127.0.0.2',
                macs={MacAddress('ab:ab:ab:ab:ab:ab')},
            ),
        ),
    ],
)
def test_merge_cli_and_config(cli, config, expected):
    result = merge_cli_and_config(cli, config)
    assert result == expected
