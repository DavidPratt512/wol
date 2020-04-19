#!/usr/bin/python3

import argparse
import json
import os
import re
import socket


MAC_REGEX = re.compile('^([0-9a-fA-F]{2}[-:.]?){5}[0-9a-fA-F]{2}$')
DEFAULT_IP = '255.255.255.255'
DEFAULT_PORT = 9
# requires that the wol_config.ini file be in the same directory as this file
CONFIG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'wol_config.ini')  # todo, change this to a json file and put it in ~/.config/wol.json


def wake(*macs, ip='255.255.255.255', port=9, repeat=1):
    """
    Sends a magic packet for the corresponding MAC addresses and SecureOn
    passwords. Add a SecureOn password to a MAC address by appending the
    SecureOn password after the MAC address with a slash.

    For example, to wake a computer with MAC address 12-34-56-AB-CD-EF and
    SecureOn password 11-11-11-11-11-11, call
    wake('12-34-56-AB-CD-EF/11-11-11-11-11-11')

    Since the Wake-on-LAN protocol uses UDP, it may be advisable to repeat
    the sending of magic packets. This can be done by adjusting the repeat
    keyword argument.
    """
    magic_packets = [make_magic(*mac.split('/')) for mac in macs]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # allow UDP socket to broadcast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for magic_packet in magic_packets:
            for _ in range(repeat):
                sock.sendto(magic_packet, (ip, port))
                # todo: consider adding sleep here


def make_magic(mac, secureon=None):
    """
    Creates a magic packet for the given mac address and SecureOn
    password.
    """
    mac = clean_mac(mac)

    if secureon is not None:
        # SecureOn passwords are formatted the same way as mac addresses
        # so they can be 'cleaned' the same way
        if not MAC_REGEX.match(secureon):
            raise ValueError(f'Invalid SecureOn password: {secureon}')

        secureon = clean_mac(secureon)
        return bytes.fromhex('F'*12 + mac*16 + secureon)
    else:
        return bytes.fromhex('F'*12 + mac*16)


def clean_mac(mac):
    """
    Removes punctuation from a mac address. The input mac address need
    not be formatted 'neatly'.

    Example:
         >>> clean_mac('7824-AF:3B-55.E3')
         '7824AF3B55E3'
    """
    if not MAC_REGEX.match(mac):
        raise ValueError(f'Invalid MAC address or SecureOn password: {mac}')

    return ''.join(char for char in mac if char.isalnum()).upper()


def main():
    argparser = argparse.ArgumentParser(
        description='Wake computers using the Wake-On-Lan protocol.'
    )
    argparser.add_argument(
        'macs',
        nargs='*',
        metavar='MAC/SecureOn',
        help='The mac addresses of the computers you wish to wake. To add a SecureOn password, enter the mac address and SecureOn password separated by a "/": <MAC>/<SecureOn>.'
    )
    argparser.add_argument(
        '-i',
        metavar='IP',
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
    args = argparser.parse_args()





if __name__ == '__main__':
    main()
