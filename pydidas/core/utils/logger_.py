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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['pydidas_logger', 'LOGGING_LEVEL']

import os
import logging
import time
import multiprocessing as mp


LOGGING_LEVEL = logging.DEBUG


def pydidas_logger(level=logging.DEBUG):
    """
    Get the pydidas logger.

    The pydidas logger will create logfiles in a subdirectory logs of the
    pydidas module directory.

    Returns
    -------
    multiprocessing.logger
        The logger instance
    """
    logger = mp.get_logger()
    logger.setLevel(level)
    formatter = logging.Formatter(\
        '[%(asctime)s| %(levelname)s| %(processName)s] %(message)s')
    _logpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__)))), 'logs')
    if not os.path.exists(_logpath):
        os.makedirs(_logpath)
    _time = time.localtime()
    _timestr = f'{_time.tm_year:04d}{_time.tm_mon:02d}{_time.tm_mday:02d}'
    _logfile = os.path.join(_logpath, f'pydidas_log{_timestr}.log')
    handler = logging.FileHandler(_logfile)
    handler.setFormatter(formatter)
    # this will make sure you won't have duplicated messages in the output
    if len(logger.handlers) == 0:
        logger.addHandler(handler)
    logger.setLevel(LOGGING_LEVEL)
    return logger
