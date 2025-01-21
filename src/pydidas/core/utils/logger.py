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
The logger_ module allows to get a multiprocessing compatible logger for
pydidas which will write a logfile.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["pydidas_logger", "get_logging_dir", "clear_logging_dir", "LOGGING_LEVEL"]


import logging
import multiprocessing as mp
import os
import time
from typing import List

from qtpy import QtCore

from pydidas.logging_level import LOGGING_LEVEL
from pydidas.version import VERSION


_LOG_FORMATTER = logging.Formatter(
    "[%(asctime)s| %(levelname)s| %(processName)s] %(message)s"
)


def pydidas_logger(level: int = LOGGING_LEVEL) -> logging.Logger:
    """
    Get the pydidas logger.

    The pydidas logger will create logfiles in a subdirectory logs of the
    pydidas module directory.

    Returns
    -------
    multiprocessing.logger
        The logger instance
    """
    _logpath = os.path.join(get_logging_dir(), "logs")
    if not os.path.exists(_logpath):
        os.makedirs(_logpath)

    _logger = mp.get_logger()
    _logger.setLevel(level)

    # this will make sure you won't have duplicated messages in the output
    if len(_logger.handlers) == 0:
        _logfile = _get_todays_log_name()
        _handler = logging.FileHandler(_logfile)
        _handler.setFormatter(_LOG_FORMATTER)
        _logger.addHandler(_handler)

    return _logger


def get_logging_dir() -> str:
    """
    Return the pydidas logging directory.

    Returns
    -------
    str
        The path to the pydidas module.
    """
    _docs_path = QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.DocumentsLocation
    )[0]
    if os.sep == "\\":
        _docs_path = _docs_path.replace("/", "\\")
    _log_path = os.path.join(_docs_path, "pydidas", VERSION)
    if not os.path.exists(_log_path):
        os.makedirs(_log_path)
    return _log_path


def _get_todays_log_name() -> str:
    """
    Get the name of today's logfile.

    Returns
    -------
    str
        The filename.
    """
    _time = time.localtime()
    _timestr = f"{_time.tm_year:04d}{_time.tm_mon:02d}{_time.tm_mday:02d}"
    return os.path.join(get_logging_dir(), "logs", f"pydidas_log_{_timestr}.log")


def clear_logging_dir() -> List[str]:
    """
    Clear all files in the logging dir, if possible.

    Returns
    -------
    list
        The list of files which could not be removed because of permission problems.
    """
    _logdir = get_logging_dir()
    _log_file_dir = os.path.join(_logdir, "logs")

    _files_wo_permission = []
    try:
        os.remove(os.path.join(_logdir, "pydidas_exception.log"))
    except PermissionError:
        _files_wo_permission.append(os.path.join(_logdir, "pydidas_exception.log"))
    except FileNotFoundError:
        pass

    for _file in os.listdir(_log_file_dir):
        _fname = os.path.join(_log_file_dir, _file)
        try:
            os.remove(_fname)
        except PermissionError:
            _files_wo_permission.append(_fname)

    if len(_files_wo_permission) > 0:
        _files_wo_permission.pop(-1)
    return _files_wo_permission
