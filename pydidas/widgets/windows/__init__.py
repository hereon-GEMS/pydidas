# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The pydidas.gui.windows subpackage includes stand-alone main windows which can
be opened by the main GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .about_window import *
from .export_eiger_pixelmask import *
from .feedback_window import *
from .image_series_operations_window import *
from .global_settings_window import *
from .manually_set_beamcenter_window import *
from .mask_editor_window import *
from .qt_paths_window import *
from .scan_dimension_information_window import *
from .select_integration_region_window import *
from .show_detailed_plugin_results_window import *
from .show_information_for_result import *
from .tweak_plugin_parameter_window import *
from .user_config_window import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import about_window

__all__.extend(about_window.__all__)
del about_window

from . import export_eiger_pixelmask

__all__.extend(export_eiger_pixelmask.__all__)
del export_eiger_pixelmask

from . import feedback_window

__all__.extend(feedback_window.__all__)
del feedback_window

from . import image_series_operations_window

__all__.extend(image_series_operations_window.__all__)
del image_series_operations_window

from . import global_settings_window

__all__.extend(global_settings_window.__all__)
del global_settings_window

from . import manually_set_beamcenter_window

__all__.extend(manually_set_beamcenter_window.__all__)
del manually_set_beamcenter_window

from . import mask_editor_window

__all__.extend(mask_editor_window.__all__)
del mask_editor_window

from . import qt_paths_window

__all__.extend(qt_paths_window.__all__)
del qt_paths_window

from . import scan_dimension_information_window

__all__.extend(scan_dimension_information_window.__all__)
del scan_dimension_information_window

from . import select_integration_region_window

__all__.extend(select_integration_region_window.__all__)
del select_integration_region_window

from . import show_detailed_plugin_results_window

__all__.extend(show_detailed_plugin_results_window.__all__)
del show_detailed_plugin_results_window

from . import show_information_for_result

__all__.extend(show_information_for_result.__all__)
del show_information_for_result

from . import tweak_plugin_parameter_window

__all__.extend(tweak_plugin_parameter_window.__all__)
del tweak_plugin_parameter_window

from . import user_config_window

__all__.extend(user_config_window.__all__)
del user_config_window
