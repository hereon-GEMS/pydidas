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
Module with the LineEditWithIcon which is a subclassed QLineEdit and displays a small
icon in the front.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["LineEditWithIcon"]


from qtpy import QtWidgets

from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.utilities import get_pyqt_icon_from_str


class LineEditWithIcon(QtWidgets.QLineEdit):
    """
    A QLineEdit with an added icon.

    Parameters
    ----------
    parent : QWidget, optional
        The Qt parent widget. The default is None.
    **kwargs : Any supported Qt arguments
        Any arguments which have an associated setArgName method in
        Qt can be defined at creation.
    """

    init_kwargs = ["parent", "icon"]

    def __init__(self, icon=None, **kwargs):
        QtWidgets.QLineEdit.__init__(self, kwargs.pop("parent", None))

        icon = kwargs.pop("icon", None)
        if isinstance(icon, str):
            icon = get_pyqt_icon_from_str(icon)
        apply_qt_properties(self, **kwargs)

        if icon is not None:
            self.addAction(icon, QtWidgets.QLineEdit.LeadingPosition)
