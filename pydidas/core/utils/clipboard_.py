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
Module with utility functions for the system's clipboard.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["copy_text_to_system_clipbord"]


from qtpy import QtWidgets


def copy_text_to_system_clipbord(text):
    """
    Copy the given text to the system clipboard.

    Parameters
    ----------
    text : str
        The text to be copied.

    Raises
    ------
    TypeError
        If the text is not of type string.
    """
    if not isinstance(text, str):
        raise TypeError("Only strings can be copied to the system clipboard.")
    _clip = QtWidgets.QApplication.clipboard()
    _clip.clear(mode=_clip.Clipboard)
    _clip.setText(text, mode=_clip.Clipboard)
