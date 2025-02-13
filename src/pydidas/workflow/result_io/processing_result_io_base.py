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
Module with the ProcessingResultIoBase class which exporters/importers should
inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResultIoBase"]


import re
from pathlib import Path
from typing import Union

from pydidas.contexts.scan import Scan
from pydidas.core import Dataset
from pydidas.core.io_registry import GenericIoBase
from pydidas.workflow.result_io.processing_result_io_meta import ProcessingResultIoMeta


class ProcessingResultIoBase(GenericIoBase, metaclass=ProcessingResultIoMeta):
    """
    Base class for WorkflowTree exporters.
    """

    extensions = []
    default_extension = ""
    format_name = "unknown"
    scan_title = ""
    _node_information = {}

    @classmethod
    def prepare_files_and_directories(
        cls, save_dir: Union[Path, str], node_information: dict, **kwargs
    ):
        """
        Prepare the required files and directories to write the data to disk.

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
        **kwargs:
            Supported kwargs are:

            scan_context : Union[Scan, None], optional
                The scan context. If None, the generic context will be used.
                Only specify this, if you explicitly require a different context.
                The default is None.
            diffraction_exp_context : Union[DiffractionExp, None], optional
                The diffraction experiment context. If None, the generic context
                will be used. Only specify this, if you explicitly require a
                different context. The default is None.
            workflow_tree : Union[WorkflowTree, None], optional
                The WorkflowTree. If None, the generic WorkflowTree will be used.
                Only specify this, if you explicitly require a different context.
                The default is None.
        """
        raise NotImplementedError

    @classmethod
    def get_attribute_dict(cls, name: str) -> dict:
        """
        Get a dictionary for a single attribute from the combined node informatinon.

        Parameters
        ----------
        name : str
            The name of the attribute to extract.

        Returns
        -------
        dict
            The dictionary with the node IDs and the single attribute values.
        """
        return {_id: _item[name] for _id, _item in cls._node_information.items()}

    @classmethod
    def get_node_attribute(cls, node_id: int, name: str) -> object:
        """
        Get a single node attribute from the stored node information.

        Parameters
        ----------
        node_id : int
            The node number.
        name : str
            The required attribute name.

        Returns
        -------
        type
            The value of the required attribute
        """
        return cls._node_information[node_id][name]

    @classmethod
    def get_filenames_from_labels(cls, labels: Union[dict, None] = None):
        """
        Get the directory names from labels.

        This method will assemble directory names which include the node ID,
        the Plugin label and the format name. Any spaces or escape characters
        will be converted to underscores.

        Parameters
        ----------
        labels : Union[dict, None], optional
            The labels to be used. If labels are not supplied, they will be taken from
            the internally stored node information. The default is None.

        Returns
        -------
        names : dict
            The dictionary of possible directory names.
        """
        _names = {}
        if labels is None:
            labels = cls.get_attribute_dict("node_label")
        for _id, _label in labels.items():
            if _label is None or _label == "":
                _names[_id] = f"node_{_id:02d}.{cls.default_extension}"
            else:
                _label = re.sub("[^a-zA-Z0-9_-]", "_", _label)
                _label = re.sub("_+", "_", _label).strip("_")
                _names[_id] = (
                    f"node_{_id:02d}_{_label}.{cls.default_extension}"
                ).replace("__", "_")
        return _names

    @classmethod
    def export_full_data_to_file(
        cls,
        full_data: dict[int, Dataset],
        scan_context: Union[Scan, None] = None,
    ):
        """
        Export all specified datasets to disk.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each concrete subclass.

        Parameters
        ----------
        full_data : dict
            The result dictionary with nodeID keys and result values.
        scan_context : Union[Scan, None], optional
            The scan context. If None, the generic context will be used. Only specify
            this, if you explicitly require a different context. The default is None.
        """
        raise NotImplementedError

    @classmethod
    def export_frame_to_file(
        cls, index: int, frame_result_dict: dict[int, Dataset], **kwargs: dict
    ):
        """
        Export the results of one frame and store them on disk.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each concrete subclass.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        **kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        raise NotImplementedError

    @classmethod
    def update_frame_metadata(cls, metadata: dict, scan: Union[Scan, None] = None):
        """
        Update the metadata of the individual frame.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each concrete subclass.

        Parameters
        ----------
        metadata : dict
            The metadata dictionary with results of one frame for each node.
        scan : Union[pydidas.contexts.scan.Scan, None], optional
            The Scan instance. If None, this will default to the generic ScanContext.
            The default is None.
        """
        raise NotImplementedError

    @classmethod
    def import_results_from_file(cls, filename: Union[Path, str]):
        """
        Import results from a file and store them as a Dataset.

        Parameters
        ----------
        filename : Union[Path, str]
            The full filename of the file to be imported.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each concrete subclass.

        Returns
        -------
        data : pydidas.core.Dataset
            The dataset with the imported data.
        node_info : dict
            A dictionary with node_label, data_label, plugin_name keys and the
            respective values.
        scan : dict
            The dictionary with meta information about the scan.
        """
        raise NotImplementedError
