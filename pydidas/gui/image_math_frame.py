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
Module with the ImageMathsFrame which allows to perform mathematical
operations on images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ImageMathFrame']


from ..core import (Parameter, ParameterCollection,
                    get_generic_param_collection)
from ..experiment import ScanSetup
from ..workflow import WorkflowTree
from ..widgets import BaseFrame
from .builders import ImageMathFrameBuilder


SCAN_SETTINGS = ScanSetup()
WORKFLOW_TREE = WorkflowTree()

_buffer_param = Parameter(
    'buffer_no', str, 'Image #1',
    name='Image buffer number',
    choices=['Image #1', 'Image #2', 'Image #3', 'Image #4', 'Image #5'])


class ImageMathFrame(ImageMathFrameBuilder):
    """
    The ImageMathFrame allows to perform mathematical operations on single
    frames or to combine multiple frames.
    """
    default_params = ParameterCollection(
        _buffer_param, get_generic_param_collection(
            'scan_index1', 'scan_index2', 'scan_index3', 'scan_index4'))

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        ImageMathFrameBuilder.__init__(self)
        self.set_default_params()
        self.build_frame()

    def frame_activated(self, index):
        ...
