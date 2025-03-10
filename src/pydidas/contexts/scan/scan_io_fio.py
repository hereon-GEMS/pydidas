# This file is part of pydidas.
#
# Copyright 2024-2025, Helmholtz-Zentrum Hereon
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
Module with the ScanIoFio class which is used to importscan axes from fio file(s).
"""

__author__ = "Ilia Petrov, Malte Storm"
__copyright__ = "Copyright 2024-2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoFio"]


import os
from pathlib import Path

import numpy as np

from pydidas.contexts.scan.scan import Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError


SCAN = ScanContext()

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

    @staticmethod
    def _get_default_values(filepath: Path, ndim: int) -> dict[str, int | str]:
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
        dict[str, Union[int, str]]
            The default values for the Parameters. This dictionary is meant
            to be used by the importer and not to set the Parameters directly.
        """
        _defaults = {
            "scan_dim": ndim,
            "scan_title": "",
            "scan_start_index": 0,
            "scan_index_stepping": 1,
            "scan_multiplicity": 1,
            "scan_multi_image_handling": "Average",
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

    @staticmethod
    def _line_starts_with_scan_cmd(line: str) -> bool:
        """
        Check if a line starts with a scan command.

        Parameters
        ----------
        line : str
            The line to check.

        Returns
        -------
        bool
            True if the line starts with a scan command, False otherwise.
        """
        return (
            line.startswith("ascan")
            or line.startswith("dscan")
            or line.startswith("mesh")
            or line.startswith("dmesh")
        )

    @classmethod
    def import_from_file(cls, filenames: Path | str | list[Path | str], **kwargs: dict):
        """
        Import scan metadata from a single or multiple fio files.

        Parameters
        ----------
        filenames : Union[Path, str, list[Union[Path, str]]]
            The filename(s) of the file(s) to be imported. Filenames can
            either be a single
        **kwargs : dict
            Additional keyword arguments. The following keys are supported:

            scan : Scan, optional
                The scan object to import the data into. If None, the global
                ScanContext is used.
            scan_dim0_motor : str, optional
                The name of the motor that is scanned in the first dimension.
                If None, the motor name is determined from differences in the
                motor positions between the scans.
        """
        scan = SCAN if kwargs.get("scan", None) is None else kwargs.get("scan")
        cls.imported_params = {}
        if isinstance(filenames, (Path, str)):
            cls._import_single_fio(filenames, scan=scan)
        elif isinstance(filenames, (list, tuple)):
            if len(filenames) == 1:
                cls._import_single_fio(filenames[0], scan=scan)
            else:
                cls._import_multiple_fio(filenames, **kwargs)
        else:
            raise UserConfigError(
                "The input for the fio importer must be a single filename or "
                "a list or tuple of filenames. Filenames can be given as string "
                "or Path objects."
            )
        cls._verify_all_entries_present()
        cls._write_to_scan_settings(scan=scan)

    @classmethod
    def _import_single_fio(cls, filename: Path | str, scan: Scan | None = None):
        """
        Import scan metadata from a single fio file.

        Parameters
        ----------
        filename : Union[Path, str]
            The filename of the file to be imported.
        scan : Scan, optional
            The scan object to import the data into. If None, the global
            ScanContext is used
        """
        _scan = SCAN if scan is None else scan
        _scan_command_found = False

        with open(filename, "r") as stream:
            file_lines = stream.readlines()
        try:
            for _i_line, _line in enumerate(file_lines):
                if cls._line_starts_with_scan_cmd(_line):
                    if _scan_command_found:
                        cls._process_duplicate_scan_command()
                    if _line.startswith("ascan") or _line.startswith("dscan"):
                        cls._process_1dscan_cmd(_i_line, _line, file_lines)
                        _scan_dim = 1
                    elif _line.startswith("mesh") or _line.startswith("dmesh"):
                        cls._process_mesh_cmd(_i_line, _line, file_lines)
                        _scan_dim = 2
                    _scan_command_found = True
            if not _scan_command_found:
                raise UserConfigError("No scan command found.")
        except (FileNotFoundError, OSError, ValueError) as error:
            cls.imported_params = {}
            raise UserConfigError from error
        cls.imported_params.update(cls._get_default_values(Path(filename), _scan_dim))

    @classmethod
    def _process_duplicate_scan_command(cls):
        """
        Process a duplicate scan command in the fio file.
        """
        cls.imported_params = {}
        raise UserConfigError(_ERROR_TEXT_MULTIPLE_SCAN_COMMANDS)

    @classmethod
    def _process_1dscan_cmd(cls, i_line: int, cmd_line: str, file_lines: list[str]):
        """
        Processs a 1D scan command from  the fio file.

        Parameters
        ----------
        i_line : int
            The index of the line containing the scan command.
        cmd_line : str
            The line of the fio file containing the scan command.
        file_lines : list[str]
            The list of all lines in the fio file.
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
        cls.imported_params[f"{_D0}_label"] = _motor
        cls.imported_params[f"{_D0}_delta"] = _delta
        cls.imported_params[f"{_D0}_n_points"] = _n_points
        cls.imported_params[f"{_D0}_offset"] = _start
        cls.imported_params["scan_dim"] = 1

    @classmethod
    def _process_mesh_cmd(cls, i_line: int, cmd_line: str, file_lines: list[str]):
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

        cls.imported_params[f"{_D0}_label"] = _motor0_name
        cls.imported_params[f"{_D0}_delta"] = _motor0_delta
        cls.imported_params[f"{_D0}_n_points"] = _motor0_n_points
        cls.imported_params[f"{_D0}_offset"] = _motor0_start
        cls.imported_params[f"{_D1}_label"] = _motor1_name
        cls.imported_params[f"{_D1}_delta"] = _motor1_delta
        cls.imported_params[f"{_D1}_n_points"] = _motor1_n_points
        cls.imported_params[f"{_D1}_offset"] = _motor1_start

    @classmethod
    def check_file_list(cls, filenames: list[Path | str], **kwargs: dict) -> list[str]:
        """
        Check if the given list of files is valid for import.

        The return values are a coded message plus any additional information.

        Parameters
        ----------
        filenames : list[Union[Path, str]]
            The list of filenames to be checked.
        **kwargs : dict
            Additional keyword arguments. Please refer to _import_multiple_fio
            for the supported keys.

        Returns
        -------
        list[str]
            The error message and additional information.
        """
        if len(filenames) == 1:
            return ["::no_error::"]
        _scan = SCAN if kwargs.get("scan", None) is None else kwargs.get("scan")
        _motor_pos, _motor_names = cls._process_fio_file_list(filenames, _scan)
        _index_moved_motors = cls._get_moved_motor_indices(_motor_pos, _motor_names)
        if len(_index_moved_motors) == 1:
            return ["::no_error::"]
        if len(_index_moved_motors) == 0:
            return ["::no_motor_moved::", "No motor has moved between scans."]
        if len(_index_moved_motors) > 1:
            return ["::multiple_motors::"] + [
                _motor_names[_i] for _i in _index_moved_motors
            ]

    @classmethod
    def _import_multiple_fio(cls, filenames: list[Path | str], **kwargs: dict):
        """
        Import scan metadata from multiple fio files.

        The list of filenames is expected to be ordered and the metadata
        differences between the files determine the second scan dimension.

        Parameters
        ----------
        filenames : list[Union[Path, str]]
            The filenames of the files to be imported.
        **kwargs : dict
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
                scans. If True, the function returns a list with the error message
                and the names of the motors that have moved.
        """
        _scan = SCAN if kwargs.get("scan", None) is None else kwargs.get("scan")
        scan_dim0_motor = kwargs.get("scan_dim0_motor", None)
        _motor_pos, _motor_names = cls._process_fio_file_list(filenames, _scan)

        # Determine the second scan dimension:
        _index_moved_motors = cls._get_moved_motor_indices(_motor_pos, _motor_names)
        if scan_dim0_motor is not None:
            _motors = {_motor_name: _i for _i, _motor_name in enumerate(_motor_names)}
            _index_moved_motors = [_motors[scan_dim0_motor]]
        if len(_index_moved_motors) != 1 and scan_dim0_motor is None:
            cls.imported_params = {}
            raise UserConfigError(
                "Could not determine the second scan dimension!\n"
                + "Multiple motors have been moved between scans: "
                + ", ".join([_motor_names[_i] for _i in _index_moved_motors])
            )

        _values = _motor_pos[_index_moved_motors[0]]
        _delta, _start = np.polyfit(np.arange(_values.size), _values, 1)
        cls.imported_params[f"{_D0}_delta"] = _delta
        cls.imported_params[f"{_D0}_n_points"] = len(filenames)
        cls.imported_params[f"{_D0}_offset"] = _start
        cls.imported_params[f"{_D0}_label"] = _motor_names[_index_moved_motors[0]]
        cls.imported_params.update(cls._get_default_values(Path(filenames[0]), 2))
        _stems = [Path(_fname).stem for _fname in filenames]
        _stem_lengths = np.unique([len(_stem) for _stem in _stems])
        _common = os.path.commonprefix(_stems)
        while _common[-1] == "0":
            _common = _common[:-1]
        if _common and _stem_lengths.size == 1:
            cls.imported_params["scan_start_index"] = int(_stems[0][len(_common) :])
            _common += "#" * (_stem_lengths[0] - len(_common))
        cls.imported_params["scan_name_pattern"] = _common

    @classmethod
    def _process_fio_file_list(cls, filenames: list[Path | str], scan: Scan):
        """
        Read the content of multiple fio files.

        Parameters
        ----------
        filenames : list[Union[Path, str]]
            The filenames of the files to be read.
        scan : Scan
            The scan object to import the data into.

        Returns
        -------
        np.ndarray
            The motor positions.
        list[str]
            The motor names.
        """

        cls._import_single_fio(filenames[0], scan=scan)
        for _key in ["delta", "n_points", "offset", "label"]:
            cls.imported_params[f"{_D1}_{_key}"] = cls.imported_params[f"{_D0}_{_key}"]
            cls.imported_params[f"{_D0}_{_key}"] = "" if _key == "label" else 0
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
                    cls.imported_params = {}
                    raise UserConfigError(
                        "The selection of FIO files has different scan commands. "
                        "Please check your file selection and make sure they "
                        "belong to the same mesh scan."
                    )
        except (ValueError, FileNotFoundError, OSError) as error:
            cls.imported_params = {}
            raise UserConfigError(
                "Could not import the selected fio files. Please verify that all "
                "files are valid and belong to the same scan.\n\n"
                f"The following error occurred:\n {error}"
            )
        # Filter for motors which have logged nan values:
        _index_not_nan = ~np.isnan(_motor_pos).all(axis=1)
        _motor_names = [
            _name for _i, _name in enumerate(_motor_names) if _index_not_nan[_i]
        ]
        _motor_pos = _motor_pos[_index_not_nan]
        return _motor_pos, _motor_names

    @classmethod
    def _get_moved_motor_indices(
        cls, motor_pos: np.ndarray, motor_names: list[str]
    ) -> list[int]:
        """
        Get the indices of the motors that have moved between scans.

        Parameters
        ----------
        motor_pos : np.ndarray
            The motor positions.
        motor_names : list[str]
            The motor names.

        Returns
        -------
        list[int]
            The indices of the motors that have moved.
        """
        _index_moved_motors = list(
            np.unique(np.where(np.diff(motor_pos, axis=1) != 0)[0])
        )
        if cls.imported_params["scan_dim1_label"] in motor_names:
            _dim1_motor_index = motor_names.index(
                cls.imported_params["scan_dim1_label"]
            )
            if _dim1_motor_index in _index_moved_motors:
                _index_moved_motors.remove(_dim1_motor_index)
        return _index_moved_motors
