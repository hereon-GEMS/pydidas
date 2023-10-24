# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import sub-packages:
from . import controllers
from . import dialogues
from . import factory
from . import framework
from . import misc
from . import parameter_config
from . import plugin_config_widgets
from . import selection
from . import silx_plot
from . import windows
from . import workflow_edit

__all__.extend(
    [
        "controllers",
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
    ]
)

# explicitly import items from subpackages into the module:
from .factory import CreateWidgetsMixIn

__all__.extend(["CreateWidgetsMixIn"])

# import __all__ items from modules:
from .file_dialog import *
from .scroll_area import *
from .utilities import *
from .widget_with_parameter_collection import *

# add modules' __all__ items to package's __all__ items and unclutter the
from . import file_dialog

__all__.extend(file_dialog.__all__)
del file_dialog

from . import scroll_area

__all__.extend(scroll_area.__all__)
del scroll_area

from . import utilities

__all__.extend(utilities.__all__)
del utilities

from . import widget_with_parameter_collection

__all__.extend(widget_with_parameter_collection.__all__)
del widget_with_parameter_collection
