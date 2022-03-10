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
The QSETTINGS_GLOBAL_KEYS constant holds the names of all global QSetting keys
used in pydidas. These are required to verify that these settings have been
written and exist. Pydidas will perform an existance check upon
module holds information about the global keys used in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['QSETTINGS_GLOBAL_KEYS']


QSETTINGS_GLOBAL_KEYS = ['mp_n_workers',
                         'shared_buffer_size',
                         'shared_buffer_max_n',
                         'det_mask',
                         'det_mask_val',
                         'mosaic_border_width',
                         'mosaic_border_value',
                         'mosaic_max_size',
                         'plugin_path',
                         'plot_update_time']
