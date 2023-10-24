# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The menu_utils module includes functions used in the pydidas main_menu.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "find_toolbar_bases",
    "get_generic_menu_entries",
    "create_generic_toolbar_entry",
]

import os
from pathlib import Path

from ...core.utils import format_input_to_multiline_str
from ...widgets.utilities import get_pyqt_icon_from_str


def find_toolbar_bases(items):
    """
    Find the bases of all toolbar items which are not included in the items
    itself.

    Base levels in items are separated by forward slashes.

    Parameters
    ----------
    items : Union[list, tuple]
        An iterable of string items.

    Example
    -------
    >>> items = ['a', 'a/b', 'a/c', 'b', 'd/e']
    >>> _find_toolbar_bases(items)
    ['', 'a', 'd']

    The '' entry is the root for all top-level items. Even though 'a' is an
    item itself, it is also a parent for 'a/b' and 'a/c' and it is therefore
    also included in the list, similar to 'd'.

    Returns
    -------
    itembases : list
        A list with string entries of all the items' parents.
    """
    _itembases = []
    for _item in items:
        _parent = os.path.dirname(_item)
        if _parent not in _itembases:
            _itembases.append(_parent)
        _item = _parent
    _itembases.sort()
    return _itembases


def create_generic_toolbar_entry(entry):
    """
    Create a generic toolbar entry for the given reference.

    Parameters
    ----------
    entry : str
        The reference string for the given entry.

    Returns
    -------
    dict
        The metadata entry for the reference key.
    """
    _generic_entries = get_generic_menu_entries()
    if entry in _generic_entries:
        return _generic_entries[entry]
    return {
        "label": format_input_to_multiline_str("Expand " + entry, max_line_length=12),
        "label_invisible": format_input_to_multiline_str(
            "Expand " + entry, max_line_length=12
        ),
        "label_visible": format_input_to_multiline_str(
            "Hide " + entry, max_line_length=12
        ),
        "icon": get_pyqt_icon_from_str("qta::mdi.arrow-right-circle"),
        "icon_invisible": get_pyqt_icon_from_str("qta::mdi.arrow-right-circle"),
        "icon_visible": get_pyqt_icon_from_str("qta::mdi.arrow-left-circle"),
        "menu_tree": [
            ("" if _path == Path() else _path.as_posix())
            for _path in reversed(Path(entry).parents)
        ]
        + [entry],
    }


def get_generic_menu_entries():
    """
    Get the generic menu entries for the MainWindow.

    Note: This dict must be implemented as function return value not to call the
    qtawesome icon creation without a QApplication.

    Returns
    -------
    dict
        The generic menu entries.
    """
    return {
        "Workflow processing": {
            "label": "Expand\nWorkflow\nprocessing",
            "label_visible": "Hide\nWorkflow\nProcessing",
            "label_invisible": "Expand\nWorkflow\nProcessing",
            "icon": get_pyqt_icon_from_str("pydidas::workflow_processing_expand.png"),
            "icon_visible": get_pyqt_icon_from_str(
                "pydidas::workflow_processing_hide.png"
            ),
            "icon_invisible": get_pyqt_icon_from_str(
                "pydidas::workflow_processing_expand.png"
            ),
            "menu_tree": ["", "Workflow processing"],
        }
    }
