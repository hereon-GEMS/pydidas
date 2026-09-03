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
Package with modified widgets required for creating the pydidas graphical user
interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from types import ModuleType

from . import (
    base_classes,
    base_reimplementations,
    controllers,
    dialogs,
    extended_widgets,
    misc,
    param_io,
    plugin_config_widgets,
    windows,
    workflow_edit,
)
from .file_dialog import PydidasFileDialog
from .utilities import *


def __getattr__(name: str) -> ModuleType:
    """Lazy-load sub-packages on demand."""
    if name in ("data_viewer", "silx_plot", "pyqtgraph_plot"):
        import importlib

        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module  # Cache in module globals
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "base_classes",
    "base_reimplementations",
    "controllers",
    "data_viewer",
    "dialogs",
    "extended_widgets",
    "file_browser",
    "misc",
    "param_io",
    "plugin_config_widgets",
    "pyqtgraph_plot",
    "silx_plot",
    "windows",
    "workflow_edit",
    "PydidasFileDialog",
] + utilities.__all__
