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

import time
from logger import Logger
from typing import List, Optional, Tuple


def _print_cmd_help():
    print(
        """Available commands:
  ?                - print this help
  display          - open heatmap in a browser window
  zoom x1,z1 x2,z2 - zoom in to the provided coordinates (effective at the next `display`)
  zoom             - zoom out to the initial state (effective at the next `display`)
  exit             - exit the program"""
    )


class Console(Logger):

    # Implement the Logger interface.
    def log(self, s: str):
        print("%s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), s))

    def request_loop(self, *, init_fn):
        # Wait for the system to init before proceeding further
        systems = init_fn()

        print("")
        print("Input your commands at the prompt, '?' for help")
        while True:
            try:
                cmd_tokens = input("> ").lower().split()
            except KeyboardInterrupt:
                # Ctrl+C
                break
            except EOFError:
                # Ctrl+D
                break

            if len(cmd_tokens) == 0:
                # Empty command
                _print_cmd_help()
                continue

            cmd = cmd_tokens[0]
            if cmd == "?" or cmd == "h" or cmd == "help":
                _print_cmd_help()
            elif cmd == "display":
                systems.display()
            elif cmd == "zoom":
                if len(cmd_tokens) == 1:
                    # Exact match on the 'zoom' command: zoom out
                    systems.zoom_out()
                elif len(cmd_tokens) == 3:
                    # 'zoom' command + 2 parameters: this is a zoom in
                    coordinates = self._parse_coordinates(cmd_tokens[1:])
                    if coordinates is None:
                        _print_cmd_help()
                    else:
                        systems.zoom_in(coordinates[0], coordinates[1])
                else:
                    # Wrong number of parameters
                    _print_cmd_help()
            elif cmd == "exit":
                break
            else:
                # Unrecognized command
                _print_cmd_help()

        print("Exiting...")

    def _parse_coordinates(
        self, cmd_parameters: List[str]
    ) -> Optional[List[Tuple[int, int]]]:
        if len(cmd_parameters) != 2:
            return None

        first = cmd_parameters[0].split(",")
        if len(first) != 2:
            self.log("First coordinate in bad format: %s" % cmd_parameters[0])
            return None
        second = cmd_parameters[1].split(",")
        if len(second) != 2:
            self.log("Second coordinate in bad format: %s" % cmd_parameters[1])
            return None

        try:
            x_0 = int(first[0])
            z_0 = int(first[1])
            x_1 = int(second[0])
            z_1 = int(second[1])
        except Exception as e:
            self.log("Parse error: %s" % e)
            return None
        return [(x_0, z_0), (x_1, z_1)]
