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
The PluginPositionNode class can calculate node positions in a WorkflowTree.

This module includes the PluginPositionNode class which is a subclassed GenericNode
with additional functionality to get the size of an encompassing square around
the node and all its children.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginPositionNode"]


import numpy as np

from pydidas.workflow.generic_node import GenericNode


class PluginPositionNode(GenericNode):
    """
    The PluginPositionNode class manages the sizes and positions of items in a tree.

    This class only manages the position data without any reference to actual widgets.
    """

    PLUGIN_HEIGHT_OFFSET = 0.6
    PLUGIN_WIDTH_OFFSET = 0.1

    @property
    def width(self) -> float:
        """
        Get the width of the current branch.

        This property will return the width of the current tree branch
        (this node and all children).

        Returns
        -------
        float
            The width of the tree branch.
        """
        if self.is_leaf:
            return 1
        _w = (len(self._children) - 1) * self.PLUGIN_WIDTH_OFFSET
        for child in self._children:
            _w += child.width
        return _w

    @property
    def height(self) -> float:
        """
        Get the height of the current branch.

        This property will return the height of the current tree branch
        (this node and all children).

        Returns
        -------
        float
            The height of the tree branch.
        """
        if self.is_leaf:
            return 1
        _h = []
        for child in self._children:
            _h.append(child.height)
        return max(_h) + self.PLUGIN_HEIGHT_OFFSET + 1

    def get_relative_positions(self, accuracy: int = 3) -> dict:
        """
        Get the relative positions of the node and all children.

        This method will generate a dictionary with keys corresponding to the
        node_ids and the relative positions of children with respect to the
        parent node.

        Parameters
        ----------
        accuracy : int, optional
            The accuracy of the position results.

        Returns
        -------
        pos : dict
            A dictionary with entries of the type "node_id: [xpos, ypos]".
        """
        pos = {self.node_id: [np.round((self.width - 1) / 2, accuracy), 0]}
        if self.is_leaf:
            return pos
        xoffset = 0
        yoffset = 1 + self.PLUGIN_HEIGHT_OFFSET
        for child in self._children:
            _p = child.get_relative_positions()
            for _key, (_x, _y) in _p.items():
                pos[_key] = [
                    np.round(_x + xoffset, accuracy),
                    np.round(_y + yoffset, accuracy),
                ]
            xoffset += child.width + self.PLUGIN_WIDTH_OFFSET
        return pos
