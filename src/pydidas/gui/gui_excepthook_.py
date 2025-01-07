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
Module with the pydidas excepthook for the GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["gui_excepthook"]


import os
import time
import traceback
from io import StringIO

from pydidas.core import FileReadError, UserConfigError
from pydidas.core.utils import get_logging_dir
from pydidas.widgets.dialogues import ErrorMessageBox, PydidasExceptionMessageBox
from pydidas_qtcore import PydidasQApplication


def gui_excepthook(exc_type, exception, trace):
    """
    Catch global exceptions.

    This global function is used to replace the generic sys.excepthook
    to handle exceptions. It will open a popup window with the exception
    text.

    Parameters
    ----------
    exc_type : type
        The exception type
    exception : Exception
        The exception itself.
    trace : traceback object
        The trace of where the exception occured.
    """
    _app = PydidasQApplication.instance()

    if exc_type in (UserConfigError, FileReadError):
        # need to select the splitting char explicitly because used ' and " chars
        # will alter the representation.
        _split_char = repr(exception)[16 if exc_type is UserConfigError else 14]
        _title = (
            "Configuration Error" if exc_type is UserConfigError else "File read error"
        )
        _exc_repr = repr(exception).split(_split_char)[1]
        _app.sig_gui_exception_occurred.emit()
        _ = PydidasExceptionMessageBox(text=_exc_repr, title=_title).exec_()
        return
    with StringIO() as _tmpfile:
        traceback.print_tb(trace, None, _tmpfile)
        _tmpfile.seek(0)
        _trace = _tmpfile.read()

    _time = time.strftime("%Y-%m-%d %H:%M:%S")
    _sep = "\n" + "-" * 20 + "\n"
    _msg = "-" * 20 + "\n" + _sep.join([_time, f"{exc_type}: {exception}", _trace])

    _logfile = os.path.join(get_logging_dir(), "pydidas_exception.log")
    with open(_logfile, "a+") as _file:
        _file.write("\n\n" + _msg)

    _app.sig_gui_exception_occurred.emit()

    _ = ErrorMessageBox(text=_msg).exec_()
