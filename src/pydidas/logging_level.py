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
The logging_level module sets the global logging level in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["LOGGING_LEVEL"]


import logging
import re
import sys


__log_keys = ["logging", "logger", "logging-level", "log"]
__log_levels = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "FATAL"]
__log_level = logging.ERROR


if any(
    re.match(rf"^-{{1,2}}{re.escape(key)}$", arg)
    for key in __log_keys
    for arg in sys.argv
):
    for _index, _arg in enumerate(sys.argv):
        if _arg.strip("-") in __log_keys and _index < len(sys.argv) - 1:
            _ = sys.argv.pop(_index)
            _level = sys.argv.pop(_index).upper()
            if _level in __log_levels:
                __log_level = getattr(logging, _level)
                break


LOGGING_LEVEL = __log_level

logging.basicConfig(level=LOGGING_LEVEL)
