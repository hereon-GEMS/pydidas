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
Module with the ProcessingResultIoMeta class which is used for creating
exporter/importer classes and registering them.

These exporters/importers are used to save the WorkflowTree results to
the specified file formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResultIoMeta"]


import os
from pathlib import Path
from typing import Union

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import Dataset
from pydidas.core.io_registry import GenericIoMeta
from pydidas.core.utils import get_extension
from pydidas.workflow.processing_tree import ProcessingTree


class ProcessingResultIoMeta(GenericIoMeta):
    """
    Metaclass for WorkflowTree exporters and importers which holds the
    registry with all associated file extensions for exporting WorkflowTrees.
    """

    # need to redefine the registry to have a unique registry for
    # ProcessingResultsSaverMeta
    registry = {}
    active_savers = []
    scan_title = ""

    @classmethod
    def reset(cls):
        """
        Reset the Meta registry and clear all entries.
        """
        cls.registry = {}
        cls.active_savers = []

    @classmethod
    def set_active_savers_and_title(cls, savers: list[str], title: str = "unknown"):
        """
        Set the active savers so they do not need to be specified individually
        later on.

        Parameters
        ----------
        savers : list
            A list of the names of the savers. "None" is a valid Saver to
            clear the list.
        title : str, optional
            The title of the scan. If not provided, the title will default to
            "unknown".
        """
        cls.active_savers = []
        cls.scan_title = title
        for _saver in savers:
            if not (_saver is None or _saver == "None"):
                cls.verify_extension_is_registered(_saver)
                if _saver not in cls.active_savers:
                    cls.active_savers.append(_saver)

    @classmethod
    def get_filenames_from_active_savers(cls, labels: dict) -> list[dict]:
        """
        Get the filenames from all active savers based on the supplied labels.

        Parameters
        ----------
        labels : dict
            The labels of the results in form of a dictionary with nodeID
            keys and label values.

        Returns
        -------
        list
            A list will all filenames for all selected nodes and exporters.
        """
        _names = []
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _fnames = _saver.get_filenames_from_labels(labels)
            for _name in _fnames.values():
                _names.append(_name)
        return _names

    @classmethod
    def prepare_active_savers(
        cls,
        save_dir: Union[Path, str],
        node_information: dict,
        scan_context: Union[Scan, None] = None,
        diffraction_exp: Union[DiffractionExperiment, None] = None,
        workflow_tree: Union[ProcessingTree, None] = None,
    ):
        """
        Prepare the active savers for storing data.

        This method creates the required files and directories.

        Parameters
        ----------
        save_dir : Union[Path, str]
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
        diffraction_exp : Union[DiffractionExp, None], optional
            The diffraction experiment context. If None, the generic context will be
            used. Only specify this, if you explicitly require a different context. The
            default is None.
        workflow_tree : Union[WorkflowTree, None], optional
            The WorkflowTree. If None, the generic WorkflowTree will be used. Only
            specify this, if you explicitly require a different context. The default is
            None.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.scan_title = cls.scan_title
            _saver.prepare_files_and_directories(
                save_dir,
                node_information,
                scan_context=scan_context,
                diffraction_exp_context=diffraction_exp,
                workflow_tree=workflow_tree,
            )

    @classmethod
    def push_metadata_to_active_savers(
        cls, metadata: dict, scan: Union[Scan, None] = None
    ):
        """
        Push the metadata to all active savers.

        This method is required if the ExecuteWorkflowApp is used with the
        AppRunner because the metadata cannot be transferred through the
        shared numpy.buffers and needs to be forwarded independently of the
        frame data.

        Parameters
        ----------
        metadata : dict
            The dictionary with the metadata.
        scan : Union[Scan, None], optional
            The Scan instance. If None, this will default to the generic ScanContext.
            The default is None.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.update_metadata(metadata, scan)

    @classmethod
    def export_frame_to_active_savers(
        cls, index: int, frame_result_dict: dict, **kwargs: dict
    ):
        """
        Export the results of a frame to all active savers.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.export_frame_to_file(index, frame_result_dict, **kwargs)

    @classmethod
    def export_full_data_to_active_savers(
        cls, data: dict[int, Dataset], scan_context: Union[Scan, None] = None
    ):
        """
        Export the full data to all active savers.

        Parameters
        ----------
        data : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Union[Scan, None], optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.export_full_data_to_file(data, scan_context)

    @classmethod
    def export_full_data_to_file(
        cls,
        extension: str,
        data: dict[int, Dataset],
        scan_context: Union[Scan, None] = None,
    ):
        """
        Export the full data to all active savers.

        Parameters
        ----------
        extension : str
            The file extension for the saver.
        data : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Union[Scan, None], optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        """
        cls.verify_extension_is_registered(extension)
        _saver = cls.registry[extension]
        _saver.export_full_data_to_file(data, scan_context)

    @classmethod
    def export_frame_to_file(
        cls,
        index: int,
        extension: str,
        frame_result_dict: dict[int, Dataset],
        **kwargs: dict,
    ):
        """
        Call the concrete export_to_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        index : int
            The frame index.
        extension : str
            The file extension for the saver.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        cls.verify_extension_is_registered(extension)
        _saver = cls.registry[extension]
        _saver.export_frame_to_file(index, frame_result_dict, **kwargs)

    @classmethod
    def import_data_from_directory(
        cls, dirname: Union[Path, str]
    ) -> tuple[dict[int, Dataset], dict, Scan, DiffractionExperiment, ProcessingTree]:
        """
        Import data from files in a directory.

        This method imports data, reads the metadata and passes it in a format for
        the ProcessingResults to update itself.

        Parameters
        ----------
        dirname : Union[Path, str]
            The name of the directory from which data shall be imported.

        Returns
        -------
        data_dict : dict
            The dictionary with the data. Keys are the respective node IDs and dict
            values is the imported data.
        node_info_dict : dict
            The dictionary with information for all imported nodes.
        scan : Scan
            A pydidas Scan instance with the scan's context
        exp: DiffractionExperiment
            A pydidas DiffractionExperiment instance with the experiment's context
        tree : WorkflowTree
            A pydidas WorkflowTree instance with the workflow's context
        """
        _data_dict = {}
        _node_info_dict = {}
        _scan = Scan()
        _exp = DiffractionExperiment()
        _tree = ProcessingTree()
        _files = [
            _file
            for _file in os.listdir(dirname)
            if (
                os.path.isfile(os.path.join(dirname, _file))
                and _file.startswith("node_")
            )
        ]
        for _file in _files:
            _ext = get_extension(_file)
            cls.verify_extension_is_registered(_ext)
            _importer = cls.registry[_ext]
            _node_id = int(_file[5:7])
            _path = os.path.join(dirname, _file)
            _data, _node_info, _scan, _exp, _tree = _importer.import_results_from_file(
                _path
            )
            _data_dict[_node_id] = _data
            _node_info_dict[_node_id] = _node_info
        return _data_dict, _node_info_dict, _scan, _exp, _tree
