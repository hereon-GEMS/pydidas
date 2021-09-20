# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with pydidas custom Exceptions which are used throughout the package.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['FrameConfigError', 'WidgetLayoutError', 'AppConfigError']

import numpy as np

class FrameConfigError(Exception):
    """
    FrameConfigError is used if any required Qt references are missing or
    any other specific issues are raised in the configuration of Frames.
    """
    ...

class WidgetLayoutError(Exception):
    """
    WidgetLayoutError is used if a widget attempts to add items to a layout
    without having a layout.
    """

class AppConfigError(Exception):
    """
    AppConfigError is used when app Parameters are not consistent and cannot
    be processed.
    """
