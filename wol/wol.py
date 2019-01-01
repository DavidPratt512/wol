import argparse
import configparser
import re
import socket


MAC_REGEX = re.compile('^([0-9a-fA-F]{2}[-:.]?){5}[0-9a-fA-F]{2}$')


def main():
    pass


def wake(mac, ip='255.255.255.255', port=9, secureon=None):
    """
    Sends a magic packet for the corresponding mac address and SecureOn
    password.

    """
    magic_packet = make_magic(mac, secureon)
    # create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # and allow it to broadcast
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.connect((ip, port))
    sock.send(magic_packet)
    sock.close()


def make_magic(mac, secureon=None):
    """
    Creates a magic packet for the given mac address and SecureOn
    password.

    """
    if not MAC_REGEX.match(mac):
        raise ValueError(f'Invalid mac address: {mac}')

    # remove any punctuation from the mac address
    mac = clean_mac(mac)

    if secureon:
        # SecureOn passwords are formatted the same way as mac addresses
        # so they can be 'cleaned' the same way
        if not MAC_REGEX.match(secureon):
            raise ValueError(f'Invalid SecureOn password: {secureon}')

        secureon = clean_mac(secureon)
        return bytes.fromhex('f'*12 + mac*16 + secureon)
    else:
        return bytes.fromhex('f'*12 + mac*16)


def clean_mac(mac):
    """
    Removes punctuation from a mac address. The input mac address need
    not be formatted 'neatly'.

    Example: 7824-AF:3B-55.E3 -> 7824AF3B55E3

    """
    return ''.join(char for char in mac if char.isalnum())


if __name__ == '__main__':
    main()
