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
The pydidas.gui.windows subpackage includes stand-alone main windows which can
be opened by the main GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

# import hdf5_browser_window first to avoid circular imports
from . import hdf5_browser_window
from .about_window import *
from .convert_fit2d_geometry import *
from .export_eiger_pixelmask import *
from .feedback_window import *
from .global_settings_window import *
from .hdf5_browser_window import *
from .image_series_operations_window import *
from .manually_set_beamcenter_window import *
from .mask_editor_window import *
from .qt_paths_window import *
from .scan_dimension_information_window import *
from .select_integration_region_window import *
from .show_detailed_plugin_results_window import *
from .show_information_for_result import *
from .tweak_plugin_parameter_window import *
from .user_config_window import *


__all__ = (
    about_window.__all__
    + convert_fit2d_geometry.__all__
    + export_eiger_pixelmask.__all__
    + feedback_window.__all__
    + global_settings_window.__all__
    + hdf5_browser_window.__all__
    + image_series_operations_window.__all__
    + manually_set_beamcenter_window.__all__
    + mask_editor_window.__all__
    + qt_paths_window.__all__
    + scan_dimension_information_window.__all__
    + select_integration_region_window.__all__
    + show_information_for_result.__all__
    + tweak_plugin_parameter_window.__all__
    + user_config_window.__all__
    + show_detailed_plugin_results_window.__all__
)

# Clean up the namespace:
del (
    about_window,
    convert_fit2d_geometry,
    export_eiger_pixelmask,
    feedback_window,
    global_settings_window,
    hdf5_browser_window,
    image_series_operations_window,
    manually_set_beamcenter_window,
    mask_editor_window,
    qt_paths_window,
    scan_dimension_information_window,
    select_integration_region_window,
    show_information_for_result,
    tweak_plugin_parameter_window,
    user_config_window,
    show_detailed_plugin_results_window,
)
