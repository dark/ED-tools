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

import pandas as pd
import plotly.express as px
from logger import Logger
from typing import Tuple


class Systems:

    def __init__(self, json_data, *, logger: Logger):
        self._logger = logger

        # Normalize the JSON structure, but expanding the nested "coords"
        # object to a top-level object.
        self._logger.log("Normalizing data...")
        normalized_data = pd.json_normalize(json_data)
        # Only keep systems where the *main* star is a Neutron Star.
        self._logger.log("Initializing database...")
        self._all_systems = normalized_data.query("mainStar == 'Neutron Star'")
        # Select all systems by default
        self._selected_systems = self._all_systems
        self._logger.log("Database initialized")

    def display(self):
        """Display a heatmap with the currently selected systems."""
        self._logger.log("Creating heatmap...")
        # Harcoded number of X and Y bins to avoid rendering charts too large
        px.density_heatmap(
            self._selected_systems, x="coords.x", y="coords.z", nbinsx=1000, nbinsy=1000
        ).show()
        self._logger.log("Heatmap displayed in a new browser window")

    def save(self, filename: str):
        """Save a heatmap with the currently selected systemsto file."""
        self._logger.log("Saving heatmap to %s..." % filename)
        # Harcoded number of X and Y bins to avoid rendering charts too large
        px.density_heatmap(
            self._selected_systems, x="coords.x", y="coords.z", nbinsx=1000, nbinsy=1000
        ).write_html(filename)
        self._logger.log("Heatmap saved to %s" % filename)

    def zoom_out(self):
        """Zoom out to select all systems."""
        self._logger.log("Zooming out...")
        self._selected_systems = self._all_systems
        self._logger.log("Zoomed out")

    def zoom_in(self, coord_0: Tuple[int, int], coord_1: Tuple[int, int]):
        """Zoom in to select systems between the selected coordinates."""
        self._logger.log(
            "Zooming in to area between coordinates (%d,%d) and (%d,%d)..."
            % (
                coord_0[0],
                coord_0[1],
                coord_1[0],
                coord_1[1],
            )
        )
        min_x = min(coord_0[0], coord_1[0])
        max_x = max(coord_0[0], coord_1[0])
        min_z = min(coord_0[1], coord_1[1])
        max_z = max(coord_0[1], coord_1[1])
        self._selected_systems = (
            self._all_systems.query(f"`coords.x` > {min_x}")
            .query(f"`coords.x` < {max_x}")
            .query(f"`coords.z` > {min_z}")
            .query(f"`coords.z` < {max_z}")
        )
        self._logger.log("Zoom in complete")
