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
Package with modified widgets required for creating the pydidas graphical user
interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import sub-packages:
from . import dialogues
from . import factory
from . import parameter_config
from . import selection
from . import workflow_edit

__all__.extend(
    ["dialogues", "factory", "parameter_config", "selection", "workflow_edit"]
)

# explicitly import items from subpackages into the module:
from .factory import CreateWidgetsMixIn

__all__.extend(["CreateWidgetsMixIn"])

# import __all__ items from modules:
from .base_frame import *
from .base_frame_with_app import *
from .central_widget_stack import *
from .info_widget import *
from .qta_button import *
from .read_only_text_widget import *
from .scroll_area import *
from .utilities import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import base_frame

__all__.extend(base_frame.__all__)
del base_frame

from . import base_frame_with_app

__all__.extend(base_frame_with_app.__all__)
del base_frame_with_app

from . import central_widget_stack

__all__.extend(central_widget_stack.__all__)
del central_widget_stack

from . import info_widget

__all__.extend(info_widget.__all__)
del info_widget

from . import qta_button

__all__.extend(qta_button.__all__)
del qta_button

from . import read_only_text_widget

__all__.extend(read_only_text_widget.__all__)
del read_only_text_widget

from . import scroll_area

__all__.extend(scroll_area.__all__)
del scroll_area

from . import utilities

__all__.extend(utilities.__all__)
del utilities
