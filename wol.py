#!/usr/bin/python3

import argparse
import configparser
import os
import re
import socket


MAC_REGEX = re.compile('^([0-9a-fA-F]{2}[-:.]?){5}[0-9a-fA-F]{2}$')
DEFAULT_IP = '255.255.255.255'
DEFAULT_PORT = 9
# requires that the wol_config file be in the same directory as this file
CONFIG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'wol_config')


def main():
    argparser = argparse.ArgumentParser(
        description='Wake computers using the Wake-On-Lan protocol.'
    )
    argparser.add_argument(
        'mac',
        metavar='mac address',
        help='The mac address of the computer you wish to wake.'
    )
    argparser.add_argument(
        '-i',
        metavar='ip',
        help='The IP address to send the magic packet to '
        f'(default {DEFAULT_IP}).'
    )
    argparser.add_argument(
        '-p',
        metavar='port',
        type=int,
        help='The port to send the magic packet to '
        f'(default {DEFAULT_PORT}).'
    )
    argparser.add_argument(
        '-s',
        metavar='secureon',
        help='The SecureOn password for the computer you wish to wake '
        '(default None).'
    )
    args = argparser.parse_args()

    mac = args.mac
    ip = args.i
    port = args.p
    secureon = args.s

    config = configparser.ConfigParser()
    # reading a file that is not present does not raise an error, so the
    # the script can be ran without having to consider the case in which
    # the config file is not present
    config.read(CONFIG_FILE)

    if mac in config.sections():
        # user has used an alias
        alias = mac
        try:
            # someone's config file is bound to be messed up...
            mac = config.get(mac, 'mac')
        except configparser.NoOptionError:
            print(f'No mac address associated with {alias}.')
            quit(1)

        # prioritizes command line arguments over config entries (!!!)
        # reverts to defaults if config file is unavailable or
        # formatted incorrectly
        if not ip:
            ip = config.get(alias, 'ip', fallback=DEFAULT_IP)
        if not port:
            port = config.getint(alias, 'port', fallback=DEFAULT_PORT)
        if not secureon:
            secureon = config.get(alias, 'secureon', fallback=None)
    else:
        # user did not use an alias
        # revert to defaults since options were not specified
        # prefer defaults defined in config file over preset defaults
        if not ip:
            ip = config.get('DEFAULT', 'ip', fallback=DEFAULT_IP)
        if not port:
            port = config.getint('DEFAULT', 'port', fallback=DEFAULT_PORT)
        if not secureon:
            secureon = config.get('DEFAULT', 'secureon', fallback=None)

    # display any errors in easy-to-read format
    try:
        wake(mac, ip, port, secureon)
    except ValueError as e:
        print(e.args[0])
    else:
        # no errors occurred
        print('Magic Packet sent!'
              f'\n\t     Mac: {mac}'
              f'\n\t      IP: {ip}'
              f'\n\t    Port: {port}'
              f'\n\tSecureOn: {secureon}\n')


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
