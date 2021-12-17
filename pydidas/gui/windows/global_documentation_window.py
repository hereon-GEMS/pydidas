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
Module with the GlobalConfigWindow class which is a QMainWindow widget
to view and modify the global settings in a dedicatd window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GlobalDocumentationWindow']

from PyQt5 import QtWebEngineWidgets, QtWidgets, QtCore

from ...widgets import ScrollArea, factory, get_pyqt_icon_from_str_reference
from ...core.utils import get_doc_qurl



class PydidasWebView(QtWebEngineWidgets.QWebEngineView):
    """
    Subclass of QWebEngineView with an updated size hint and fixed URL for
    the pydidas documentation.
    """
    def __init__(self):
        super().__init__()
        self.load_main_doc()

    def load_main_doc(self):
        """
        Load the main window of the documentation.
        """
        self.load(get_doc_qurl())

    def sizeHint(self):
        """
        Reimplement the generic sizeHint to return a larger window.

        Returns
        -------
        QtCore.QSize
            The desired size for the documentation html content.
        """
        return QtCore.QSize(900, 600)

    def closeEvent(self, event):
        """
        If the widget is to be closed, mark the webpage for deletion.

        Parameters
        ----------
        event : QtCore.QEvent
            The calling event.
        """
        _page = self.page()
        _page.deleteLater()
        event.accept()


class GlobalDocumentationWindow(QtWidgets.QMainWindow):
    """
    Window with a webbrowser which shows the global documentation in html
    format.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('pydidas http documentation')
        self.setWindowIcon(get_pyqt_icon_from_str_reference(
            'qta::mdi.text-box-multiple-outline'))

        self._webview = PydidasWebView()
        self._actions = {}
        self._actions['home'] = QtWidgets.QAction(
            get_pyqt_icon_from_str_reference('qta::mdi.home'), '')
        self._actions['undo'] = QtWidgets.QAction(
           get_pyqt_icon_from_str_reference('qta::mdi.undo'), '')
        self._actions['redo'] = QtWidgets.QAction(
            get_pyqt_icon_from_str_reference('qta::mdi.redo'), '')

        self._scroll_area = ScrollArea(minimumWidth=800, minimumHeight=200,
                                       widget=self._webview)

        self.setCentralWidget(self._scroll_area)
        self.setVisible(False)

        self._toolbar = QtWidgets.QToolBar()
        self._toolbar.setFixedHeight(30)
        self._toolbar.setIconSize(QtCore.QSize(25, 25))
        self._toolbar.setMovable(False)
        self.addToolBar(self._toolbar)
        self._toolbar.addAction(self._actions['home'])
        self._toolbar.addAction(self._actions['undo'])
        self._toolbar.addAction(self._actions['redo'])

        self._actions['home'].triggered.connect(self._action_home)
        self._actions['undo'].triggered.connect(self._action_undo)
        self._actions['redo'].triggered.connect(self._action_redo)

    @QtCore.pyqtSlot()
    def _action_home(self):
        """
        Goto the documentation homepage.
        """
        self._webview.load_main_doc()

    @QtCore.pyqtSlot()
    def _action_undo(self):
        self._webview.page().triggerAction(
            QtWebEngineWidgets.QWebEnginePage.Back)

    @QtCore.pyqtSlot()
    def _action_redo(self):
        self._webview.page().triggerAction(
            QtWebEngineWidgets.QWebEnginePage.Forward)
