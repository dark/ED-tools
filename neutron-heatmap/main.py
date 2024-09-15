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
from console import Console
from gui import GUI
from logger import Logger
from systems import Systems


def parse_json(input_file: str, logger: Logger):
    logger.log("Parsing input file %s..." % input_file)
    try:
        with gzip.open(input_file, "r") as fp:
            jdata = json.load(fp)
    except gzip.BadGzipFile:
        with open(input_file, "r") as fp:
            jdata = json.load(fp)

    logger.log("Input file parsed correctly")
    return jdata


def choose_control(control: str):
    if control == "console":
        return Console()
    if control == "gui":
        return GUI()
    raise ValueError('Application bug: unexpected control: %s' % control)

def main(input_file: str, control: str):
    # Initialize environment.
    control = choose_control(control)

    jdata = parse_json(input_file, control)
    # Import systems data in the database
    systems = Systems(jdata, logger=control)
    # Handle the interactive request loop
    control.request_loop(systems)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Interactively display a Neutron Star heatmap for Elite:Dangerous"
    )
    parser.add_argument(
        "input",
        type=str,
        help="input JSON file (.gz compressed or not) from https://spansh.co.uk/dumps",
    )
    parser.add_argument(
        "--control",
        type=str,
        choices=['console', 'gui'],
        default='console',
        help="preferred method to control the inputs",
    )
    args = parser.parse_args()
    main(args.input, args.control)
