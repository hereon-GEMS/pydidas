# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingTreeIoHdf5"]


from pathlib import Path
from typing import TYPE_CHECKING, Any

import h5py

from pydidas.core import UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import iso_timestring
from pydidas.core.utils.file_checks import verify_is_new_file_or_replace_set
from pydidas.core.utils.hdf5 import (
    nxs_create_recursive_groups,
    nxs_param_config_for_dset,
    nxs_write_dataset,
    read_and_decode_hdf5_dataset,
)
from pydidas.core.utils.hdf5.hdf5_pydidas_utils import get_exported_pydidas_version
from pydidas.core.utils.hdf5.nxs_export import nxs_create_nxentry
from pydidas.version import VERSION
from pydidas.workflow.processing_tree_io.processing_tree_io_base import (
    ProcessingTreeIoBase,
)


if TYPE_CHECKING:
    from pydidas.workflow.processing_tree import ProcessingTree


_GENERIC_NODE_KEYS = ["node_id", "parent", "children", "plugin_class"]


class ProcessingTreeIoHdf5(ProcessingTreeIoBase):
    """
    Import/Export class for the ProcessingTree to/from HDF5 files.
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"
    default_suffix = ".nxs"

    @staticmethod
    def export_to_file(
        filename: Path | str, tree: "ProcessingTree", **kwargs: Any
    ) -> None:
        """
        Write the content of the ProcessingTree to an HDF5 file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        tree : ProcessingTree
            The workflow tree instance.
        **kwargs : Any
            Additional keyword arguments.
        """
        verify_is_new_file_or_replace_set(filename, **kwargs)
        with h5py.File(filename, "a") as _file:
            _entry = nxs_create_nxentry(_file, "entry")
            if "pydidas_workflow" in _entry:
                del _entry["pydidas_workflow"]

            _group = nxs_create_recursive_groups(
                _entry, "pydidas_workflow", group_type="NXprocess"
            )
            nxs_write_dataset(_group, "program", "pydidas")
            nxs_write_dataset(_group, "version", VERSION)
            nxs_write_dataset(_group, "date", iso_timestring())
            nxs_write_dataset(_group, "sequence_index", 1)

            _config_group = nxs_create_recursive_groups(
                _group, "workflow_info", group_type="NXparameters"
            )
            _node_names = [f"workflow_node_{_id:02d}" for _id in tree.nodes.keys()]
            nxs_write_dataset(_config_group, "nodes", _node_names)
            nxs_write_dataset(_config_group, "num_nodes", len(tree.nodes))

            for _id, _node in tree.nodes.items():
                _param_group = nxs_create_recursive_groups(
                    _group, f"workflow_node_{_id:02d}", group_type="NXparameters"
                )
                _node_data = _node.dump()
                for _key in ["node_id", "parent", "children", "plugin_class"]:
                    nxs_write_dataset(_param_group, _key, _node_data[_key])
                for _key, _param in _node.plugin.params.items():
                    if _key.startswith("_"):
                        continue
                    _val, _attributes = nxs_param_config_for_dset(_param)
                    nxs_write_dataset(_param_group, _key, _val, **_attributes)

    @classmethod
    def import_from_file(  # type: ignore[override]
        cls, filename: Path | str, **kwargs: Any
    ) -> "ProcessingTree":
        """
        Restore the content from an HDF5 file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be read.
        **kwargs : Any
            Additional keyword arguments. Not used in the HDF5 implementation.

        Returns
        -------
        ProcessingTree
            The restored ProcessingTree.
        """
        _version = "23.7.5 or earlier"

        with h5py.File(filename, "r") as _h5file:
            try:
                _version = get_exported_pydidas_version(_h5file)
                if "/entry/pydidas_workflow/workflow_info" in _h5file:
                    _tree = cls._import_processing_tree(_h5file)
                else:
                    _tree = cls._import_legacy_processing_tree(_h5file)
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

    @staticmethod
    def _import_legacy_processing_tree(hdf5_file: h5py.File) -> "ProcessingTree":
        """
        Import the ProcessingTree from the legacy HDF5 file.

        Parameters
        ----------
        hdf5_file : h5py.File
            The HDF5 file to be imported.

        Returns
        -------
        ProcessingTree
            The restored ProcessingTree from the legacy HDF5 file.
        """
        from pydidas.workflow.processing_tree import ProcessingTree

        _tree_repr = read_and_decode_hdf5_dataset(
            hdf5_file["entry/pydidas_config/workflow"]
        )
        _tree = ProcessingTree()
        _tree.restore_from_string(_tree_repr)
        return _tree

    @staticmethod
    def _import_processing_tree(hdf5_file: h5py.File) -> "ProcessingTree":
        """
        Import the ProcessingTree from the HDF5 file.#

        Parameters
        ----------
        hdf5_file : h5py.File
            The HDF5 file to be imported.

        Returns
        -------
        ProcessingTree
            The restored ProcessingTree from the HDF5 file.
        """
        from pydidas.workflow.processing_tree import ProcessingTree

        _node_names = [
            _key.decode()
            for _key in read_and_decode_hdf5_dataset(
                hdf5_file["entry/pydidas_workflow/workflow_info/nodes"]
            )
        ]
        _nodes = []
        for _node_key in _node_names:
            _group = hdf5_file[f"entry/pydidas_workflow/{_node_key}"]
            _node_data = {
                _key: read_and_decode_hdf5_dataset(_group[_key])
                for _key in _GENERIC_NODE_KEYS
            }
            _node_data["plugin_params"] = [
                (_param_key, read_and_decode_hdf5_dataset(_group[_param_key]))
                for _param_key in _group.keys()
                if _param_key not in _GENERIC_NODE_KEYS
            ]
            _nodes.append(_node_data)
        _tree = ProcessingTree()
        _tree.restore_from_list_of_nodes(_nodes)
        return _tree
