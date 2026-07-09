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
Module with the ProcessingResultIoMeta class which is used for creating
exporter/importer classes and registering them.

These exporters/importers are used to save the WorkflowTree results to
the specified file formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResultIoMeta"]


import os
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import Dataset
from pydidas.core.io_registry import GenericIoMeta
from pydidas.core.utils import get_extension
from pydidas.workflow.processing_tree import ProcessingTree


if TYPE_CHECKING:
    from pydidas.workflow.result_io import ProcessingResultIoBase


class ProcessingResultIoMeta(GenericIoMeta):
    """
    Metaclass for ProcessingResult exporters and importers which holds the
    registry with all associated file extensions for exporting ProcessingResults.
    """

    registry: ClassVar[dict[str, type["ProcessingResultIoBase"]]] = {}

    @staticmethod
    def get_savers(
        formats: str | list[str] | None = None,
    ) -> dict[str, "ProcessingResultIoBase"]:
        """
        Get the savers based on the selected formats.

        Parameters
        ----------
        formats : str or list[str] or None
            A single string with the name of the format or a list of names
            of the formats. None is a valid format to get an empty dictionary.
            Multiple formats can also be given as a single string if they are
            separated by a semicolon `;`.

        Returns
        -------
        dict[str, ProcessingResultIoBase]
            The dictionary with the active savers. Keys are the file extensions
            and values are the respective saver instances.
        """
        _active_savers: dict[str, "ProcessingResultIoBase"] = {}
        _current_savers: list[type["ProcessingResultIoBase"]] = []
        if formats is None or formats == "":
            return _active_savers
        if isinstance(formats, str):
            formats = formats.split(";")
        for _format in formats:
            _format = _format.lower().strip()
            if not _format.startswith("."):
                _format = "." + _format
            if not (_format is None or _format == "none"):
                ProcessingResultIoMeta.verify_extension_is_registered(_format)
                _format_cls = ProcessingResultIoMeta.registry[_format]
                if _format_cls not in _current_savers:
                    _active_savers[_format] = _format_cls()
                    _current_savers.append(_format_cls)
        return _active_savers

    @staticmethod
    def import_data_from_directory(
        dir_name: Path | str,
    ) -> tuple[dict[int, Dataset], dict, Scan, DiffractionExperiment, ProcessingTree]:
        """
        Import data from files in a directory.

        This method imports data, reads the metadata and passes it in a format for
        the ProcessingResults to update it

        Parameters
        ----------
        dir_name : Path or String
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
        tree : ProcessingTree
            A pydidas ProcessingTree instance (i.e. possibly also the
            WorkflowTree) with the workflow configuration.
        """
        _data_dict = {}
        _node_info_dict = {}
        _scan = Scan()
        _exp = DiffractionExperiment()
        _tree = ProcessingTree()
        dir_name = Path(dir_name)
        _files = [
            _file
            for _file in os.listdir(dir_name)
            if (dir_name / _file).exists() and _file.startswith("node_")
        ]
        for _file in _files:
            _ext = get_extension(_file)
            ProcessingResultIoMeta.verify_extension_is_registered(_ext)
            _importer = ProcessingResultIoMeta.registry[_ext]
            _node_id = int(_file[5:7])
            _path = dir_name / _file
            _data, _node_info, _scan, _exp, _tree = _importer.import_results_from_file(
                _path
            )
            _data_dict[_node_id] = _data
            _node_info_dict[_node_id] = _node_info
        return _data_dict, _node_info_dict, _scan, _exp, _tree
