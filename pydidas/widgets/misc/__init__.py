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
Package with miscellaneous individual QWidgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .line_edit_with_icon import *
from .point_position_table_widget import *
from .select_image_frame_widget import *
from .show_information_for_result import *
from .show_integration_roi_params_widget import *
from .read_only_text_widget import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import line_edit_with_icon

__all__.extend(line_edit_with_icon.__all__)
del line_edit_with_icon

from . import point_position_table_widget

__all__.extend(point_position_table_widget.__all__)
del point_position_table_widget

from . import select_image_frame_widget

__all__.extend(select_image_frame_widget.__all__)
del select_image_frame_widget

from . import show_information_for_result

__all__.extend(show_information_for_result.__all__)
del show_information_for_result

from . import show_integration_roi_params_widget

__all__.extend(show_integration_roi_params_widget.__all__)
del show_integration_roi_params_widget

from . import read_only_text_widget

__all__.extend(read_only_text_widget.__all__)
del read_only_text_widget
