#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with Warning class for showing notifications."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTreePluginPositionNode']

import numpy as np

from .generic_node import GenericNode
from ..config import gui_constants

class WorkflowTreePluginPositionNode(GenericNode):
    """
    The WorkflowTreePluginPositionNode class manages the sizes and positions of
    widgets in the workflow tree. This class only manages the position data
    without any reference to the actual QtWidgets.
    """
    generic_width = gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
    generic_height = gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT
    child_spacing = gui_constants.GENERIC_PLUGIN_WIDGET_Y_OFFSET
    border_spacing = gui_constants.GENERIC_PLUGIN_WIDGET_X_OFFSET

    def __init__(self, parent=None, node_id=None):
        super().__init__(parent=parent)
        self.node_id = node_id
        self._children = []
        if parent:
            parent.add_child(self)

    @property
    def width(self):
        if self.is_leaf():
            return self.generic_width
        w = (len(self._children) - 1) * self.child_spacing
        for child in self._children:
            w += child.width
        return w

    @property
    def height(self):
        if len(self._children) == 0:
            return self.generic_height
        h = []
        for child in self._children:
            h.append(child.height)
        return max(h) + self.child_spacing + self.generic_height

    def get_relative_positions(self):
        pos = {self.node_id: [(self.width - self.generic_width) // 2, 0]}
        if self.is_leaf():
            return pos
        xoffset = 0
        yoffset = self.generic_height + self.child_spacing
        for child in self._children:
            _p = child.get_relative_positions()
            for key in _p:
                pos.update({key: [_p[key][0] + xoffset,
                                  _p[key][1] + yoffset]})
            xoffset += child.width + self.child_spacing
        self.make_grid_positions_positive(pos)
        return pos

    @staticmethod
    def make_grid_positions_positive(pos_dict):
        vals = np.asarray(list(pos_dict.values()))
        xoffset = np.amin(vals[:, 0])
        yoffset = np.amin(vals[:, 1])
        for key in pos_dict:
            pos_dict[key] = [pos_dict[key][0] - xoffset,
                             pos_dict[key][1] - yoffset]
