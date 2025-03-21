# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The colors module holds color names and RGB codes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "COLOR_ORANGE",
    "COLOR_BLUE",
    "COLOR_RED",
    "COLOR_GREEN",
    "COLOR_PURPLE",
    "COLOR_CYAN",
    "COLOR_GRAY",
    "COLOR_HEREON_RED",
    "COLOR_HEREON_BLUE",
    "COLOR_HEREON_TURQUOISE",
    "PYDIDAS_COLORS",
]


COLOR_ORANGE = "#FFA500"

# Blue orchid:
COLOR_BLUE = "#1F45FC"

# Chilli pepper
COLOR_RED = "#C11B17"

# Green apple
COLOR_GREEN = "#4CC417"

# Indigo
COLOR_PURPLE = "#4B0082"

# Turqoise
COLOR_CYAN = "#40E0D0"

# Vampire Gray
COLOR_GRAY = "#565051"


COLOR_HEREON_RED = "#E60046"
COLOR_HEREON_BLUE = "#00AAE6"
COLOR_HEREON_TURQUOISE = "#0091A0"

PYDIDAS_COLORS = {
    "orange": COLOR_ORANGE,
    "blue": COLOR_BLUE,
    "red": COLOR_RED,
    "green": COLOR_GREEN,
    "purple": COLOR_PURPLE,
    "cyan": COLOR_CYAN,
    "gray": COLOR_GRAY,
    "black": "#000000",
    "white": "#FFFFFF",
}
