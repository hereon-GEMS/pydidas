# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
The pydidas_documentation script allows to open the pydidas documentation in a
webbrowser.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["open_documentation"]


from qtpy import QtGui, QtWidgets


def open_documentation():
    """
    Open the pydidas documentation in the system's default browser.
    """
    from pydidas.core.utils import DOC_HOME_QURL

    _app = QtWidgets.QApplication.instance()
    if _app is None:
        _app = QtWidgets.QApplication([])
    _ = QtGui.QDesktopServices.openUrl(DOC_HOME_QURL)


if __name__ == "__main__":
    open_documentation()
