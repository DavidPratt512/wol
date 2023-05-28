import pytest
from wol import StructuredLog


def test_store_headers_after_create():
    headers = [
        'header1',
        'header2',
        'im_not_creative',
    ]
    log = StructuredLog(headers)

    assert list(log.headers) == [
        'header1',
        'header2',
        'im_not_creative',
    ]


def test_headers_are_immutable():
    headers = ('header1', 'header2', 'im_not_creative')
    log = StructuredLog(headers)

    with pytest.raises(AttributeError):
        log.headers.append('another_header')

    assert log.headers == headers

    with pytest.raises(AttributeError):
        log.headers = ['new_headers']

    assert log.headers == headers


def test_stores_empty_rows_immediately_after_creation():
    log = StructuredLog(['some_headers'])
    assert len(log._rows) == 0


def test_dunder_str_is_only_headers_immediately_after_creation():
    log = StructuredLog(['some_header', 'another_header'])
    log_string = str(log)
    assert 'some_header' in log_string and 'another_header' in log_string


def test_append_row_using_headers():
    log = StructuredLog(['some_header', 'another_header'])
    log.append(some_header='some value', another_header='another value')
    assert len(log._rows) == 1


def test_append_row_blank_values_are_StructuredLogBLANK():
    log = StructuredLog(['some_header', 'another_header'])
    log.append(some_header='some value')
    assert log._rows[0].another_header is StructuredLog._BLANK


def test_log_updated_is_false_immediately_after_creation():
    log = StructuredLog(['some_header', 'another_header'])
    assert not log._changed_since_last_construct


def test_log_string_is_only_headers_immediately_after_creation():
    log = StructuredLog(['some_header', 'another_header'])
    assert log._log_string == 'some_header another_header'


def test_updated_is_true_after_append():
    log = StructuredLog(['some_header', 'another_header'])
    log.append(some_header='some value')
    assert log._changed_since_last_construct


def test_log_string_is_updated_after_append_and_calling_dunder_str():
    log = StructuredLog(['some_header', 'another_header'])
    log.append(some_header='some value', another_header='another value')
    original_log_string = log._log_string
    str(log)
    assert original_log_string != log._log_string


def test_dunder_string_becomes_log_string():
    log = StructuredLog(['some_header', 'another_header'])
    log.append(some_header='some value', another_header='another value')
    assert str(log) == log._log_string


def test_updated_is_false_after_append_and_dunder_string():
    log = StructuredLog(['some_header', 'another_header'])
    log.append(some_header='some value', another_header='another value')
    str(log)
    assert not log._changed_since_last_construct


def test_find_max_field_length():
    log = StructuredLog(
        ['some_header', 'another_header', 'a_very_wimpy_header_not_really']
    )
    log.append(some_header='some value', another_header='another value')
    log.append(
        some_header='some other value', another_header='another interesting value'
    )
    log.append(some_header='some strange value', another_header='another simple value')
    assert log._max_field_length() == {
        'some_header': 18,
        'another_header': 25,
        'a_very_wimpy_header_not_really': 30,
    }


def test_repr():
    log = StructuredLog('Name Age Occupation'.split())
    assert repr(log) == "StructuredLog(['Name', 'Age', 'Occupation'])"


def test_bool_matches_bool_rows():
    log = StructuredLog('Name Age Occupation'.split())
    assert not bool(log)
    log.append(Name='Alice', Age=28, Occupation='Student')
    assert bool(log)


def test_log_string_format():
    log = StructuredLog(['Name', 'Age', 'Occupation'])
    log.append(Name='Alice', Age=28, Occupation='Student')
    log.append(Name='Bob', Age=4, Occupation='Rocket Scientist')
    log.append(Name='Charles', Age=65, Occupation='Retired')
    assert (
        str(log)
        == 'Name    Age Occupation      \n'
        + 'Alice   28  Student         \n'
        + 'Bob     4   Rocket Scientist\n'
        + 'Charles 65  Retired         '
    )


def test_log_string_format_with_value_that_is_None():
    log = StructuredLog(['Name', 'Age', 'Occupation'])
    log.append(Name='Alice', Age=28, Occupation='Student')
    log.append(Name=None, Age=4, Occupation='Rocket Scientist')
    log.append(Name='Charles', Age=65, Occupation='Retired')
    assert (
        str(log)
        == 'Name    Age Occupation      \n'
        + 'Alice   28  Student         \n'
        + 'None    4   Rocket Scientist\n'
        + 'Charles 65  Retired         '
    )


def test_log_string_format_like_issue_9():
    log = StructuredLog('MACAddress IP Port Repeat'.split())
    log.append(
        MACAddress='-'.join(['AA'] * 6), IP='.'.join(['255'] * 4), Port=9, Repeat=3
    )
    log.append(
        MACAddress='-'.join(['BB'] * 6), IP='.'.join(['255'] * 4), Port=9, Repeat=3
    )
    log.append(
        MACAddress='-'.join(['CC'] * 6), IP='.'.join(['255'] * 4), Port=9, Repeat=3
    )
    log.append(
        MACAddress='-'.join(['DD'] * 6), IP='.'.join(['255'] * 4), Port=9, Repeat=3
    )
    log.append(
        MACAddress='-'.join(['EE'] * 6), IP='some.special.ip.address', Port=9, Repeat=3
    )
    assert (
        str(log)
        == 'MACAddress        IP                      Port Repeat\n'
        + 'AA-AA-AA-AA-AA-AA 255.255.255.255         9    3     \n'
        + 'BB-BB-BB-BB-BB-BB 255.255.255.255         9    3     \n'
        + 'CC-CC-CC-CC-CC-CC 255.255.255.255         9    3     \n'
        + 'DD-DD-DD-DD-DD-DD 255.255.255.255         9    3     \n'
        + 'EE-EE-EE-EE-EE-EE some.special.ip.address 9    3     '
    )
