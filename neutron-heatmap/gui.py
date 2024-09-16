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

import functools
import re
import threading
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
        # Separate thread where long-operations are offloaded to
        self._longop_thread = None

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

    def _progressbar_start(self):
        if self._progressbar is None:
            self._progressbar = ttk.Progressbar(
                self._mainframe,
                orient=tkinter.HORIZONTAL,
                mode="indeterminate",
                maximum=40,
            )
        self._progressbar.grid(
            column=1, row=5, columnspan=2, sticky=(tkinter.W, tkinter.E)
        )
        self._progressbar.start()

    def _progressbar_stop(self):
        self._progressbar.stop()
        self._progressbar.grid_remove()

    def _long_op_pre(self):
        """Prepare for a long op"""
        # Disable all buttons
        for child in self._mainframe.winfo_children():
            if isinstance(child, ttk.Button):
                child["state"] = tkinter.DISABLED
        # Display and start the progress bar
        self._progressbar_start()

    def _long_op_post(self, event):
        """Recover from a long op."""
        # Join the background thread
        if self._longop_thread is None:
            raise RuntimeError("BUG: long op thread should not be None")
        self._longop_thread.join()
        self._longop_thread = None
        # Restore all buttons
        for child in self._mainframe.winfo_children():
            if isinstance(child, ttk.Button):
                child["state"] = tkinter.NORMAL
        # Stop and hide the progress bar
        self._progressbar_stop()

    def _handle_long_op(self, fn):
        # Prepare for a long op
        self._long_op_pre()

        # In a separate thread, call the long op and generate an event when it's done
        def _worker():
            fn()
            self._mainframe.event_generate("<<LongOpComplete>>", when="head")

        # Sanity check
        if self._longop_thread is not None:
            raise RuntimeError("BUG: long op thread should be None")
        self._longop_thread = threading.Thread(target=_worker)
        self._longop_thread.start()

    def request_loop(self, systems: Systems):
        self._systems = systems

        # Setup root (main application window)
        root = tkinter.Tk()
        root.title("Neutron Star heatmap plotter")

        # Setup main frame (covering the entire application window)
        self._mainframe = ttk.Frame(root, padding="3 3 12 12")
        self._mainframe.grid(
            column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S)
        )
        self._mainframe.bind("<<LongOpComplete>>", self._long_op_post)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Setup all actions
        #
        # The first column will include buttons, while the second will
        # have labels; to preserve the layout when the window is
        # stretched (e.g. when the status bar has a very long text),
        # ensure that the first column never resizes, while the second
        # one always will.
        self._mainframe.columnconfigure(1, weight=0)
        self._mainframe.columnconfigure(2, weight=1)
        # 1. Display
        ttk.Button(
            self._mainframe,
            text="Display",
            command=functools.partial(self._handle_long_op, self._systems.display),
        ).grid(column=1, row=1, sticky=tkinter.E)
        ttk.Label(
            self._mainframe,
            text="open heatmap in a browser window using current zoom settings",
        ).grid(column=2, row=1, sticky=tkinter.W)
        # 2. Interstitial
        ttk.Label(
            self._mainframe,
            text="NOTE: Zoom in/out are effective at the next 'Display'",
        ).grid(column=1, row=2, columnspan=2, sticky=tkinter.W)
        # 3. Zoom In
        ttk.Button(
            self._mainframe,
            text="Zoom In",
            command=functools.partial(self._handle_long_op, self._handle_zoom_in),
        ).grid(column=1, row=3, sticky=tkinter.E)
        zoomin_data_frame = self._build_zoomin_data_frame(self._mainframe)
        zoomin_data_frame.grid(
            column=2, row=3, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S)
        )
        # 4. Zoom Out
        ttk.Button(
            self._mainframe, text="Zoom Out", command=self._systems.zoom_out
        ).grid(column=1, row=4, sticky=tkinter.E)
        ttk.Label(self._mainframe, text="zoom out to the initial state").grid(
            column=2, row=4, sticky=tkinter.W
        )

        # Add a progress bar for long operations; this will be created on-demand
        self._progressbar = None

        # Add a homebrew status bar at the bottom
        self._status_text = tkinter.StringVar()
        ttk.Label(
            self._mainframe,
            textvariable=self._status_text,
            relief="sunken",
        ).grid(column=1, row=6, columnspan=2, sticky=(tkinter.W, tkinter.E))

        # Setup padding for all children of the mainframe
        for child in self._mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.log("Main window ready")
        root.mainloop()
        self.log("Exiting...")
        # Wait for the background thread, if it is still running
        if self._longop_thread is not None:
            self._longop_thread.join()
            self._longop_thread = None
        self.log("Exited")
