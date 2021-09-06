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

"""Module with the DataBrowsingFrame which is used to browse data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DataBrowsingFrame']

import os
from functools import partial

from PyQt5 import QtWidgets

from pydidas.widgets import BaseFrame
from pydidas.image_io import ImageReaderFactory, read_image
from pydidas.config import HDF5_EXTENSIONS
from pydidas.gui.builders.data_browsing_frame_builder import (
    create_data_browsing_frame_widgets_and_layout)


IMAGE_READER = ImageReaderFactory()


class DataBrowsingFrame(BaseFrame):
    """
    The DataBrowsingFrame is widget / frame with a directory exporer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        super().__init__(parent=parent, name=name)

        create_data_browsing_frame_widgets_and_layout(self)
        self._widgets['tree'].doubleClicked.connect(self.__fileSelected)
        self._widgets['tree'].clicked.connect(self.__fileHighlighted)
        self._widgets['but_minimize'].clicked.connect(
        partial(self.change_splitter_pos, False))
        self._widgets['but_maximize'].clicked.connect(
            partial(self.change_splitter_pos, True))
        self.__selection_width = self._widgets['selection'].width()

    def change_splitter_pos(self, enlargeDir=True):
        if enlargeDir:
            self._widgets['splitter'].moveSplitter(770, 1)
        else:
            self._widgets['splitter'].moveSplitter(300, 1)

    def __fileHighlighted(self):
        """
        Perform actions after a file has been highlighted in the
        DirectoryExplorer.
        """
        index = self._widgets['tree'].selectedIndexes()[0]
        _name = self._widgets['tree']._filemodel.filePath(index)
        if os.path.isfile(_name):
            _name = os.path.dirname(_name)
        self.q_settings.setValue('directory_explorer/path', _name)

    def __fileSelected(self):
        """
        Open a file after sit has been selected in the DirectoryExplorer.
        """
        index = self._widgets['tree'].selectedIndexes()[0]
        _name = self._widgets['tree']._filemodel.filePath(index)
        self.set_status(f'Opened file: {_name}')
        if not os.path.isfile(_name):
            return
        _extension= '.' + os.path.basename(_name).split(".")[-1]
        _supported_nothdf_ext = (set(IMAGE_READER._extensions.keys())
                          - set(HDF5_EXTENSIONS))
        if _extension in HDF5_EXTENSIONS:
            self._widgets['hdf_dset'].setVisible(True)
            self._widgets['hdf_dset'].set_filename(_name)
            return
        self._widgets['hdf_dset'].setVisible(False)
        if _extension in _supported_nothdf_ext:
            _data = read_image(_name)
            self._widgets['viewer'].setData(_data)


if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.config.STANDARD_FONT_SIZE

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()
    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'),
                       DataBrowsingFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()
