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
Module with the ProcessingTreeIoYaml class to import/export the WorkflowTree to yaml
files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingTreeIoYaml"]


from pathlib import Path
from typing import NewType, Union

import yaml

from pydidas.core import UserConfigError
from pydidas.core.constants import YAML_EXTENSIONS
from pydidas.version import VERSION
from pydidas.workflow.processing_tree_io.processing_tree_io_base import (
    ProcessingTreeIoBase,
)


ProcessingTree = NewType("ProcessingTree", type)


class ProcessingTreeIoYaml(ProcessingTreeIoBase):
    """
    Base class for ProcessingTree exporters.
    """

    extensions = YAML_EXTENSIONS
    format_name = "YAML"

    @classmethod
    def export_to_file(
        cls, filename: Union[Path, str], tree: ProcessingTree, **kwargs: dict
    ):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        tree : ProcessingTree
            The workflow tree instance.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _dump = {
            "version": VERSION,
            "nodes": tree.export_to_list_of_nodes(),
        }
        with open(filename, "w") as _file:
            yaml.safe_dump(_dump, _file)

    @classmethod
    def import_from_file(cls, filename: Union[Path, str]) -> ProcessingTree:
        """
        Restore the content from a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Union[Path, str]
            The filename of the file to be written.

        Returns
        -------
        pydidas.workflow.ProcessingTree
            The restored ProcessingTree.
        """
        from pydidas.workflow.processing_tree import ProcessingTree

        _version = "23.7.5 or earlier"

        with open(filename, "r") as _file:
            _restoration = yaml.safe_load(_file)

        try:
            if isinstance(_restoration, dict):
                _version = _restoration["version"]
                _restoration = _restoration["nodes"]
            _tree = ProcessingTree()
            _tree.restore_from_list_of_nodes(_restoration)
        except (KeyError, TypeError, UserConfigError, ValueError, NameError):
            if _version < VERSION:
                raise UserConfigError(
                    "Import of ProcessingTree was not successful. \n\n"
                    "The selected file does not include a workflow tree configuration "
                    f"or the ProcessingTree was created with version {_version} and "
                    f"could not be imported in the current version ({VERSION})."
                )
            raise UserConfigError(
                "Could not import the Workflow from the given file:"
                f"\n    {filename}\nPlease check that the content of the file "
                "is a Pydidas ProcessingTree."
            )
        return _tree
