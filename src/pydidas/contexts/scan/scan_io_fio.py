# This file is part of pydidas.
#
# Copyright 2024-2026, Helmholtz-Zentrum Hereon
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
Module with the ScanIoFio class which is used to import scan axes from fio file(s).
"""

__author__ = "Ilia Petrov, Malte Storm"
__copyright__ = "Copyright 2024-2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoFio"]


import os
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError


_ERROR_TEXT_MULTIPLE_SCAN_COMMANDS = (
    "Multiple scan commands found in FIO file. Please check "
    "the file and try again with a correct file."
)
_D0 = "scan_dim0"
_D1 = "scan_dim1"


class ScanIoFio(ScanIoBase):
    """
    FIO importer/exporter for Scan objects.
    """

    extensions = ["fio"]
    format_name = "Sardana FIO"
    beamline_format = True
    import_only = True

    @classmethod
    def check_file_list(
        cls, filenames: Sequence[Path | str], **kwargs: Any
    ) -> list[str]:
        """
        Check if the given list of files is valid for import.

        The return values are a coded message plus any additional information.

        Parameters
        ----------
        filenames : Sequence[Path or str]
            The list of filenames to be checked.
        **kwargs : Any
            Additional keyword arguments. Please refer to _import_multiple_fio
            for the supported keys.

        Returns
        -------
        list[str]
            The error message and additional information.
        """
        if len(filenames) == 1:
            return ["::no_error::"]
        _scan = kwargs.get("scan") or ScanContext()
        _params, _motor_pos, _motor_names = cls._process_fio_file_list(filenames)
        _index_moved_motors = cls._get_moved_motor_indices(
            _motor_pos, _motor_names, _params
        )
        if len(_index_moved_motors) == 0:
            return ["::no_motor_moved::", "No motor has moved between scans."]
        if len(_index_moved_motors) == 1:
            return ["::no_error::"]
        # last case: len(_index_moved_motors) > 1:
        return ["::multiple_motors::"] + [
            _motor_names[_i] for _i in _index_moved_motors
        ]

    @classmethod
    def import_from_file(  # type: ignore[override]
        cls, filename: Path | str, **kwargs: Any
    ) -> None:
        """
        Import scan metadata from a single or multiple fio files.

        Parameters
        ----------
        filename : Path or str or list[Path or str]
            The filename(s) of the file(s) to be imported. Filenames can
            either be a single filename or a list of filenames.
        **kwargs : Any
            Additional keyword arguments. The following keys are supported:

            scan : Scan, optional
                The scan object to import the data into. If None, the global
                ScanContext is used.
        """
        _scan = kwargs.get("scan") or ScanContext()
        if isinstance(filename, (Path, str)):
            _imported_params = cls._read_single_fio_file(filename)
        else:
            raise UserConfigError(
                "The input for the fio importer must be a single filename or "
                "a list or tuple of filenames. Filenames can be given as string "
                "or Path objects."
            )
        cls.update_scan_from_import(_imported_params, _scan)

    @classmethod
    def import_from_file_sequence(cls, filenames: Sequence[Path | str], **kwargs: Any):
        """
        Import a Scan from a sequence of filenames.

        Parameters
        ----------
        filenames : Sequence[Path or str]
            The sequence of filenames to be imported.
        **kwargs : Any
            Additional keyword arguments. The following keys are supported:

            scan : Scan, optional
                The scan object to import the data into. If None, the global
                ScanContext is used.
            scan_dim0_motor : str, optional
                The name of the motor that is scanned in the first dimension.
                If None, the motor name is determined from differences in the
                motor positions between the scans.
        """
        _scan = kwargs.get("scan") or ScanContext()
        if len(filenames) == 1:
            _imported_params = cls._read_single_fio_file(filenames[0])
        else:
            _imported_params = cls._import_multiple_fio(filenames, **kwargs)
        cls.update_scan_from_import(_imported_params, _scan)

    @staticmethod
    def _get_default_values(filepath: Path, ndim: int) -> dict[str, Any]:
        """
        Get the default Parameter values for a 1D scan.

        Parameters
        ----------
        filepath : Path
            The path to the file being imported.
        ndim : int
            The number of dimensions of the scan.

        Returns
        -------
        dict[str, Any]
            The default values for the Parameters. This dictionary is meant
            to be used by the importer and not to set the Parameters directly.
        """
        _defaults = {
            "scan_dim": ndim,
            "scan_title": "",
            "pattern_number_offset": 0,
            "pattern_number_delta": 1,
            "frame_indices_per_scan_point": 1,
            "scan_frames_per_point": 1,
            "scan_multi_frame_handling": "Average",
            "scan_name_pattern": filepath.stem,
            "scan_base_directory": filepath.parents[1],
        }
        for _dim in range(ndim):
            _defaults[f"scan_dim{_dim}_unit"] = ""
        return _defaults

    @staticmethod
    def _get_device_substring(file_content: str) -> str:
        """
        Get the substring containing the device positions from the fio file content.

        Parameters
        ----------
        file_content : str
            The content of the fio file.

        Returns
        -------
        str
            The substring containing the device positions.
        """
        _param_start_str = "\n!\n! Parameter\n!\n%p\n"
        _param_start_str_index = file_content.find(_param_start_str)
        _param_end_str = "\n!\n! Data\n!\n"
        _param_end_str_index = file_content.find(_param_end_str)
        return file_content[
            len(_param_start_str) + _param_start_str_index : _param_end_str_index
        ]

    @staticmethod
    def _get_motor_positions(string: str) -> np.ndarray:
        """
        Get the motor positions from the fio file string subset.

        Parameters
        ----------
        string : str
            The string representing the motor positions.

        Returns
        -------
        np.ndarray
            The motor positions.
        """
        return np.array(
            [
                (float(_val) if "nan" not in _val else np.nan)
                for _line in string.split("\n")
                for _, _val in [_line.split("=")]
            ]
        )

    @classmethod
    def _read_single_fio_file(cls, filename: Path | str) -> dict[str, Any]:
        """
        Import scan metadata from a single fio file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be imported.

        Returns
        -------
        dict[str, Any]
            The imported representation of the Scan parameters.
        """
        _scan_command_found = False
        _params = {"scan_dim": 0}  # Initialize to avoid unbound variable
        try:
            with open(filename, "r") as stream:
                file_lines = stream.readlines()
        except (FileNotFoundError, OSError, ValueError) as error:
            raise UserConfigError from error
        for _i_line, _line in enumerate(file_lines):
            if _line.startswith(("ascan", "dscan", "mesh", "dmesh")):
                if _scan_command_found:
                    raise UserConfigError(_ERROR_TEXT_MULTIPLE_SCAN_COMMANDS)
                if _line.startswith(("ascan", "dscan")):
                    _params = cls._process_1dscan_cmd(_i_line, _line, file_lines)
                else:  # "mesh" or "dmesh"
                    _params = cls._process_mesh_cmd(_i_line, _line, file_lines)
                _scan_command_found = True
        if not _scan_command_found:
            raise UserConfigError("No scan command found.")
        _ndim = _params.get("scan_dim", 0)
        _imported_params = cls._get_default_values(Path(filename), _ndim)
        _imported_params.update(_params)
        return _imported_params

    @classmethod
    def _process_1dscan_cmd(
        cls, i_line: int, cmd_line: str, file_lines: list[str]
    ) -> dict[str, Any]:
        """
        Process a 1D scan command from  the fio file.

        Parameters
        ----------
        i_line : int
            The index of the line containing the scan command.
        cmd_line : str
            The line of the fio file containing the scan command.
        file_lines : list[str]
            The list of all lines in the fio file.

        Returns
        -------
        dict[str, Any]
            The imported representation of the Scan parameters.
        """
        _cmd, _motor, *_scan_pars = cmd_line.split()
        _start = float(_scan_pars[0])
        _end = float(_scan_pars[1])
        # The scan defines the number of intervals, not the number of points
        _n_points = int(_scan_pars[2]) + 1
        _delta = (_end - _start) / (_n_points - 1)
        if cmd_line.startswith("dscan"):
            for _l in file_lines[i_line + 1 :]:
                if _l.startswith(_motor):
                    _start += float(_l.split("= ")[1])
        return {
            f"{_D0}_label": _motor,
            f"{_D0}_delta": _delta,
            f"{_D0}_n_points": _n_points,
            f"{_D0}_offset": _start,
            "scan_dim": 1,
        }

    @classmethod
    def _process_mesh_cmd(
        cls, i_line: int, cmd_line: str, file_lines: list[str]
    ) -> dict[str, Any]:
        """
        Process a mesh command from the fio file.

        Parameters
        ----------
        i_line : int
            The index of the line containing the scan command.
        cmd_line : str
            The line of the fio file containing the scan command.
        file_lines : list[str]
            The list of all lines in the fio file.

        Returns
        -------
        dict[str, Any]
            The imported representation of the Scan parameters.
        """
        _cmd, *_scan_pars = cmd_line.split()
        _motor1_name = _scan_pars[0]
        _motor1_start = float(_scan_pars[1])
        _motor1_end = float(_scan_pars[2])
        _motor1_n_points = int(_scan_pars[3]) + 1
        _motor1_delta = (_motor1_end - _motor1_start) / (_motor1_n_points - 1)
        # in the sardana syntax, the first motor is the fast motor and runs
        # a nested loop inside the second motor scan. In pydidas nomenclature,
        # the fast motor is the second motor, so we need to swap the motor names
        _motor0_name = _scan_pars[4]
        _motor0_start = float(_scan_pars[5])
        _motor0_end = float(_scan_pars[6])
        _motor0_n_points = int(_scan_pars[7]) + 1
        _motor0_delta = (_motor0_end - _motor0_start) / (_motor0_n_points - 1)
        if cmd_line.startswith("dmesh"):
            for _l in file_lines[i_line + 1 :]:
                if _l.startswith(_motor1_name):
                    _motor1_start += float(_l.split("= ")[1])
                if _l.startswith(_motor0_name):
                    _motor0_start += float(_l.split("= ")[1])
        return {
            f"{_D0}_label": _motor0_name,
            f"{_D0}_delta": _motor0_delta,
            f"{_D0}_n_points": _motor0_n_points,
            f"{_D0}_offset": _motor0_start,
            f"{_D1}_label": _motor1_name,
            f"{_D1}_delta": _motor1_delta,
            f"{_D1}_n_points": _motor1_n_points,
            f"{_D1}_offset": _motor1_start,
            "scan_dim": 2,
        }

    @classmethod
    def _import_multiple_fio(
        cls, filenames: Sequence[Path | str], **kwargs: Any
    ) -> dict[str, Any]:
        """
        Import scan metadata from multiple fio files.

        The list of filenames is expected to be ordered and the metadata
        differences between the files determine the second scan dimension.

        Parameters
        ----------
        filenames : Sequence[Path or str]
            The filenames of the files to be imported.
        **kwargs : Any
            Additional keyword arguments. The following keys are supported:

            scan : Scan, optional
                The scan object to import the data into. If None, the global
                ScanContext is used.
            scan_dim0_motor : str, optional
                The name of the motor that is scanned in the first dimension.
                If None, the motor name is determined from differences in the
                motor positions between the scans.
            return_moved_motor_names : bool, optional
                Flag to return the names of the motors that have moved between
                scans. If True, the function returns a list with the error
                message and the names of the motors that have moved.
        """
        _params = cls._get_default_values(Path(filenames[0]), 2)
        scan_dim0_motor: str | None = kwargs.get("scan_dim0_motor", None)
        _fio_params, _motor_pos, _motor_names = cls._process_fio_file_list(filenames)
        _params.update(_fio_params)
        _index_moved_motors = cls._get_moved_motor_indices(
            _motor_pos, _motor_names, _params
        )
        if scan_dim0_motor is not None:
            _motors = {_motor_name: _i for _i, _motor_name in enumerate(_motor_names)}
            if scan_dim0_motor in _motors:
                _index_moved_motors = [_motors[scan_dim0_motor]]
            else:
                scan_dim0_motor = None
        if len(_index_moved_motors) != 1 and scan_dim0_motor is None:
            raise UserConfigError(
                "Could not determine the second scan dimension!\n"
                + "Multiple motors have been moved between scans: "
                + ", ".join([_motor_names[_i] for _i in _index_moved_motors])
            )
        # process other parameters
        _values = _motor_pos[_index_moved_motors[0]]
        _delta, _start = np.polyfit(np.arange(_values.size), _values, 1)
        _params[f"{_D0}_delta"] = _delta
        _params[f"{_D0}_n_points"] = len(filenames)
        _params[f"{_D0}_offset"] = _start
        _params[f"{_D0}_label"] = _motor_names[_index_moved_motors[0]]
        return _params

    @classmethod
    def _process_fio_file_list(
        cls, filenames: Sequence[Path | str]
    ) -> tuple[dict[str, Any], np.ndarray, list[str]]:
        """
        Read the content of multiple fio files.

        Parameters
        ----------
        filenames : Sequence[Path or str]
            The filenames of the files to be read.

        Returns
        -------
        dict[str, Any]
            The imported parameters that are expected to be the
            same across all files.
        np.ndarray
            The motor positions.
        list[str]
            The motor names.
        """
        _params = cls._read_single_fio_file(filenames[0])
        for _key in ["delta", "n_points", "offset", "label"]:
            _params[f"{_D1}_{_key}"] = _params[f"{_D0}_{_key}"]
            _params[f"{_D0}_{_key}"] = "" if _key == "label" else 0
        # check for file name consistency:
        _stems = [Path(_fname).stem for _fname in filenames]
        _common = os.path.commonprefix(_stems)
        _stem_lengths = np.unique([len(_stem) for _stem in _stems])
        if not _common or _stem_lengths.size > 1:
            raise UserConfigError(
                "The selected fio files do not have a common filename prefix "
                "and/or differ in their filename length. Please check the "
                "selected files and try again. Only filenames with a common "
                "prefix and identical lengths are supported."
            )
        _common = _common.rstrip("0")
        _params["pattern_number_offset"] = int(_stems[0].removeprefix(_common))
        _params["scan_name_pattern"] = _common + "#" * (_stem_lengths[0] - len(_common))
        # Initialize variables to avoid possibly unbound issues
        _motor_names: list[str] = []
        _motor_pos = np.array([])
        _scan_command_ref = ""
        try:
            for _index, _fname in enumerate(filenames):
                with open(_fname, "r") as stream:
                    _file_content = stream.read()
                _index_scan = _file_content.find("scan") - 1
                _device_pos_str = cls._get_device_substring(_file_content)
                if _index == 0:
                    _scan_command_ref = _file_content[_index_scan:].split("\n")[0]
                    _motor_names = [
                        _name.strip()
                        for _line in _device_pos_str.split("\n")
                        for _name, _ in [_line.split("=")]
                    ]
                    _motor_pos = np.full((len(_motor_names), len(filenames)), np.nan)
                _motor_pos[:, _index] = cls._get_motor_positions(_device_pos_str)
                if _scan_command_ref != _file_content[_index_scan:].split("\n")[0]:
                    raise UserConfigError(
                        "The selection of FIO files has different scan commands. "
                        "Please check your file selection and make sure they "
                        "belong to the same mesh scan."
                    )
        except (ValueError, FileNotFoundError, OSError) as error:
            raise UserConfigError(
                "Could not import the selected fio files. Please verify that all "
                "files are valid and belong to the same scan.\n\n"
                f"The following error occurred:\n {error}"
            )
        # Filter for motors which have logged nan values:
        _index_not_nan = np.isfinite(_motor_pos).all(axis=1)
        _motor_names = [
            _name
            for _i, _name in enumerate(_motor_names)
            if _index_not_nan[_i]  # type: ignore[index]
        ]
        _motor_pos = _motor_pos[_index_not_nan]
        return _params, _motor_pos, _motor_names

    @classmethod
    def _get_moved_motor_indices(
        cls, motor_pos: np.ndarray, motor_names: list[str], params: dict[str, Any]
    ) -> list[int]:
        """
        Get the indices of the motors that have moved between scans.

        Parameters
        ----------
        motor_pos : np.ndarray
            The motor positions.
        motor_names : list[str]
            The motor names.
        params : dict[str, Any]
            The imported parameters. Used to identify the motor moved in
            dimension 1.

        Returns
        -------
        list[int]
            The indices of the motors that have moved.
        """
        _motor1 = params.get("scan_dim1_label", "")
        _index_moved_motors = list(
            np.unique(np.where(np.diff(motor_pos, axis=1) != 0)[0])
        )
        if _motor1 and _motor1 in motor_names:
            _dim1_motor_index = motor_names.index(_motor1)
            if _dim1_motor_index in _index_moved_motors:
                _index_moved_motors.remove(_dim1_motor_index)
        return _index_moved_motors
