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
Module with the PydidasWebView class which is a QWebEngineView of the html
documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PydidasHtmlDocView']

from qtpy import QtCore, QtWebEngineWidgets

from ..core.utils import get_doc_home_qurl


class PydidasHtmlDocView(QtWebEngineWidgets.QWebEngineView):
    """
    Subclass of QWebEngineView with an updated size hint and fixed URL for
    the pydidas documentation.
    """
    def __init__(self):
        super().__init__()
        _profile = self.page().profile()
        _profile.setHttpCacheType(0)
        self.load_main_doc()

    def load_main_doc(self):
        """
        Load the main window of the documentation.
        """
        self.load(get_doc_home_qurl())

    def sizeHint(self):
        """
        Reimplement the generic sizeHint to return a larger window.

        Returns
        -------
        QtCore.QSize
            The desired size for the documentation html content.
        """
        return QtCore.QSize(900, 600)
