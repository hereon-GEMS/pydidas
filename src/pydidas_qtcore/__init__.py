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
import sys
import sys as __sys


# Check for Qt6 flag and PySide6 availability and set the QT_API environment
# variable accordingly
_env_qt_version = __os.environ.get("QT_API", None)
__os.environ["FORCE_QT_API"] = "True"

if _env_qt_version is None and True in [arg.upper() == "--QT6" for arg in sys.argv]:
    try:
        import PySide6  # noqa F401
    except ImportError:
        print("PySide6 requested but not found. Falling back to PyQt5.")
    finally:
        __os.environ["QT_API"] = "pyside6" if "PySide6" in __sys.modules else "pyqt5"


import qtpy as __qtpy  # noqa E402


if "--verbose" in sys.argv:
    print("pydidas Using QT: ", __qtpy.API_NAME)


from . import pydidas_qapp  # noqa E402
from .fontsize import *  # noqa E402
from .pydidas_qapp import *  # noqa E402
from .pydidas_splash_screen import *  # noqa E402

__all__ = pydidas_qapp.__all__ + pydidas_splash_screen.__all__ + fontsize.__all__

# Start the custom PydidasQApplication to assure the correct QApplication is running:
__app = pydidas_qapp.PydidasQApplication(sys.argv)
