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
Window to pop out data viewing frames
"""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataViewerWindow"]


from typing import Any

from pydidas.widgets.base_classes import PydidasWindow
from pydidas.widgets.data_viewer import DataViewer


class DataViewerWindow(PydidasWindow):
    """
    Window which displays basic information about the pydidas software.
    """

    def __init__(self, **kwargs: Any) -> None:
        PydidasWindow.__init__(self, title="Data viewer", **kwargs)
        self.resize(900, 700)

    def build_frame(self) -> None:
        """Embed a DataViewer inside the window."""
        self.add_any_widget(
            "viewer",
            DataViewer(parent=self),
            gridPos=(0, 0, 1, 1),
        )

    @property
    def viewer(self) -> DataViewer:
        """Direct access to the internal DataViewer instance."""
        return self._widgets["viewer"]
