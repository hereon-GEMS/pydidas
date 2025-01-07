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
The pydidas_pushbutton includes a subclassed QPushButton with automatic font formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPushButton"]


from functools import partial

from qtpy import QtWidgets

from pydidas.core.constants import POLICY_EXP_FIX
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin
from pydidas.widgets.utilities import get_pyqt_icon_from_str


class PydidasPushButton(PydidasWidgetMixin, QtWidgets.QPushButton):
    """
    Create a QPushButton with automatic font and size formatting.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs[:] + ["icon"]

    def __init__(self, *args: tuple, **kwargs: dict):
        QtWidgets.QPushButton.__init__(self, *args)
        if isinstance(kwargs.get("icon", None), str):
            kwargs["icon"] = get_pyqt_icon_from_str(kwargs.get("icon"))
        PydidasWidgetMixin.__init__(self, **kwargs)
        if "sizePolicy" not in kwargs:
            self.setSizePolicy(*POLICY_EXP_FIX)
        self.sizeHint = partial(QtWidgets.QPushButton.sizeHint, self)
