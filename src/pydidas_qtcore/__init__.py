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
The core package defines base classes used throughout the full pydidas
suite.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os as __os
import sys as __sys

import qtpy

from . import pydidas_qapp
from .fontsize import *
from .pydidas_qapp import *
from .pydidas_splash_screen import *


if "--qt6" in __sys.argv:
    __os.environ["QT_API"] = "pyside6"
    __os.environ["FORCE_QT_API"] = "True"


if "--verbose-qt" in __sys.argv:
    print("pydidas Using QT: ", qtpy.API_NAME)

__all__ = pydidas_qapp.__all__ + pydidas_splash_screen.__all__ + fontsize.__all__
