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
The logger_ module allows to get a multiprocessing compatible logger for
pydidas which will write a logfile.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["pydidas_logger", "get_logging_dir", "clear_logging_dir", "LOGGING_LEVEL"]

import os
import logging
import time
import multiprocessing as mp

from qtpy import QtCore

from ...version import VERSION


LOGGING_LEVEL = logging.ERROR


_LOG_FORMATTER = logging.Formatter(
    "[%(asctime)s| %(levelname)s| %(processName)s] %(message)s"
)


def pydidas_logger(level=LOGGING_LEVEL):
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


def get_logging_dir():
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


def _get_todays_log_name():
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


def clear_logging_dir():
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
