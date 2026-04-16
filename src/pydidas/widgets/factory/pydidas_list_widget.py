# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
The pydidas_list includes a subclassed QListWidget with automatic font formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasListWidget"]


from typing import Any

from qtpy import QtWidgets

from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


class PydidasListWidget(PydidasWidgetMixin, QtWidgets.QListWidget):
    """
    A QListWidget with automatic width scaling and font formatting
    """

    def __init__(self, **kwargs: Any) -> None:
        QtWidgets.QListWidget.__init__(self, parent=kwargs.get("parent", None))
        PydidasWidgetMixin.__init__(self, **kwargs)
