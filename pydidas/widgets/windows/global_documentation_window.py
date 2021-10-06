# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the GlobalConfigWindow class which is a MainWindow widget
to view and modify the global settings."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GlobalDocumentationWindow', 'get_doc_qurl']


import os

import qtawesome as qta
from PyQt5 import QtWebEngineWidgets, QtWidgets, QtCore

from ..scroll_area import ScrollArea


def get_doc_qurl():
    """
    Get the full filepath & -name of the index.html

    Returns
    -------
    url : QtCore.QUrl
        The QUrl object with the path to the index.html file.

    """
    _name = __file__
    for i in range(4):
        _name = os.path.dirname(_name)
    _docdir = os.path.join(_name, 'docs', 'build', 'html')
    _docfile = 'file:///' + os.path.join(_docdir, 'index.html')
    _docfile = _docfile.replace('\\', '/')
    return QtCore.QUrl(_docfile)


class WebView(QtWebEngineWidgets.QWebEngineView):
    """
    Subclass of QWebEngineView with an updated size hint and fixed URL for
    the pydidas documentation.
    """

    def __init__(self):
        super().__init__()
        self.load(get_doc_qurl())

    def sizeHint(self):
        return QtCore.QSize(900, 600)

    def closeEvent(self, event):
        _page = self.page()
        _page.deleteLater()
        event.accept()


class GlobalDocumentationWindow(QtWidgets.QMainWindow):
    """
    Window with a webbrowser which shows the global documentation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('pydidas http documentation')
        self.setWindowIcon(qta.icon('mdi.text-box-multiple-outline'))

        self._scroll_area = ScrollArea(minimumWidth=800, minimumHeight=200,
                                       widget=WebView())
        self.setCentralWidget(self._scroll_area)
        self.setVisible(False)

    # def closeEvent(self, event):
    #     _webview = self._scroll_area.widget()
    #     _webview.deleteLater()
    #     self._scroll_area.deleteLater()
    #     event.accept()
