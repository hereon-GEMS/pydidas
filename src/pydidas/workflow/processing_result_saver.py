# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
Module with the ProcessingResultSaver class which handles the saving
of ProcessingTree results to files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResultSaver"]


from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import Dataset
from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.plugins.plugin_result_info import PluginResultInfo
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io import ProcessingResultIoMeta


if TYPE_CHECKING:
    from pydidas.workflow.result_io import ProcessingResultIoBase


class ProcessingResultSaver(ObjectWithParameterCollection):
    """
    A class which handles the saving of ProcessingTree results.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._active_savers: dict[str, ProcessingResultIoBase] = {}
        self._config["savers_ready"] = False

    @property
    def current_formats(self) -> list[str]:
        """
        Get the list of currently active formats.

        Returns
        -------
        list[str]
            The list of currently active formats.
        """
        return list(self._active_savers.keys())

    def set_active_savers(self, formats: str | list[str] | None) -> None:
        """
        Set the active savers so they do not need to be specified individually
        later on.

        Parameters
        ----------
        formats : str or list[str] or None
            A single string with the name of the saver or a list of names
            of the savers. None is a valid Saver to clear the list.
            Multiple savers can also be given as a single string if they are
            separated by a semicolon `;`.
        """
        self._config["savers_ready"] = False
        self._active_savers = ProcessingResultIoMeta.get_savers(formats)

    def expected_export_filenames(
        self, node_info: dict[int, PluginResultInfo]
    ) -> list[str]:
        """
        Get the filenames from all active savers based on the supplied labels.

        Parameters
        ----------
        config : dict[str, Any]
            The configuration of the active savers.
        node_info : dict[int, PluginResultInfo]
            The information about the node results.

        Returns
        -------
        list[str]
            A list will all filenames for all selected nodes and exporters.
        """
        _names = []
        for _saver in self._active_savers.values():
            _fnames = _saver.get_filenames(node_info)
            _names.extend(_name for _name in _fnames.values())
        return _names

    def prepare_active_savers(
        self,
        save_dir: str | Path,
        node_information: dict[int, PluginResultInfo],
        scan: Scan | None = None,
        diffraction_exp: DiffractionExperiment | None = None,
        processing_tree: ProcessingTree | None = None,
    ) -> None:
        """
        Prepare the active savers for storing data.

        Parameters
        ----------
        save_dir : Path or str
            The full path for the data to be saved.
        node_information : dict[int, PluginResultInfo]
            A dictionary with nodeID keys and PluginResultInfo values.
        scan : Scan or None, optional
            The scan context. If None, the generic context will be used. Only
            specify this, if you explicitly require a different context.
            The default is None.
        diffraction_exp : DiffractionExp or None, optional
            The diffraction experiment context. If None, the generic context
            will be used. Only specify this, if you explicitly require a
            different context. The default is None.
        processing_tree : ProcessingTree or None, optional
            The ProcessingTree. If None, the generic WorkflowTree will be used.
            Only specify this, if you explicitly require a different context.
            The default is None.
        """
        self._config["save_dir"] = Path(save_dir)
        for _saver in self._active_savers.values():
            _saver.prepare_files_and_directories(
                self._config["save_dir"],
                node_information,
                scan=scan,
                diffraction_exp=diffraction_exp,
                processing_tree=processing_tree,
            )
        self._config["savers_ready"] = True

    def update_saver_metadata(
        self,
        result_metadata: dict[int, dict[str, Any]],
    ):
        """
        Push the metadata to all active savers.

        This method is required if the ExecuteWorkflowApp is used with the
        AppRunner because the metadata cannot be transferred through the
        shared numpy.buffers and needs to be forwarded independently of the
        frame data.

        Parameters
        ----------
        result_metadata : dict[int, dict[str, Any]]
            The dictionary with the metadata for each node. Keys are plugin
            node keys and results are dictionaries with metadata keys and
            values.
        """
        for _saver in self._active_savers.values():
            _saver.update_result_metadata(result_metadata)

    def export_frame_to_active_savers(
        self, index: int, frame_result_dict: dict[int, Dataset], **kwargs: Any
    ):
        """
        Export the results of a frame to all active savers.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict[int, Dataset]
            The result dictionary with nodeID keys and result values.
        kwargs : Any
            Any kwargs which should be passed to the underlying exporter.
        """
        for _saver in self._active_savers.values():
            _saver.export_frame_to_file(index, frame_result_dict, **kwargs)

    def export_full_data_to_active_savers(
        self,
        data: dict[int, Dataset],
        squeeze: bool = False,
    ):
        """
        Export the full data to all active savers.

        Parameters
        ----------
        data : dict[int, Dataset]
            The result dictionary with nodeID keys and result values.
        squeeze : bool, optional
            Flag to toggle squeezing of the data. If True, any dimension
            of size one will be squeezed from the data. The default is False.
        """
        for _saver in self._active_savers.values():
            _saver.export_full_data_to_file(data, squeeze=squeeze)
