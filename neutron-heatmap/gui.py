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

import re
import time
import tkinter
from logger import Logger
from systems import Systems
from tkinter import ttk
from typing import List, Optional, Tuple


class GUI(Logger):

    def __init__(self):
        # This will be set when the main window is first displayed
        self._status_text = None

    # Implement the Logger interface.
    def log(self, s: str):
        msg = "%s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), s)
        print(msg)
        if self._status_text is not None:
            self._status_text.set(msg)

    def _handle_zoom_in(self, *args):
        try:
            coord0 = (int(self.x0.get()), int(self.z0.get()))
        except ValueError as e:
            self.log("Error parsing first coordinate: %s" % e)
            return
        try:
            coord1 = (int(self.x1.get()), int(self.z1.get()))
        except ValueError as e:
            self.log("Error parsing second coordinate: %s" % e)
            return

        self._systems.zoom_in(coord0, coord1)

    def _build_zoomin_data_frame(self, mainframe):
        zoomin_data_frame = ttk.Frame(mainframe, padding="1 1 1 1")
        ttk.Label(zoomin_data_frame, text="zoom in to (x=").grid(
            column=1, row=1, sticky=tkinter.W
        )
        self.x0 = tkinter.StringVar()
        x0_entry = ttk.Entry(zoomin_data_frame, width=7, textvariable=self.x0)
        x0_entry.grid(column=2, row=1, sticky=(tkinter.W, tkinter.E))
        ttk.Label(zoomin_data_frame, text=", z=").grid(
            column=3, row=1, sticky=tkinter.W
        )
        self.z0 = tkinter.StringVar()
        z0_entry = ttk.Entry(zoomin_data_frame, width=7, textvariable=self.z0)
        z0_entry.grid(column=4, row=1, sticky=(tkinter.W, tkinter.E))
        ttk.Label(zoomin_data_frame, text="), (x=").grid(
            column=5, row=1, sticky=tkinter.W
        )
        self.x1 = tkinter.StringVar()
        x1_entry = ttk.Entry(zoomin_data_frame, width=7, textvariable=self.x1)
        x1_entry.grid(column=6, row=1, sticky=(tkinter.W, tkinter.E))
        ttk.Label(zoomin_data_frame, text=", z=").grid(
            column=7, row=1, sticky=tkinter.W
        )
        self.z1 = tkinter.StringVar()
        z1_entry = ttk.Entry(zoomin_data_frame, width=7, textvariable=self.z1)
        z1_entry.grid(column=8, row=1, sticky=(tkinter.W, tkinter.E))
        ttk.Label(zoomin_data_frame, text=")").grid(column=9, row=1, sticky=tkinter.W)

        return zoomin_data_frame

    def request_loop(self, systems: Systems):
        self._systems = systems

        # Setup root (main application window)
        root = tkinter.Tk()
        root.title("Neutron Star heatmap plotter")

        # Setup main frame (covering the entire application window)
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(
            column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S)
        )
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Setup all actions
        # 1. Display
        ttk.Button(mainframe, text="Display", command=self._systems.display).grid(
            column=1, row=1, sticky=tkinter.E
        )
        ttk.Label(
            mainframe,
            text="open heatmap in a browser window using current zoom settings",
        ).grid(column=2, row=1, sticky=tkinter.W)
        # 2. Interstitial
        ttk.Label(
            mainframe, text="NOTE: Zoom in/out are effective at the next 'Display'"
        ).grid(column=1, row=2, columnspan=2, sticky=tkinter.W)
        # 3. Zoom In
        ttk.Button(mainframe, text="Zoom In", command=self._handle_zoom_in).grid(
            column=1, row=3, sticky=tkinter.E
        )
        zoomin_data_frame = self._build_zoomin_data_frame(mainframe)
        zoomin_data_frame.grid(
            column=2, row=3, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S)
        )
        # 4. Zoom Out
        ttk.Button(mainframe, text="Zoom Out", command=self._systems.zoom_out).grid(
            column=1, row=4, sticky=tkinter.E
        )
        ttk.Label(mainframe, text="zoom out to the initial state").grid(
            column=2, row=4, sticky=tkinter.W
        )

        # Add a homebrew status bar at the bottom
        self._status_text = tkinter.StringVar()
        ttk.Label(
            mainframe,
            textvariable=self._status_text,
            relief="sunken",
        ).grid(column=1, row=5, columnspan=2, sticky=(tkinter.W, tkinter.E))

        # Setup padding for all children of the mainframe
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.log("Main window ready")
        root.mainloop()
        self.log("Exiting...")
