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
Module with PydidasExceptionMessageBox class for handling user config exceptions in a
lighter way.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasExceptionMessageBox"]


from typing import Any

from qtpy import QtGui

from pydidas.resources import icons
from pydidas.widgets.dialogues.acknowledge_box import AcknowledgeBox


class PydidasExceptionMessageBox(AcknowledgeBox):
    """
    Show a dialogue box with exception information.

    Parameters
    ----------
    *args : Any
        Arguments passed to QtWidgets.QDialogue instantiation.
    **kwargs : Any
        Supported keyword arguments are:

        text : str, optional
            The error string. The default is an empty string.
        title : str, optional
            The window title. The default is "Configuration error".
        text_preformatted : bool, optional
            Flag to keep the text formatting and not to auto-format the text
            to keep a width of < 60 characters.
    """

    default_title = "Configuration error"
    add_error_icon = True

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs["show_checkbox"] = False
        super().__init__(*args, **kwargs)

    @property
    def default_icon(self) -> QtGui.QIcon:
        """
        The default icon for the message box.

        Returns
        -------
        QtGui.QIcon
            The default icon.
        """
        return icons.pydidas_error_icon_with_bg()
