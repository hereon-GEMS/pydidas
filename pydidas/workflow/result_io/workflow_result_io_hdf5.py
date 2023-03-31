# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the WorkflowResultIoHdf5 class which exports and imports results in
Hdf5 file format.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkflowResultIoHdf5"]

import os
from functools import partial

import h5py

from ... import version
from ...contexts import DiffractionExperimentContext, ScanContext
from ...contexts.diffraction_exp_context import DiffractionExperiment
from ...contexts.scan_context import Scan
from ...core import Dataset
from ...core.constants import HDF5_EXTENSIONS
from ...core.utils import create_hdf5_dataset, read_and_decode_hdf5_dataset
from ..workflow_tree import WorkflowTree, _WorkflowTree
from .workflow_result_io_base import WorkflowResultIoBase


def get_detector_metadata_entries(scan, exp):
    """
    Get the metadata for the detector.

    Parameters
    ----------
    scan : Scan
        The scan context.
    exp : DiffractionExp
        The diffraction experiment context.

    Returns
    -------
    list
        List with entries of all metadata to be written.
    """
    return [
        [
            "entry/instrument/detector",
            "frame_start_number",
            {"data": scan.get_param_value("scan_start_index")},
        ],
        [
            "entry/instrument/detector",
            "x_pixel_size",
            {"data": exp.get_param_value("detector_pxsizex")},
        ],
        [
            "entry/instrument/detector",
            "y_pixel_size",
            {"data": exp.get_param_value("detector_pxsizey")},
        ],
        [
            "entry/instrument/detector",
            "distance",
            {"data": exp.get_param_value("detector_dist")},
        ],
    ]


def get_pydidas_context_config_entries(scan, exp, tree):
    """
    Get the context configuration from the pydidas Context singletons.

    Parameters
    ----------
    scan : Scan
        The scan context.
    exp : DiffractionExp
        The diffraction experiment context.
    tree : WorkflowTree
        The workflow tree.

    Returns
    -------
    list
        List with writable entries for the contexts.
    """
    _dsets = []
    for _key, _value in scan.get_param_values_as_dict(True).items():
        _dsets.append(["entry/pydidas_config/scan", _key, {"data": _value}])
    for _key, _value in exp.get_param_values_as_dict(True).items():
        _dsets.append(["entry/pydidas_config/diffraction_exp", _key, {"data": _value}])
    _dsets.append(
        ["entry/pydidas_config", "workflow", {"data": tree.export_to_string()}]
    )
    _dsets.append(
        ["entry/pydidas_config", "pydidas_version", {"data": version.version}]
    )
    return _dsets


class WorkflowResultIoHdf5(WorkflowResultIoBase):
    """
    Implementation of the WorkflowResultIoBase for Hdf5 files.
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"
    default_extension = "h5"
    _filenames = []
    _save_dir = None
    _metadata_written = False

    @classmethod
    def prepare_files_and_directories(cls, save_dir, node_information, **kwargs):
        """
        Prepare the hdf5 files with the metadata.

        Parameters
        ----------
        save_dir : Union[pathlib.Path, str]
            The full path for the data to be saved.
        node_information : dict
            A dictionary with nodeID keys and dictionary values. Each value dictionary
            must have the following keys: shape, node_label, data_label, plugin_name
            and the respecive values. The shape (tuple) detemines the shape of the
            Dataset, the node_label is the user's name for the processing node. The
            data_label gives the description of what the data shows (e.g. intensity)
            and the plugin_name is simply the name of the plugin.
        scan_context : Union[Scan, None], optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        diffraction_exp_context : Union[DiffractionExp, None], optional
            The diffraction experiment context. If None, the generic context will be
            used. Only specify this, if you explicitly require a different context. The
            default is None.
        workflow_tree : Union[WorkflowTree, None], optional
            The WorkflowTree. If None, the generic WorkflowTree will be used. Only
            specify this, if you explicitly require a different context. The default is
            None.
        """
        _scan = kwargs.get("scan_context", ScanContext())
        _exp = kwargs.get("diffraction_exp_context", DiffractionExperimentContext())
        _tree = kwargs.get("workflow_tree", WorkflowTree())
        cls._save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        cls._node_information = node_information
        cls._filenames = cls.get_filenames_from_labels()
        cls._metadata_written = False
        for _index in cls._node_information.keys():
            cls._create_file_and_populate_metadata(_index, _scan, _exp, _tree)

    @classmethod
    def _create_file_and_populate_metadata(cls, node_id, scan, exp, workflow):
        """
        Create a hdf5 file and populate it with the Scan metadata.

        Parameters
        ----------
        node_id : int
            The nodeID.
        scan : Scan
            The scan context.
        exp : DiffractionExperiment
            The diffraction experiment context.
        workflow : WorkflowTree
            The workflow.
        """
        _node_attribute = partial(cls.get_node_attribute, node_id)
        _dsets = [
            ["entry", "scan_title", {"data": cls.scan_title}],
            ["entry", "node_id", {"data": node_id}],
            ["entry", "node_label", {"data": _node_attribute("node_label")}],
            ["entry", "plugin_name", {"data": _node_attribute("plugin_name")}],
            ["entry", "data_label", {"data": _node_attribute("data_label")}],
            ["entry", "data_unit", {"data": _node_attribute("data_unit")}],
            ["entry/data", "data", {"shape": _node_attribute("shape")}],
        ]
        _dsets.extend(get_detector_metadata_entries(scan, exp))
        _dsets.extend(get_pydidas_context_config_entries(scan, exp, workflow))
        with h5py.File(
            os.path.join(cls._save_dir, cls._filenames[node_id]), "w"
        ) as _file:
            for _group, _name, kws in _dsets:
                create_hdf5_dataset(_file, _group, _name, **kws)
            for _dim in range(scan.get_param_value("scan_dim")):
                _file[f"entry/data/axis_{_dim}"] = h5py.SoftLink(
                    f"/entry/scan/dim_{_dim}"
                )

    @classmethod
    def export_frame_to_file(
        cls, index, frame_result_dict, scan_context=None, **kwargs
    ):
        """
        Export the results of one frame and store them on disk.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Union[Scan, None], optional
            The scan context to be used for exporting to file.
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        _scan = ScanContext() if scan_context is None else scan_context
        _indices = _scan.get_frame_position_in_scan(index)
        if not cls._metadata_written:
            cls.write_metadata_to_files(frame_result_dict, _scan)
        for _node_id, _data in frame_result_dict.items():
            _fname = os.path.join(cls._save_dir, cls._filenames[_node_id])
            with h5py.File(_fname, "r+") as _file:
                _file["entry/data/data"][_indices] = _data

    @classmethod
    def export_full_data_to_file(
        cls,
        full_data,
        scan_context=None,
    ):
        """
        Export the full dataset to disk.

        Parameters
        ----------
        full_data : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Union[Scan, None], optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        """
        _scan = ScanContext() if scan_context is None else scan_context

        if not cls._metadata_written:
            _indices = _scan.get_frame_position_in_scan(0)
            cls.write_metadata_to_files(
                {_id: _data[_indices] for _id, _data in full_data.items()}, _scan
            )
        for _node_id, _data in full_data.items():
            _fname = os.path.join(cls._save_dir, cls._filenames[_node_id])
            with h5py.File(_fname, "r+") as _file:
                _file["entry/data/data"][()] = _data.array

    @classmethod
    def write_metadata_to_files(cls, frame_result_dict, scan):
        """
        Write the metadata from the WorkflowTree to the individual files
        for each node.

        Parameters
        ----------
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Union[Scan, None], optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        """
        for _node_id, _data in frame_result_dict.items():
            cls.update_node_metadata(_node_id, _data, scan)
        cls._metadata_written = True

    @classmethod
    def update_node_metadata(cls, index, data, scan):
        """
        Update the metadata for a single node.

        Parameters
        ----------
        index : int
            The nodeID.
        data : pydidas.core.Dataset
            The processed Dataset.
        scan : Union[Scan, None], optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        """
        _ndim = scan.get_param_value("scan_dim")
        with h5py.File(
            os.path.join(cls._save_dir, cls._filenames[index]), "r+"
        ) as _file:
            for _dim in range(data.ndim):
                _group = _file["entry/data"]
                _axisgroup = _group.create_group(f"axis_{_dim + _ndim}")
                for _key in ["label", "unit", "range"]:
                    _dict = getattr(data, f"axis_{_key}s")
                    create_hdf5_dataset(_axisgroup, None, _key, data=_dict[_dim])

    @classmethod
    def update_frame_metadata(cls, metadata, scan=None):
        """
        Update the frame metadata with a separately supplied metadata
        dictionary.

        Parameters
        ----------
        metadata : dict
            The metadata in dictionary form with entries of the form
            node_id: node_metadata.
        scan : Union[pydidas.contexts.scan_context.Scan, None], optional
            The Scan instance. If None, this will default to the generic ScanContext.
            The default is None.
        """
        _scan = ScanContext() if scan is None else scan
        _ndim = _scan.get_param_value("scan_dim")
        for _id, _metadata in metadata.items():
            with h5py.File(
                os.path.join(cls._save_dir, cls._filenames[_id]), "r+"
            ) as _file:
                _ndim_frame = len(_metadata["axis_labels"])
                for _dim in range(_ndim_frame):
                    _group = _file["entry/data"]
                    _axisgroup = _group.create_group(f"axis_{_dim + _ndim}")
                    for _key in ["label", "unit", "range"]:
                        _val = _metadata[f"axis_{_key}s"][_dim]
                        _val = "None" if _val is None else _val
                        _axisgroup.create_dataset(_key, data=_val)
        cls._metadata_written = True

    @classmethod
    def import_results_from_file(cls, filename):
        """
        Import results from a file and store them as a Dataset.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The full filename of the file to be imported.

        Returns
        -------
        data : pydidas.core.Dataset
            The dataset with the imported data.
        node_info : dict
            A dictionary with node_label, data_label, plugin_name keys and the
            respective values.
        scan : pydidas.contexts.scan_context.Scan
            The imported scan context.
        diffraction_exp : pydidas.contexts.diffraction_exp.DiffractionExp
            The inported diffraction experiment context.
        tree : pydidas.workflow.WorkflowTree
            The imported workflow tree.
        """
        _tree = _WorkflowTree()
        _scan = Scan()
        _exp = DiffractionExperiment()
        with h5py.File(filename, "r") as _file:
            for _key, _param in _exp.params.items():
                _exp.set_param_value(
                    _key,
                    read_and_decode_hdf5_dataset(
                        _file[f"entry/pydidas_config/diffraction_exp/{_key}"]
                    ),
                )
            for _key, _param in _scan.params.items():
                _scan.set_param_value(
                    _key,
                    read_and_decode_hdf5_dataset(
                        _file[f"entry/pydidas_config/scan/{_key}"]
                    ),
                )
            _tree.restore_from_string(
                read_and_decode_hdf5_dataset(_file["entry/pydidas_config/workflow"])
            )

            _data = Dataset(_file["entry/data/data"][()])
            _info = {
                "node_label": read_and_decode_hdf5_dataset(_file["entry/node_label"]),
                "data_label": read_and_decode_hdf5_dataset(_file["entry/data_label"]),
                "data_unit": read_and_decode_hdf5_dataset(_file["entry/data_unit"]),
                "plugin_name": read_and_decode_hdf5_dataset(_file["entry/plugin_name"]),
                "node_id": read_and_decode_hdf5_dataset(_file["entry/node_id"]),
            }
            _info["result_title"] = (
                f"{_info['node_label']} (node #{_info['node_id']:03d})"
                if len(_info["node_label"]) > 0
                else f"[{_info['plugin_name']}] (node #{_info['node_id']:03d})"
            )
            _axlabels = []
            _axunits = []
            _axranges = []
            for _dim in range(_data.ndim):
                _rangeentry = read_and_decode_hdf5_dataset(
                    _file[f"entry/data/axis_{_dim}/range"], return_dataset=False
                )
                _axranges.append(
                    None
                    if (isinstance(_rangeentry, bytes) and _rangeentry == b"::None::")
                    else _rangeentry
                )
                _axunits.append(
                    read_and_decode_hdf5_dataset(_file[f"entry/data/axis_{_dim}/unit"])
                )
                _axlabels.append(
                    read_and_decode_hdf5_dataset(_file[f"entry/data/axis_{_dim}/label"])
                )
        _data.axis_units = _axunits
        _data.axis_labels = _axlabels
        _data.axis_ranges = _axranges
        _data.data_label = _info["data_label"]
        _data.data_unit = _info["data_unit"]
        _info["shape"] = _data.shape
        return _data, _info, _scan, _exp, _tree
