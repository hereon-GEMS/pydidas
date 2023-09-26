# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the WorkflowTreeIoYaml class to import/export the WorkflowTree to yaml
files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowTreeIoYaml"]


from pathlib import Path
from typing import NewType, Union

import yaml

from ...core.constants import YAML_EXTENSIONS
from .workflow_tree_io_base import WorkflowTreeIoBase


WorkflowTree = NewType("WWorkflowTree", type)


class WorkflowTreeIoYaml(WorkflowTreeIoBase):
    """
    Base class for WorkflowTree exporters.
    """

    extensions = YAML_EXTENSIONS
    format_name = "YAML"

    @classmethod
    def export_to_file(
        cls, filename: Union[Path, str], tree: WorkflowTree, **kwargs: dict
    ):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        tree : WorkflowTree
            The workflow tree instance.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _dump = [node.dump() for node in tree.nodes.values()]
        with open(filename, "w") as _file:
            yaml.safe_dump(_dump, _file)

    @classmethod
    def import_from_file(cls, filename: Union[Path, str]) -> WorkflowTree:
        """
        Restore the content from a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Union[Path, str]
            The filename of the file to be written.

        Returns
        -------
        pydidas.workflow.WorkflowTree
            The restored WorkflowTree.
        """
        from ..workflow_tree import _WorkflowTree

        with open(filename, "r") as _file:
            _restoration = yaml.safe_load(_file)

        _tree = _WorkflowTree()
        _tree.restore_from_list_of_nodes(_restoration)
        return _tree
