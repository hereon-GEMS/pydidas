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
Module with the ImageMathFrame which allows to perform mathematical
operations on images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ImageMathFrame"]


from ...contexts import ScanContext
from ...core import Parameter, ParameterCollection, get_generic_param_collection
from ...workflow import WorkflowTree
from .builders import ImageMathFrameBuilder


SCAN_SETTINGS = ScanContext()
WORKFLOW_TREE = WorkflowTree()

_buffer_param = Parameter(
    "buffer_no",
    str,
    "Image #1",
    name="Image buffer number",
    choices=["Image #1", "Image #2", "Image #3", "Image #4", "Image #5"],
)


class ImageMathFrame(ImageMathFrameBuilder):
    """
    The ImageMathFrame allows to perform mathematical operations on single
    frames or to combine multiple frames.
    """

    menu_icon = "qta::mdi.home"
    menu_title = "Image math"
    menu_entry = "Image math"

    default_params = ParameterCollection(
        _buffer_param,
        get_generic_param_collection(
            "scan_index1", "scan_index2", "scan_index3", "scan_index4"
        ),
    )

    def __init__(self, parent=None, **kwargs):
        ImageMathFrameBuilder.__init__(self, parent=parent, **kwargs)
        self.set_default_params()
