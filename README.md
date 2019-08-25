# WOL - Wake On LAN
**WOL** is a simple Python command line interface to the Wake On LAN protocol.
You can configure common use cases in the `wol_config.ini` file.

_Requires Python 3.6+_

## Usage 
**WOL** is designed to be used from the command line.
Without any optional setup, navigate to the directory which contains `wol.py` and just type `python3 wol.py <macaddress>` to send a magic packet to 255.255.255.255 port 9.
Optionally, you may specify the IP address, port, and SecureOn password with the `-i`, `-p`, and `-s` flags, respectively.

### Optional Setup
You may find it useful to have `wol` available as a system command.
To do so, copy `wol.py` and `wol_config.ini` to the `~/bin/` directory.
Change the shebang in the first line of `wol.py` to point to your Python 3.6+ interpreter.
Also, rename `wol.py` to `wol`.
Make `wol` executable by using `chmod u+x wol`.

You will find it useful to add aliases into the `wol_config.ini` file.
Directions to do so are given in the comments of that file.

Note that the `wol_config.ini` file is completely optional and the script will work without it present.

## Future Improvements
- Allow the `wol_config.ini` file to be in another directory (say, `~/.config/`).
- Allow input of multiple mac addresses with SecureOn passwords in the command line.
- Add an option to read multiple mac/ip/port/SecureOn from a file (like a `.csv`).
- Additionally, allow files to be aliased in the configuration file.

Have any more ideas?
Want to implement some ideas?
Feel free to contribute!
