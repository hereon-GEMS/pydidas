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
Package with modified widgets required for creating the pydidas graphical user
interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from . import (
    controllers,
    data_viewer,
    dialogues,
    factory,
    framework,
    misc,
    parameter_config,
    plugin_config_widgets,
    selection,
    silx_plot,
    windows,
    workflow_edit,
)
from .factory import CreateWidgetsMixIn
from .file_dialog import *
from .scroll_area import *
from .utilities import *
from .widget_with_parameter_collection import *


__all__ = [
    "controllers",
    "data_viewer",
    "dialogues",
    "factory",
    "framework",
    "misc",
    "parameter_config",
    "plugin_config_widgets",
    "selection",
    "silx_plot",
    "windows",
    "workflow_edit",
    "CreateWidgetsMixIn",
] + (
    file_dialog.__all__
    + scroll_area.__all__
    + utilities.__all__
    + widget_with_parameter_collection.__all__
)

# Clean up the namespace:
del file_dialog, scroll_area, utilities, widget_with_parameter_collection
