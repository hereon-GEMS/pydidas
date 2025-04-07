# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the ProcessingTreeIoHdf5 class to import/export the WorkflowTree to HDF5.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingTreeIoHdf5"]


from pathlib import Path
from typing import NewType

import h5py

from pydidas.core import UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import (
    create_nx_dataset,
    create_nx_entry_groups,
    read_and_decode_hdf5_dataset,
)
from pydidas.version import VERSION
from pydidas.workflow.processing_tree_io.processing_tree_io_base import (
    ProcessingTreeIoBase,
)


ProcessingTree = NewType("ProcessingTree", type)


class ProcessingTreeIoHdf5(ProcessingTreeIoBase):
    """
    Import/Export class for the ProcessingTree to/from HDF5 files.
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"

    @classmethod
    def export_to_file(cls, filename: Path | str, tree: ProcessingTree, **kwargs: dict):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Path | str
            The filename of the file to be written.
        tree : ProcessingTree
            The workflow tree instance.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _group_name = "entry/pydidas_config"
        with h5py.File(filename, "a") as _file:
            create_nx_entry_groups(_file, _group_name, group_type="NXcollection")
            create_nx_dataset(_file[_group_name], "workflow", tree.export_to_string())
            create_nx_dataset(_file[_group_name], "pydidas_version", VERSION)

    @classmethod
    def import_from_file(cls, filename: Path | str) -> ProcessingTree:
        """
        Restore the content from a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Path | str
            The filename of the file to be written.

        Returns
        -------
        ProcessingTree
            The restored ProcessingTree.
        """
        from pydidas.workflow.processing_tree import ProcessingTree

        _version = "23.7.5 or earlier"

        with h5py.File(filename, "r") as _file:
            try:
                _tree_repr = read_and_decode_hdf5_dataset(
                    _file["entry/pydidas_config/workflow"]
                )
                _version = read_and_decode_hdf5_dataset(
                    _file["entry/pydidas_config/pydidas_version"]
                )
                _tree = ProcessingTree()
                _tree.restore_from_string(_tree_repr)
            except (KeyError, TypeError, UserConfigError, ValueError, NameError):
                if _version < VERSION:
                    raise UserConfigError(
                        "Import of ProcessingTree was not successful. \n\n"
                        "The selected file does not include a workflow tree "
                        "configuration or the ProcessingTree was created with "
                        f"version {_version} and could not be imported in the "
                        f"current version ({VERSION})."
                    )
                raise UserConfigError(
                    "Could not import the Workflow from the given file:"
                    f"\n    {filename}\nPlease check that the content of the file "
                    "is a Pydidas ProcessingTree."
                )
        return _tree
