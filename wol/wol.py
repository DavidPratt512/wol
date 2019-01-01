import argparse
import configparser
import re
import socket


# TODO consider adding support for SecureOn Passwords
MAC_REGEX = re.compile('^([0-9a-fA-F]{2}[-:.]?){5}[0-9a-fA-F]{2}$')


def main():
    pass


def send_magic(magic):
    pass


def make_magic(mac, secureon=None):
    """
    Creates a magic packet for the given mac address and SecureOn
    password.

    """
    if not MAC_REGEX.match(mac):
        raise ValueError(f'Invalid mac address: {mac}')

    # remove any punctuation from the mac address
    mac = clean_mac(mac)

    # all magic packets begin with the synchronization stream ('f' * 12)
    # followed by 16 repetitions of the mac address
    # then convert to an encoded bytes object
    return bytes.fromhex('f'*12 + mac*16)


def clean_mac(mac):
    """
    Removes punctuation from a mac address.
    78-24-AF:3B-55.E3 -> 7824AF3B55E3
    """
    return ''.join(char for char in mac if char.isalnum())


if __name__ == '__main__':
    main()
