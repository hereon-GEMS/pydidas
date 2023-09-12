# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


# import __all__ items from modules:
from .base_frame import *
from .base_frame_with_app import *
from .font_scaling_toolbar import *
from .pydidas_status_widget import *
from .pydidas_frame_stack import *
from .pydidas_window import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import base_frame

__all__.extend(base_frame.__all__)
del base_frame

from . import base_frame_with_app

__all__.extend(base_frame_with_app.__all__)
del base_frame_with_app

from . import font_scaling_toolbar

__all__.extend(font_scaling_toolbar.__all__)
del font_scaling_toolbar

from . import pydidas_status_widget

__all__.extend(pydidas_status_widget.__all__)
del pydidas_status_widget

from . import pydidas_frame_stack

__all__.extend(pydidas_frame_stack.__all__)
del pydidas_frame_stack

from . import pydidas_window

__all__.extend(pydidas_window.__all__)
del pydidas_window
