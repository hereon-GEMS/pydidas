# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
The pydidas_qtcore package provides Qt-related utilities for pydidas.

This module initializes the Qt bindings (PyQt5 or PySide6) and provides
the PydidasQApplication, PydidasSplashScreen, and font size constants.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os as __os
import sys as __sys
import warnings as __warnings


# Check for Qt6 flag and PySide6 availability and set the QT_API
# environment variable accordingly
ENV_QT_VERSION = __os.environ.get("QT_API", None)
QT5_FLAG = "--QT5" in [arg.upper() for arg in __sys.argv]
__os.environ["FORCE_QT_API"] = "True"


if QT5_FLAG or ENV_QT_VERSION == "pyqt5":
    try:
        import PyQt5
    except ImportError:
        __warnings.warn("PyQt5 requested but not found. Falling back to PySide6.")
    finally:
        _qt_api = "pyqt5" if "PyQt5" in __sys.modules else "pyside6"
        __os.environ["QT_API"] = _qt_api
else:
    if ENV_QT_VERSION is None:
        __os.environ["QT_API"] = "pyside6"

import qtpy as __qtpy  # noqa E402


__os.environ["PYQTGRAPH_QT_LIB"] = __qtpy.API_NAME

if "--verbose" in __sys.argv:
    print("pydidas Using QT: ", __qtpy.API_NAME)


from .fontsize import PYDIDAS_STANDARD_FONT_SIZE  # noqa E402
from .pydidas_qapp import PydidasQApplication  # noqa E402
from .pydidas_splash_screen import PydidasSplashScreen  # noqa E402


__all__ = [
    "PydidasQApplication",
    "PydidasSplashScreen",
    "PYDIDAS_STANDARD_FONT_SIZE",
]

# Start the custom PydidasQApplication to assure the correct
# QApplication is running:
__app = PydidasQApplication(__sys.argv)
