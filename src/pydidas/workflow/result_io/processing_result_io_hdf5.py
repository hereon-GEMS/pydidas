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
Module with the ProcessingResultIoHdf5 class which exports and imports results in
Hdf5 file format.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResultIoHdf5"]


import os
from functools import partial
from pathlib import Path

import h5py

from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import (
    create_nx_dataset,
    create_nx_entry_groups,
    read_and_decode_hdf5_dataset,
)
from pydidas.core.utils.hdf5_dataset_utils import (
    _create_nxdata_axis_entry,
    get_nx_class_for_param,
)
from pydidas.data_io import import_data
from pydidas.version import VERSION
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io.processing_result_io_base import ProcessingResultIoBase
from pydidas.workflow.workflow_tree import WorkflowTree


_DEFAULT_GROUPS = [
    ["entry", "NXentry"],
    ["entry/data", "NXdata"],
    ["entry/instrument", "NXinstrument"],
    ["entry/instrument/detector", "NXdetector"],
    ["entry/instrument/detector/COLLECTION", "NXcollection"],
    ["entry/pydidas_config", "NXcollection"],
    ["entry/pydidas_config/diffraction_exp", "NXcollection"],
    ["entry/pydidas_config/scan", "NXcollection"],
]


def _get_pydidas_context_config_entries(
    scan: Scan, exp: DiffractionExperiment, tree: ProcessingTree
) -> list[list[str, str, dict]]:
    """
    Get the context configuration from the pydidas Context singletons.

    Parameters
    ----------
    scan : pydidas.contexts.Scan
        The scan (context).
    exp : pydidas.contexts.DiffractionExperiment
        The diffraction experiment (context).
    tree : WorkflowTree
        The workflow tree.

    Returns
    -------
    list[list[str, str, dict]]
        List with writable entries for the contexts.
    """
    _dsets = []
    for _key, _param in scan.params.items():
        _dsets.append(
            [
                "entry/pydidas_config/scan",
                _key,
                {"data": _param.value_for_export},
                {"NX_class": get_nx_class_for_param(_param), "units": _param.unit},
            ]
        )
    for _key, _param in exp.params.items():
        _dsets.append(
            [
                "entry/pydidas_config/diffraction_exp",
                _key,
                {"data": _param.value_for_export},
                {"NX_class": get_nx_class_for_param(_param), "units": _param.unit},
            ]
        )
    _dsets += [
        [
            "entry/pydidas_config",
            "workflow",
            {"data": tree.export_to_string()},
            {"NX_class": "NX_CHAR", "units": ""},
        ],
        [
            "entry/pydidas_config",
            "pydidas_version",
            {"data": VERSION},
            {"NX_class": "NX_CHAR", "units": ""},
        ],
        [
            "entry/instrument/detector/COLLECTION",
            "frame_start_number",
            {"data": scan.get_param_value("scan_start_index")},
            {"NX_class": "NX_INT", "units": ""},
        ],
        [
            "entry/instrument/detector",
            "x_pixel_size",
            {"data": exp.get_param_value("detector_pxsizex")},
            {"NX_class": "NX_FLOAT", "units": "um"},
        ],
        [
            "entry/instrument/detector",
            "y_pixel_size",
            {"data": exp.get_param_value("detector_pxsizey")},
            {"NX_class": "NX_FLOAT", "units": "um"},
        ],
        [
            "entry/instrument/detector",
            "distance",
            {"data": exp.get_param_value("detector_dist")},
            {"NX_class": "NX_FLOAT", "units": "m"},
        ],
    ]
    return _dsets


class ProcessingResultIoHdf5(ProcessingResultIoBase):
    """
    Implementation of the ProcessingResultIoBase for Hdf5 files.
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"
    default_extension = "h5"
    _filenames = []
    _save_dir = None
    _metadata_written = False

    @classmethod
    def prepare_files_and_directories(
        cls, save_dir: Path | str, node_information: dict, **kwargs: dict
    ):
        """
        Prepare the hdf5 files with the metadata.

        Parameters
        ----------
        save_dir : Path | str
            The full path for the data to be saved.
        node_information : dict
            A dictionary with nodeID keys and dictionary values. Each value dictionary
            must have the following keys: shape, node_label, data_label, plugin_name
            and the respective values. The shape (tuple) determines the shape of the
            Dataset, the node_label is the user's name for the processing node. The
            data_label gives the description of what the data shows (e.g. intensity)
            and the plugin_name is simply the name of the plugin.
        **kwargs:
            Supported kwargs are:

            scan_context : Optional[pydidas.contexts.Scan]
                The scan context. If None, the generic context will be used.
                Only specify this, if you explicitly require a different context.
                The default is None.
            diffraction_exp_context : Optional[pydidas.contexts.DiffractionExperiment]
                The diffraction experiment context. If None, the generic context
                will be used. Only specify this, if you explicitly require a
                different context. The default is None.
            workflow_tree : Union[WorkflowTree, None], optional
                The WorkflowTree. If None, the generic WorkflowTree will be used.
                Only specify this, if you explicitly require a different context.
                The default is None.
        """
        _scan = kwargs.get("scan_context", ScanContext())
        _exp = kwargs.get("diffraction_exp_context", DiffractionExperimentContext())
        _tree = kwargs.get("workflow_tree", WorkflowTree())
        cls._save_dir = save_dir if isinstance(save_dir, Path) else Path(save_dir)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        cls._node_information = node_information
        cls._filenames = cls.get_filenames_from_labels()
        cls._metadata_written = False
        for _index in cls._node_information.keys():
            cls._create_file_and_populate_metadata(_index, _scan, _exp, _tree)

    @classmethod
    def _create_file_and_populate_metadata(
        cls,
        node_id: int,
        scan: Scan,
        exp: DiffractionExperiment,
        workflow: ProcessingTree,
    ):
        """
        Create a hdf5 file and populate it with the Scan metadata.

        Parameters
        ----------
        node_id : int
            The nodeID.
        scan : pydidas.contexts.Scan
            The scan (context).
        exp : pydidas.contexts.DiffractionExperiment
            The diffraction experiment (context).
        workflow : WorkflowTree
            The workflow tree.
        """
        _dsets = cls._get_datasets_to_be_written(node_id, scan, exp, workflow)
        with h5py.File(cls._save_dir / cls._filenames[node_id], "w") as _file:
            for _group_key, _type in _DEFAULT_GROUPS:
                create_nx_entry_groups(_file, _group_key, group_type=_type)
            for _group, _name, kws, _nxs_attrs in _dsets:
                create_nx_dataset(_file[_group], _name, kws, **_nxs_attrs)

    @classmethod
    def _get_datasets_to_be_written(
        cls,
        node_id: int,
        scan: Scan,
        exp: DiffractionExperiment,
        workflow: ProcessingTree,
    ) -> list[list[str, str, dict]]:
        """
        Get the datasets to be written to the hdf5 file.

        Parameters
        ----------
        node_id : int
            The nodeID.
        scan : pydidas.contexts.Scan
            The scan (context).
        exp : pydidas.contexts.DiffractionExperiment
            The diffraction experiment (context).
        workflow : WorkflowTree
            The workflow tree.

        Returns
        -------
        list[list[str, str, dict, dict]]
            List with the dataset information to be written.
        """

        _node_attribute = partial(cls.get_node_attribute, node_id)
        _dsets = [
            [
                "entry",
                "scan_title",
                {"data": cls.scan_title},
                {"NX_class": "NX_CHAR", "units": ""},
            ],
            [
                "entry",
                "node_id",
                {"data": node_id},
                {"NX_class": "NX_INT", "units": ""},
            ],
            [
                "entry",
                "node_label",
                {"data": _node_attribute("node_label")},
                {"NX_class": "NX_CHAR", "units": ""},
            ],
            [
                "entry",
                "plugin_name",
                {"data": _node_attribute("plugin_name")},
                {"NX_class": "NX_CHAR", "units": ""},
            ],
            [
                "entry",
                "data_label",
                {"data": ""},
                {"NX_class": "NX_CHAR", "units": ""},
            ],
            [
                "entry",
                "data_unit",
                {"data": ""},
                {"NX_class": "NX_CHAR", "units": ""},
            ],
            [
                "entry/data",
                "data",
                {"shape": _node_attribute("shape")},
                {"NX_class": "NX_INT", "units": ""},
            ],
        ] + _get_pydidas_context_config_entries(scan, exp, workflow)
        return _dsets

    @classmethod
    def export_frame_to_file(
        cls,
        index: int,
        frame_result_dict: dict,
        scan_context: Scan | None = None,
        **kwargs: dict,
    ):
        """
        Export the results of one frame and store them on disk.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Scan |None, optional
            The scan context to be used for exporting to file. If None, the
            global scan context will be used. The default is None.
        kwargs : dict
            Any kwargs which should be passed to the underlying exporter.
        """
        _scan = ScanContext() if scan_context is None else scan_context
        _indices = _scan.get_index_position_in_scan(index)
        if not cls._metadata_written:
            cls.update_metadata(frame_result_dict)
        for _node_id, _data in frame_result_dict.items():
            with h5py.File(cls._save_dir / cls._filenames[_node_id], "r+") as _file:
                _file["entry/data/data"][_indices] = _data

    @classmethod
    def export_full_data_to_file(
        cls,
        full_data: dict,
        scan_context: Scan | None = None,
    ):
        """
        Export the full dataset to disk.

        Parameters
        ----------
        full_data : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Scan |None, optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        """
        if not cls._metadata_written:
            cls.update_metadata(full_data)
        for _node_id, _data in full_data.items():
            with h5py.File(cls._save_dir / cls._filenames[_node_id], "r+") as _file:
                _file["entry/data/data"][()] = _data.array

    @classmethod
    def update_metadata(cls, metadata: dict[int, Dataset | dict]):
        """
        Update the frame metadata with a separately supplied metadata
        dictionary.

        Parameters
        ----------
        metadata : dict
            The metadata in dictionary form with entries of the form
            node_id: node_metadata.
        """
        for _id, _metadata in metadata.items():
            if isinstance(_metadata, Dataset):
                _metadata = _metadata.property_dict
            _ndim = len(_metadata["axis_labels"])
            _shape = tuple(_range.size for _range in _metadata["axis_ranges"].values())
            _axes_attr = [f"axis_{_i}_repr" for _i in range(_ndim)]
            with h5py.File(cls._save_dir / cls._filenames[_id], "r+") as _file:
                _file["entry/data_label"][()] = _metadata.get("data_label", "")
                _file["entry/data_unit"][()] = _metadata.get("data_unit", "")
                _nxdata_group = _file["entry/data"]
                _nxdata_group.attrs["signal"] = "data"
                _nxdata_group.attrs["axes"] = _axes_attr
                for _dim in range(_ndim):
                    _nxdata_group.attrs[f"axis_{_dim}_repr_indices"] = [_dim]
                    _create_nxdata_axis_entry(
                        _nxdata_group,
                        _dim,
                        _metadata["axis_labels"][_dim],
                        _metadata["axis_units"][_dim],
                        _metadata["axis_ranges"][_dim],
                    )
        cls._metadata_written = True

    @classmethod
    def import_results_from_file(
        cls, filename: Path | str
    ) -> tuple[Dataset, dict, Scan, DiffractionExperiment, ProcessingTree]:
        """
        Import results from a file and store them as a Dataset.

        Parameters
        ----------
        filename : Path | str
            The full filename of the file to be imported.

        Returns
        -------
        data : pydidas.core.Dataset
            The dataset with the imported data.
        node_info : dict
            A dictionary with node_label, data_label, plugin_name keys and the
            respective values.
        scan : pydidas.contexts.Scan
            The imported scan configuration.
        diffraction_exp : pydidas.contexts.DiffractionExperiment
            The imported diffraction experiment configuration.
        tree : pydidas.workflow.WorkflowTree
            The imported workflow tree.
        """
        _tree = ProcessingTree()
        _scan = Scan()
        _exp = DiffractionExperiment()
        _data = import_data(filename, auto_squeeze=False)
        _scan.import_from_file(filename)
        _exp.import_from_file(filename)
        with h5py.File(filename, "r") as _file:
            try:
                _tree.restore_from_string(
                    read_and_decode_hdf5_dataset(_file["entry/pydidas_config/workflow"])
                )
            except KeyError:
                raise UserConfigError(
                    "The given file does not conform to the pydidas results data "
                    "standard and cannot be imported. Please check the input file."
                )
            _info = {
                "node_label": read_and_decode_hdf5_dataset(_file["entry/node_label"]),
                "plugin_name": read_and_decode_hdf5_dataset(_file["entry/plugin_name"]),
                "node_id": read_and_decode_hdf5_dataset(_file["entry/node_id"]),
            }
            _info["result_title"] = (
                f"{_info['node_label']} (node #{_info['node_id']:03d})"
                if len(_info["node_label"]) > 0
                else f"[{_info['plugin_name']}] (node #{_info['node_id']:03d})"
            )

        _info["shape"] = _data.shape
        return _data, _info, _scan, _exp, _tree
