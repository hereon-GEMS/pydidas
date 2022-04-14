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
Module with the GlobalDocumentationWindow class which is a QMainWindow widget
to view the pydidas html documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GlobalDocumentationWindow']

from qtpy import QtWidgets, QtCore, QtWebEngineWidgets

from ...widgets import (PydidasHtmlDocView, ScrollArea,
                        get_pyqt_icon_from_str_reference)
from .pydidas_window import PydidasWindow


class GlobalDocumentationWindow(PydidasWindow):
    """
    Window with a webbrowser which shows the global documentation in html
    format.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('pydidas http documentation')
        self.setWindowIcon(get_pyqt_icon_from_str_reference(
            'qta::mdi.text-box-multiple-outline'))

        self._webview = PydidasHtmlDocView()
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

    @QtCore.Slot()
    def _action_home(self):
        """
        Goto the documentation homepage.
        """
        self._webview.load_main_doc()

    @QtCore.Slot()
    def _action_undo(self):
        """
        Implement a "go back" action for the documentation browser.
        """
        self._webview.page().triggerAction(
            QtWebEngineWidgets.QWebEnginePage.Back)

    @QtCore.Slot()
    def _action_redo(self):
        """
        Implement a "go forward" action for the documentation browser.
        """
        self._webview.page().triggerAction(
            QtWebEngineWidgets.QWebEnginePage.Forward)

    def deleteLater(self):
        """
        Reimplement the deleteLater method to explicitly destroy the QWebView.
        """
        if self._webview is not None:
            self._webview.deleteLater()
        self._webview = None
        super().deleteLater()
