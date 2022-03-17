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
Module with the PluginPositionNode class which is a subclassed GenericNode
with additional functionality to get the size of an encompassing square around
the node and all its children.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PluginPositionNode']

import numpy as np

from .generic_node import GenericNode
from ..core.constants import (
    GENERIC_PLUGIN_WIDGET_WIDTH, GENERIC_PLUGIN_WIDGET_HEIGHT,
    GENERIC_PLUGIN_WIDGET_Y_OFFSET, GENERIC_PLUGIN_WIDGET_X_OFFSET)


class PluginPositionNode(GenericNode):
    """
    The PluginPositionNode class manages the sizes and positions of
    items in a tree. This class only manages the position data without any
    reference to actual widgets.
    """

    @property
    def width(self):
        """
        Get the width of the current branch.

        This property will return the width of the current tree branch
        (this node and all children).

        Returns
        -------
        int
            The width of the tree branch.
        """
        if self.is_leaf:
            return GENERIC_PLUGIN_WIDGET_WIDTH
        _w = (len(self._children) - 1) * GENERIC_PLUGIN_WIDGET_X_OFFSET
        for child in self._children:
            _w += child.width
        return _w

    @property
    def height(self):
        """
        Get the height of the current branch.

        This property will return the height of the current tree branch
        (this node and all children).

        Returns
        -------
        int
            The height of the tree branch.
        """
        if self.is_leaf:
            return GENERIC_PLUGIN_WIDGET_HEIGHT
        _h = []
        for child in self._children:
            _h.append(child.height)
        return (max(_h)
                + GENERIC_PLUGIN_WIDGET_Y_OFFSET
                + GENERIC_PLUGIN_WIDGET_HEIGHT)

    def get_relative_positions(self):
        """
        Get the relative positions of the node and all children.

        This method will generate a dictionary with keys corresponding to the
        node_ids and the relative positions of children with respect to the
        parent node.

        Returns
        -------
        pos : dict
            A dictionary with entries of the type "node_id: [xpos, ypos]".
        """
        pos = {self.node_id: \
                   [(self.width - GENERIC_PLUGIN_WIDGET_WIDTH) // 2, 0]}
        if self.is_leaf:
            return pos
        xoffset = 0
        yoffset = GENERIC_PLUGIN_WIDGET_HEIGHT + GENERIC_PLUGIN_WIDGET_Y_OFFSET
        for child in self._children:
            _p = child.get_relative_positions()
            for key in _p:
                pos.update({key: [_p[key][0] + xoffset,
                                  _p[key][1] + yoffset]})
            xoffset += child.width + GENERIC_PLUGIN_WIDGET_X_OFFSET
        self.make_grid_positions_positive(pos)
        return pos

    @staticmethod
    def make_grid_positions_positive(pos_dict):
        """
        Make all grid positions positive.

        Because child positions will be setup symmetrically around the parent
        node, negative numbers will be included. To correctly print the tree,
        positive numbers are required. This method will change the dictionary
        values in place and make them positive.

        Parameters
        ----------
        pos_dict : dict
            A dictionary with entries of the type "node_id: [xpos, ypos]".

        Returns
        -------
        pos_dict : dict
            A dictionary with entries of the type "node_id: [xpos, ypos]"
            where all positions are positive.
        """
        vals = np.asarray(list(pos_dict.values()))
        xoffset = np.amin(vals[:, 0])
        yoffset = np.amin(vals[:, 1])
        for key in pos_dict:
            pos_dict[key] = [pos_dict[key][0] - xoffset,
                             pos_dict[key][1] - yoffset]
