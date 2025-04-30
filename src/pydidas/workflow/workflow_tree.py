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
Module with the WorkflowTree singleton which is pydidas's context instance of
a ProcessingTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowTree"]

from typing import Type

from pydidas.core import SingletonObject
from pydidas.workflow.processing_tree import ProcessingTree


class WorkflowTree(SingletonObject, ProcessingTree):
    """
    The WorkflowTree class is the singleton instance of the ProcessingTree
    class and is used to store the current processing tree of the workflow.

    It implements a copy method to allow copying the current tree to a new
    instance of the ProcessingTree class.
    """

    def __copy__(self, as_type: Type | None = None) -> ProcessingTree:
        """
        Create a copy of the current ProcessingTree instance.

        Returns
        -------
        ProcessingTree
            A new instance of the ProcessingTree class with the same
            parameters as the current instance.
        """
        return ProcessingTree.__copy__(self, as_type=ProcessingTree)

    def copy(self, as_type: Type | None = None) -> ProcessingTree:
        """
        Create a copy of the current ProcessingTree instance.

        Returns
        -------
        ProcessingTree
            A new instance of the ProcessingTree class with the same
            parameters as the current instance.
        """
        return self.__copy__()
