# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with silx actions to extend the functionality of the generic silx plotting
widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


import numpy as np
from silx.gui import colors


# if "wheel" not in colors._DEFAULT_PREFERRED_COLORMAPS:
#     colors._DEFAULT_PREFERRED_COLORMAPS = colors.preferredColormaps() +("wheel",)


_LUT = np.zeros((256, 4))
_LUT[:, 3] = 255
# set up the red part of the LUT:
_LUT[:42, 0] = 255
_LUT[42:85, 0] = np.linspace(255, 0, 43)
_LUT[85:127, 0] = 0
_LUT[127:170, 0] = 0
_LUT[170:213, 0] = np.linspace(0, 255, 43)
_LUT[213:256, 0] = 255

# green part:
_LUT[:42, 1] = np.linspace(0, 255, 42)
_LUT[42:85, 1] = 255
_LUT[85:127, 1] = 255
_LUT[127:170, 1] = np.linspace(255, 0, 43)
_LUT[170:213, 1] = 0
_LUT[213:256, 1] = 0

# blue part:
_LUT[:42, 2] = 0
_LUT[42:85, 2] = 0
_LUT[85:127, 2] = np.linspace(0, 255, 42)
_LUT[127:170, 2] = 255
_LUT[170:213, 2] = 255
_LUT[213:256, 2] = np.linspace(255, 0, 43)

colors.registerLUT("wheel", _LUT.astype(np.uint8))
WHEEL = colors.Colormap(name="wheel", vmin=0, vmax=np.pi)
WHEEL.setNaNColor([128, 128, 128, 255])
