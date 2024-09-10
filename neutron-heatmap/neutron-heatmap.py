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
import pandas as pd
import plotly.express as px


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


def request_loop(all_systems):
    # Select all systems by default
    selected_systems = all_systems

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
            px.density_heatmap(
                selected_systems, x="coords.x", y="coords.z", nbinsx=1000, nbinsy=1000
            ).show()
        elif cmd[0:4] == "zoom":
            # norm = norm.query("`coords.x` > -1111").query("`coords.x` < 8980").query("`coords.z` > 57338").query("`coords.z` < 65269")
            print("zoom")
        elif cmd == "exit":
            break
        else:
            # Unrecognized command
            print_cmd_help()

    print("Exiting...")


def main(input_file: str):
    jdata = parse_json(input_file)
    # Normalize the JSON structure, but expanding the nested "coords"
    # object to a top-level object.
    print("Normalizing data...")
    normalized_data = pd.json_normalize(jdata)
    # Only keep systems where the *main* star is a Neutron Star.
    print("Initializing database...")
    all_systems = normalized_data.query("mainStar == 'Neutron Star'")
    # Handle the interactive request loop
    request_loop(all_systems)


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
