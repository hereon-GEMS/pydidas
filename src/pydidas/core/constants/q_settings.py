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
Definitions of variables for persistent QSettings names in use.

The QSETTINGS_GLOBAL_KEYS and QSETTINGS_USER_KEYS constant holds the names
of all global QSetting keys used in pydidas. These are required to verify
that these settings have been written and exist. Pydidas will perform an
existence check upon module holds information about the global keys used in
pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "QSETTINGS_GLOBAL_KEYS",
    "QSETTINGS_USER_KEYS",
    "QSETTINGS_USER_SPECIAL_KEYS",
]


QSETTINGS_GLOBAL_KEYS = [
    "mp_n_workers",
    "data_buffer_size",
    "shared_buffer_size",
    "shared_buffer_max_n",
    "max_image_size",
    "plot_update_time",
]

QSETTINGS_USER_KEYS = [
    "mosaic_border_width",
    "mosaic_border_value",
    "max_number_curves",
    "histogram_outlier_fraction_low",
    "histogram_outlier_fraction_high",
    "plugin_path",
    "auto_check_for_updates",
    "cmap_nan_color",
]

QSETTINGS_USER_SPECIAL_KEYS = [
    "cmap_name",
]
