#!/usr/bin/python3
#
#  Interactively display a Neutron Star heatmap for Elite:Dangerous
#  Copyright (C) 2024  Marco Leogrande
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import gzip
import json
import re
from systems import Systems
from typing import List, Optional, Tuple


def parse_json(input_file: str):
    print("Parsing input file %s..." % input_file)
    try:
        with gzip.open(input_file, "r") as fp:
            jdata = json.load(fp)
    except gzip.BadGzipFile:
        with open(input_file, "r") as fp:
            jdata = json.load(fp)

    print("Input file parsed correctly")
    return jdata


def print_cmd_help():
    print(
        """Available commands:
  ?                - print this help
  display          - open heatmap in a browser window
  zoom x1,z1 x2,z2 - zoom in to the provided coordinates (effective at the next `display`)
  zoom             - zoom out to the initial state (effective at the next `display`)
  exit             - exit the program"""
    )


def parse_coordinates(cmd: str) -> Optional[List[Tuple[int, int]]]:
    if len(cmd) <= 5 or cmd[0:5] != "zoom ":
        return None
    matches = re.fullmatch("(?i:zoom) ([-+0-9]*),([-+0-9]*) ([-+0-9]*),([-+0-9]*)", cmd)
    if matches is None:
        return None
    try:
        x_0 = int(matches[1])
        z_0 = int(matches[2])
        x_1 = int(matches[3])
        z_1 = int(matches[4])
    except:
        return None
    return [(x_0, z_0), (x_1, z_1)]


def request_loop(systems: Systems):
    print("")
    print("Input your commands at the prompt, '?' for help")
    while True:
        try:
            cmd = input("> ").lower()
        except KeyboardInterrupt:
            # Ctrl+C
            break
        except EOFError:
            # Ctrl+D
            break

        if cmd == "?" or cmd == "h" or cmd == "help":
            print_cmd_help()
        elif cmd == "display":
            systems.display()
        elif cmd == "zoom":
            # Exact match on the 'zoom' command
            systems.zoom_out()
        elif cmd[0:4] == "zoom":
            coordinates = parse_coordinates(cmd)
            if coordinates is None:
                print_cmd_help()
            else:
                systems.zoom_in(coordinates[0], coordinates[1])
        elif cmd == "exit":
            break
        else:
            # Unrecognized command
            print_cmd_help()

    print("Exiting...")


def main(input_file: str):
    jdata = parse_json(input_file)
    # Import systems data in the database
    systems = Systems(jdata)
    # Handle the interactive request loop
    request_loop(systems)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Interactively display a Neutron Star heatmap for Elite:Dangerous"
    )
    parser.add_argument(
        "input",
        type=str,
        help="input JSON file (.gz compressed or not) from https://spansh.co.uk/dumps",
    )
    args = parser.parse_args()
    main(args.input)
