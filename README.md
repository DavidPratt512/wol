# WOL - Wake On LAN
**WOL** is a simple Python command line interface to the Wake On LAN protocol.
Default behavior can be changed and common use cases can be configured in a `.json` file.

_Requires Python 3.7+_

## Usage 
**WOL** is designed to be used from the command line.
Without any additional setup, use `python3 wol.py 12:34:56:78:90:12` to send a magic packet for the MAC address 
`12:34:56:78:90:12` to `255.255.255.255` port 9.

The full signature is
```
wol.py [-h] [-i ip] [-p port] [-r repeat] [-n interface] [-f file] [-q]
       MAC/SecureOn [MAC/SecureOn ...]
```
Computers requiring a SecureOn password can be woken by separating the MAC address and SecureOn password with a 
`/`.
For example, to wake a computer with MAC address `12:34:56:78:90:12` and SecureOn password `AB:CD:EF:12:34:56`, use
`python3 wol.py 12:34:56:78:90:12/AB:CD:EF:12:34:56`.

Note that MAC addresses and SecureOn passwords do not require the `:` separator and are case insensitive.
Valid separators are `:`, `-`, `.`, or no separator.

## Configuration Setup
Optionally, users may create a `.json` file to save common use cases and change default behavior.

By default, `wol.py` will look in `~/.config/` on a Unix like machine or `%userprofile%/.config/` on Windows for `wol.json`.
Users may specify the `-f` flag to point to another `.json` file instead.

The `.json` file is meant to contain _groups_ of MAC addresses with corresponding IP addresses, ports, repeat counts,
interfaces, and other groups.

For example, to change the default behavior of `wol.py`, create `wol.json` in the directory specified above with a 
`DEFAULT` group:
```json
{
  "DEFAULT": {
    "ip": "10.0.1.10",
    "port": 2718,
    "repeat": 2
  }
}
```
With the above configuration, `python3 wol.py 123456789012` will send 2 magic packets to `10.0.1.10` port 2718.

Users may find it useful to create other groups:
```json
{
  "all": {
    "groups": [
      "home",
      "work"
    ]
  },
  
  "home": {
    "ip": "home_ip",
    "port": 3141,
    "macs": [
      "123456789012",
      "123ABCDEF987"
    ]
  },
  
  "work": {
    "ip": "work_ip",
    "port": 2718,
    "macs": [
      "556677889900"
    ]
  }
}
```
With the above configuration, `python3 wol.py all` will send magic packets for MAC addresses `123456789012` and 
`123ABCDEF987` to `home_ip` port 3141 as well as the magic packet for MAC address `556677889900` to `work_ip` port 2718.

Additionally an `"interface"` can be defined for any group.
This option is useful if a users machine has multiple NICs.