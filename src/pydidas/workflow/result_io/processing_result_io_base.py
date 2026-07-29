# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResultIoBase"]


import re
from pathlib import Path
from typing import Any, ClassVar

from pydidas.contexts import (
    DiffractionExperiment,
    DiffractionExperimentContext,
    Scan,
    ScanContext,
)
from pydidas.core import Dataset
from pydidas.core.io_registry import GenericIoBase
from pydidas.plugins.plugin_result_info import PluginResultInfo
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io.processing_result_io_meta import ProcessingResultIoMeta
from pydidas.workflow.workflow_tree import WorkflowTree


class ProcessingResultIoBase(GenericIoBase, metaclass=ProcessingResultIoMeta):
    """
    Base class for processing result importers and exporters.
    """

    extensions: ClassVar[list[str]] = []
    default_suffix: ClassVar[str] = ""
    format_name: ClassVar[str] = ""

    def __init__(self):
        self._config: dict[str, Any] = {}

    def prepare_files_and_directories(
        self,
        save_dir: Path | str,
        node_information: dict[int, PluginResultInfo],
        **kwargs: Any,
    ) -> None:
        """
        Prepare the required files and directories to write the data to disk.

        Parameters
        ----------
        save_dir : Path or str
            The full path for the data to be saved.
        node_information : dict[int, PluginResultInfo]
            A dictionary with nodeID keys and PluginResultInfo values.
        **kwargs:
            Supported kwargs are:

            scan : Scan or None, optional
                The scan context. If None, the generic context will be used.
                Only specify this, if you explicitly require a different context.
                The default is None.
            diffraction_exp : DiffractionExp or None, optional
                The diffraction experiment context. If None, the generic context
                will be used. Only specify this, if you explicitly require a
                different context. The default is None.
            processing_tree : ProcessingTree or None, optional
                The ProcessingTree. If None, the generic WorkflowTree will be
                used. Only specify this, if you explicitly require a different
                context. The default is None.
        """
        _save_dir = Path(save_dir)
        if not _save_dir.exists():
            _save_dir.mkdir(parents=True)
        self._config["save_dir"] = _save_dir
        self._config["filenames"] = {
            _node_id: _save_dir / _fname
            for _node_id, _fname in self.get_filenames(node_information).items()
        }
        self._config["scan"] = kwargs.get("scan", ScanContext())
        self._config["diffraction_exp"] = kwargs.get(
            "diffraction_exp", DiffractionExperimentContext()
        )
        self._config["processing_tree"] = kwargs.get("processing_tree", WorkflowTree())

    def get_filenames(
        self, node_information: dict[int, PluginResultInfo]
    ) -> dict[int, str]:
        """
        Get the directory names from labels.

        This method will assemble directory names which include the node ID,
        the Plugin label and the format name. Any spaces or escape characters
        will be converted to underscores.

        Parameters
        ----------
        node_information : dict[int, PluginResultInfo]
            A dictionary with nodeID keys and PluginResultInfo values.

        Returns
        -------
        names : dict[int, str]
            The dictionary of filenames for all nodes to export.
        """
        _names = {}
        for _id, _node in node_information.items():
            _label = _node.label
            if _label is None or _label == "":
                _names[_id] = f"node_{_id:02d}{self.default_suffix}"
            else:
                _label = re.sub("[^a-zA-Z0-9_-]", "_", _label)
                _label = re.sub("_+", "_", _label.strip("_"))
                _name = f"node_{_id:02d}_{_label}{self.default_suffix}"
                _names[_id] = _name
        return _names

    def export_full_data_to_file(
        self,
        full_data: dict[int, Dataset],
        squeeze: bool = False,
    ) -> None:
        """
        Export all specified datasets to disk.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each concrete subclass.

        Parameters
        ----------
        full_data : dict[int, Dataset]
            The result dictionary with nodeID keys and result values.
        squeeze : bool, optional
            Flag to toggle squeezing of the data. If True, any empty dimensions will
            be squeezed from the data. The default is False.
        """
        raise NotImplementedError

    def export_frame_to_file(
        self,
        index: int,
        frame_result_dict: dict[int, Dataset],
        **kwargs: Any,
    ) -> None:
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
        frame_result_dict : dict[int, Dataset]
            The result dictionary with nodeID keys and result values.
        **kwargs
            Any kwargs which should be passed to the underlying exporter.
        """
        raise NotImplementedError

    def update_result_metadata(
        self, result_metadata: dict[int, dict[str, Any]] | dict[int, Dataset]
    ) -> None:
        """
        Update the result metadata of the individual frame.

        Parameters
        ----------
        result_metadata : dict[int, dict[str, Any]] or dict[int, Dataset]
            The metadata dictionary with results of one frame for each node.
        """
        raise NotImplementedError

    @staticmethod
    def import_results_from_file(
        filename: Path | str,
    ) -> tuple[Dataset, dict[str, Any], Scan, DiffractionExperiment, ProcessingTree]:
        """
        Import results from a file and store them as a Dataset.

        Parameters
        ----------
        filename : Path or str
            The full filename of the file to be imported.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by each concrete subclass.

        Returns
        -------
        data : pydidas.core.Dataset
            The dataset with the imported data.
        node_info : dict[str, Any]
            A dictionary with node_label, data_label, plugin_name keys and
            the respective values.
        scan : Scan
            The imported scan configuration.
        diffraction_exp : DiffractionExperiment
            The imported diffraction experiment configuration.
        tree : ProcessingTree
            The imported processing tree.
        """
        raise NotImplementedError
