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
Module with the WorkflowResultIoMeta class which is used for creating
exporter/importer classes and registering them.

These exporters/importers are used to save the WorkflowTree results to
the specified file formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkflowResultIoMeta"]

import os

from ...core.io_registry import GenericIoMeta
from ...core.utils import get_extension


class WorkflowResultIoMeta(GenericIoMeta):
    """
    Metaclass for WorkflowTree exporters and importers which holds the
    registry with all associated file extensions for exporting WorkflowTrees.
    """

    # need to redefine the registry to have a unique registry for
    # WorkflowResultsSaverMeta
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
    def set_active_savers_and_title(cls, savers, title="unknown"):
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
    def get_filenames_from_active_savers(cls, labels):
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
    def prepare_active_savers(cls, save_dir, node_information):
        """
        Prepare the active savers for storing data by creating the required
        files and directories.

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
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.scan_title = cls.scan_title
            _saver.prepare_files_and_directories(save_dir, node_information)

    @classmethod
    def prepare_saver(cls, extension, save_dir, node_information):
        """
        Call the concrete saver associated with the extension to prepare
        all requird files and directories.

        Parameters
        ----------
        extension : str
            The extension of the saved files.
        save_dir : Union[pathlib.Path, str]
            The full path for the data to be saved.
        node_information : dict
            A dictionary with nodeID keys and dictionary values. Each value dictionary
            must have the following keys: shape, node_label, data_label, plugin_name
            and the respecive values. The shape (tuple) detemines the shape of the
            Dataset, the node_label is the user's name for the processing node. The
            data_label gives the description of what the data shows (e.g. intensity)
            and the plugin_name is simply the name of the plugin.
        """
        cls.verify_extension_is_registered(extension)
        _saver = cls.registry[extension]
        _saver.prepare_files_and_directories(save_dir, node_information)

    @classmethod
    def push_frame_metadata_to_active_savers(cls, metadata):
        """
        Push the frame metadata to all active savers.

        This method is required if the ExecuteWorkflowApp is used with the
        AppRunner because the metadata cannot be transferred through the
        shared numpy.buffers and needs to be forwarded independently of the
        frame data.

        Parameters
        ----------
        metadata : dict
            The dictionary with the metadata.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.update_frame_metadata(metadata)

    @classmethod
    def export_frame_to_active_savers(cls, index, frame_result_dict, **kwargs):
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
    def export_full_data_to_active_savers(cls, data):
        """
        Export the full data to all active savers.

        Parameters
        ----------
        data : dict
            The result dictionary with nodeID keys and result values.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.export_full_data_to_file(data)

    @classmethod
    def export_full_data_to_file(cls, extension, data):
        """
        Export the full data to all active savers.

        Parameters
        ----------
        extension : str
            The file extension for the saver.
        data : dict
            The result dictionary with nodeID keys and result values.
        """
        cls.verify_extension_is_registered(extension)
        _saver = cls.registry[extension]
        _saver.export_full_data_to_file(data)

    @classmethod
    def export_frame_to_file(cls, index, extension, frame_result_dict, **kwargs):
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
    def import_data_from_directory(cls, dirname):
        """
        Import data from files in a directory and pass it in a format for the
        WorkflowResults to update itself.

        Parameters
        ----------
        dirname : Union[pathlib.Path, str]
            The name of the directory from which data shall be imported.

        Returns
        -------
        data_dict : dict
            The dictionary with the data. Keys are the respective node IDs and dict
            values is the imported data.
        node_info_dict : dict
            The dictionary with information for all imported nodes.
        scan : dict
            The dictionary with information about the Scan.
        """
        _data_dict = {}
        _node_info_dict = {}
        _scan = {}
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
            _data, _node_info, _scan = _importer.import_results_from_file(_path)
            _data_dict[_node_id] = _data
            _node_info_dict[_node_id] = _node_info
        return _data_dict, _node_info_dict, _scan