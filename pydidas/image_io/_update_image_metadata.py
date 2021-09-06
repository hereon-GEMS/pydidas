# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The read_image_func module includes the read_image function which queries
the ImageReaderCollection for the correct reader and reads the image from the file.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['update_image_metadata']

from ..core.experimental_settings import ExperimentalSettings

EXP_SETTINGS = ExperimentalSettings()

def update_image_metadata(dataset):
    """
    Apply metadata acquired from the ExperimentalSettings to the image.

    Note: As arrays are mutable, there is no return value but the dataset
    is changed in place.
    """
    dataset.axis_labels = ('det_y', 'det_x')
    if EXP_SETTINGS.get_param_value('detector_sizey') > 0:
        dataset.axis_scales[0] = EXP_SETTINGS.get_param_value('detector_sizey')
        dataset.axis_units[0] = 'm'
    if EXP_SETTINGS.get_param_value('detector_sizex') > 0:
        dataset.axis_scales[1] = EXP_SETTINGS.get_param_value('detector_sizex')
        dataset.axis_units[1] = 'm'
    return dataset
