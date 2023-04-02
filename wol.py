#!/usr/bin/python3
"""
Wake computers using the Wake-On-LAN protocol with configuration options.

See the README for configuration details.
"""
import argparse
import itertools
import json
import os
import re
import socket
from collections import ChainMap, namedtuple
from pathlib import Path


__version__ = "0.2.2"


class StructuredLog:
    """
    A table-like data structure for visual logging of magic packets sent.
    """

    _BLANK = None

    def __init__(self, headers):
        self._headers = tuple(headers)
        self._rows = []
        self._log_string = " ".join(self._headers)
        self._changed_since_last_construct = False
        self.LogRow = namedtuple("LogRow", self._headers)

    @property
    def headers(self):
        return self._headers

    def append(self, **fields):
        """
        Appends a record to the log using StructuredLog._BLANK as the
        placeholder for values not given.
        """
        header_defaults = dict.fromkeys(self._headers, StructuredLog._BLANK)
        self._rows.append(self.LogRow(**ChainMap(fields, header_defaults)))
        self._changed_since_last_construct = True

    def _max_field_length(self):
        """
        Utility method to find the length of the longest value under each
        header.
        """
        return {
            header: max(
                len(header),
                max(
                    map(len, (str(getattr(row, header)) for row in self._rows)),
                    default=0,
                ),
            )
            for header in self._headers
        }

    def _construct_log_string(self):
        """
        Utility method to construct the self._log_string (structured table).
        This is called from the __str__ method only when there have been
        changes (appends) since the last run of this method.
        """
        max_field_length = self._max_field_length()

        # Create the format string "{:<N}" for every field where N is the max
        # field length for that header.
        cell = {
            header: "{{:<{}}}".format(length)
            for header, length in max_field_length.items()
        }

        header_row = " ".join(
            [cell[header].format(str(header)) for header in self._headers]
        )
        rows = [
            " ".join(
                [
                    cell[header].format(str(getattr(row, header)))
                    for header in self._headers
                ]
            )
            for row in self._rows
        ]
        row_string = "\n".join(rows)
        self._log_string = "{}\n{}".format(header_row, row_string)
        self._changed_since_last_construct = False

    def __str__(self):
        if self._changed_since_last_construct:
            self._construct_log_string()
        return self._log_string

    def __repr__(self):
        return f"{type(self).__name__}({list(self._headers)!r})"

    def __bool__(self):
        return bool(self._rows)


class WOLConfig:

    DEFAULTS = {
        "ip": "255.255.255.255",
        "port": 9,
        "interface": None,
        "repeat": 0,
    }

    def __init__(self, config_file, **cli_kwargs):
        self._config_file = config_file
        self._user_config = self._init_dict()

        # prefer configuration options in this order:
        # cli > alias config > default config > class defaults
        self._default_config = self.DEFAULTS.copy()
        self._default_config.update(self._user_config.get("DEFAULT", self.DEFAULTS))
        self._cli_arguments = cli_kwargs

    def _init_dict(self):
        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            return {}

    def _process_alias(self, alias, seen=None, groups=None):
        """
        Yields dictionaries of parameters for each alias and sub-alias.
        """
        if groups is None:
            # keep a unique stack/queue of sub-aliases that need to be called
            groups = set()
        if seen is None:
            # keep track of alias we see to avoid any infinite loops
            seen = set()
        seen.add(alias)
        alias_config = self._user_config.get(alias, alias)

        try:
            groups.update(set(alias_config.pop("groups")))
        except (KeyError, AttributeError):
            pass

        try:
            macs = alias_config.pop("macs")
        except (KeyError, AttributeError):
            macs = []

        if isinstance(alias_config, str):  # assume alias_config is mac address
            config = self._default_config.copy()
            config.update(self._cli_arguments)
            yield {"macs": [alias_config], **config}
            return

        # alias_config is a dictionary
        config = self._default_config.copy()
        config.update(alias_config)
        config.update(self._cli_arguments)
        if macs:
            yield {"macs": macs, **config}
        for group in groups - seen:
            yield from self._process_alias(group, seen=seen, groups=groups)

    def get_config(self, *aliases):
        """
        Yields dictionaries of parameters to call the wake() function with.
        Minimizes the number of calls by grouping the calls by parameters.
        """
        calls = []
        for alias in aliases:
            calls.extend(list(self._process_alias(alias)))

        def call_params(call_dict):
            return tuple(v for k, v in call_dict.items() if k != "macs")

        calls.sort(key=call_params)

        for _, group in itertools.groupby(calls, key=call_params):
            group_macs = []
            for call in group:
                group_macs.extend(call.pop("macs"))
            yield {"macs": group_macs, **call}  # pretty hack-y using call here


def wake(*macs, ip="255.255.255.255", port=9, repeat=0, interface=None):
    """
    Sends a magic packet for the corresponding MAC addresses and SecureOn
    passwords. Add a SecureOn password to a MAC address by appending the
    SecureOn password after the MAC address with a slash.

    For example, to wake a computer with MAC address 12-34-56-AB-CD-EF and
    SecureOn password 11-11-11-11-11-11, call
    wake('12-34-56-AB-CD-EF/11-11-11-11-11-11')

    If your machine has multiple NICs, you can use the interface keyword to
    specify which NIC to use to send magic packets.

    Since the Wake-on-LAN protocol uses UDP, it may be advisable to repeat
    the sending of magic packets. This can be done by adjusting the repeat
    keyword argument.
    """
    magic_packets = [make_magic(*mac.split("/")) for mac in macs]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        if interface is not None:
            sock.bind((interface, 0))
        # allow UDP socket to broadcast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for magic_packet in magic_packets:
            for _ in range(repeat + 1):
                sock.sendto(magic_packet, (ip, port))


def make_magic(mac, secureon=None):
    """
    Returns a magic packet for the given mac address and SecureOn password.
    """
    mac = clean_mac(mac)

    if secureon is not None:
        # SecureOn passwords are formatted the same way as mac addresses
        # so they can be 'cleaned' the same way
        secureon = clean_mac(secureon)
        return bytes.fromhex("F" * 12 + mac * 16 + secureon)
    else:
        return bytes.fromhex("F" * 12 + mac * 16)


def clean_mac(mac):
    """
    Removes punctuation from a mac address. The input mac address need
    not be formatted 'neatly'.

    Example:
         >>> clean_mac('7824-aF:3B-55.E3')
         '7824AF3B55E3'
    """
    try:
        match = re.match(r"^([0-9a-fA-F]{2}[-:.]?){5}[0-9a-fA-F]{2}$", mac)
    except TypeError:
        match = False
    finally:
        if not match:
            raise ValueError(f"Invalid MAC address or SecureOn password: {mac}")

    return "".join(char for char in mac if char.isalnum()).upper()


if __name__ == "__main__":
    config_fp = (
        Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser().absolute()
        / "wol"
        / "wol.json"
    )

    argparser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Contribute at https://github.com/davidpratt512/wol.",
    )
    argparser.add_argument(
        "macs",
        nargs="+",
        metavar="MAC/SecureOn",
        help="The mac addresses or groups of the computers you wish to wake. "
        "To add a SecureOn password, enter the mac address and SecureOn "
        'password separated by a "/": <MAC>/<SecureOn>. To define groups,'
        f" create/edit the configuration file at {config_fp}.",
    )
    argparser.add_argument(
        "-i",
        "--ip",
        metavar="ip",
        help="The IP address to send the magic packets to "
        f'(default {WOLConfig.DEFAULTS.get("ip")}).',
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="port",
        type=int,
        help="The port to send the magic packets to "
        f'(default {WOLConfig.DEFAULTS.get("port")}).',
    )
    argparser.add_argument(
        "-r",
        "--repeat",
        metavar="repeat",
        type=int,
        help="How many additional times to send each magic packet "
        f'(default {WOLConfig.DEFAULTS.get("repeat")}).',
    )
    argparser.add_argument(
        "-n",
        "--interface",
        metavar="interface",
        help="The interface to send magic packets from. Useful if there are "
        "multiple NICs on your machine (default "
        f'{WOLConfig.DEFAULTS.get("interface")}).',
    )
    argparser.add_argument(
        "-f",
        "--config-file",
        metavar="file",
        help="The .json file to read configuration options from (default "
        f"{config_fp}).",
    )
    argparser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Run quietly, do not print out result of program unless an error "
        "occurred (default false).",
    )
    parsed_args = vars(argparser.parse_args())

    config_fp = Path(parsed_args.pop("config_file") or config_fp)
    quiet = parsed_args.pop("quiet")
    macs_and_aliases = parsed_args.pop("macs")

    # get rid of cli arguments from parsed args that were not specified by user
    arguments = ["ip", "port", "repeat", "interface"]
    args = {arg: parsed_args.get(arg) for arg in arguments if parsed_args.get(arg)}

    log = StructuredLog(["MAC", "IP", "Port", "Repeat", "Interface"])
    wol_config = WOLConfig(config_fp, **args)
    for wake_call in wol_config.get_config(*macs_and_aliases):
        mac_addresses = wake_call.pop("macs")
        try:
            wake(*mac_addresses, **wake_call)
        except ValueError as e:
            print(e.args[0])
        else:
            for mac in mac_addresses:
                log.append(
                    MAC=mac,
                    IP=wake_call.get("ip"),
                    Port=wake_call.get("port"),
                    Interface=wake_call.get("interface"),
                    Repeat=wake_call.get("repeat"),
                )
    if log and not quiet:
        print(log)
