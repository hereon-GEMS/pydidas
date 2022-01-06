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
Module with the WorkflowTreeExporterBase class which exporters should inherit
from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTreeIoYaml']

import yaml

from ...core.constants import YAML_EXTENSIONS
from .workflow_tree_io_base import WorkflowTreeIoBase


class WorkflowTreeIoYaml(WorkflowTreeIoBase):
    """
    Base class for WorkflowTree exporters.
    """
    extensions = YAML_EXTENSIONS
    format_name = 'YAML'

    @classmethod
    def export_to_file(cls, filename, tree, **kwargs):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        content : type
            The content in any format.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _dump = [node.dump() for node in tree.nodes.values()]
        with open(filename, 'w') as _file:
            yaml.safe_dump(_dump, _file)

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.

        Returns
        -------
        pydidas.workflow.WorkflowTree
            The restored WorkflowTree.
        """
        from ..workflow_tree import _WorkflowTree

        with open(filename, 'r') as _file:
            _restoration = yaml.safe_load(_file)

        _tree = _WorkflowTree()
        _tree.restore_from_list_of_nodes(_restoration)
        return _tree
