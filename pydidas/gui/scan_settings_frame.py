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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSettingsFrame']

import sys
from PyQt5 import QtWidgets, QtCore


from pydidas.core import ScanSettings
from pydidas.core.scan_settings import ScanSettingsIoMeta
from pydidas.widgets import CreateWidgetsMixIn, excepthook, BaseFrame
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn
from pydidas.gui.builders.scan_settings_frame_builder import (
    create_scan_settings_frame_widgets_and_layout)

SCAN_SETTINGS = ScanSettings()


class ScanSettingsFrame(BaseFrame, ParameterWidgetsMixIn,
                        CreateWidgetsMixIn):
    """
    Frame for managing the global scan settings.
    """
    TEXT_WIDTH = 180
    PARAM_INPUT_WIDTH = 120

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        BaseFrame.__init__(self, parent,name=name)
        ParameterWidgetsMixIn.__init__(self)

        create_scan_settings_frame_widgets_and_layout(self)
        self._widgets['but_save'].clicked.connect(self.export_to_file)
        self._widgets['but_load'].clicked.connect(self.load_from_file)
        self._widgets['but_reset'].clicked.connect(self.reset_entries)
        self.toggle_dims()

    def toggle_dims(self):
        _prefixes = ['scan_dir_{n}', 'n_points_{n}', 'delta_{n}',
                     'unit_{n}', 'offset_{n}']
        _dim = int(self.param_widgets['scan_dim'].currentText())
        for i in range(1, 5):
            _toggle = True if i <= _dim else False
            self._widgets[f'title_{i}'].setVisible(_toggle)
            for _pre in _prefixes:
                self.toggle_param_widget_visibility(_pre.format(n=i), _toggle)

    def update_param(self, param_ref, widget):
        """
        Overload the update of a parameter method to handle the linked
        X-ray energy / X-ray wavelength variables.

        Parameters
        ----------
        param_ref : str
            The Parameter reference key
        widget : pydidas.widgets.parameter_config.InputWidget
            The widget used for the I/O of the Parameter value.
        """
        try:
            SCAN_SETTINGS.set(param_ref, widget.get_value())
        except Exception:
            widget.set_value(SCAN_SETTINGS.get(param_ref))
            excepthook(*sys.exc_info())
        # explicitly call update fo wavelength and energy
        if param_ref == 'xray_wavelength':
            _w = self.param_widgets['xray_energy']
            _w.set_value(SCAN_SETTINGS.get('xray_energy'))
        elif param_ref == 'xray_energy':
            _w = self.param_widgets['xray_wavelength']
            _w.set_value(SCAN_SETTINGS.get('xray_wavelength') * 1e10)

    def load_from_file(self):
        """
        Load ScanSettings from a file.

        This method will open a QFileDialog to select the file to be read.
        """
        _formats = ScanSettingsIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Name of file', None, _formats)[0]
        if fname != '':
            SCAN_SETTINGS.import_from_file(fname)
            for param in SCAN_SETTINGS.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    def export_to_file(self):
        """
        Save ScanSettings to a file.

        This method will open a QFileDialog to select a filename for the
        file in which the information shall be written.
        """
        _formats = ScanSettingsIoMeta.get_string_of_formats()
        fname =  QtWidgets.QFileDialog.getSaveFileName(
            self, 'Name of file', None, _formats)[0]
        if fname != '':
            SCAN_SETTINGS.export_to_file(fname)

    def reset_entries(self):
        """
        Reset all ScanSetting entries to their default values.
        """
        SCAN_SETTINGS.restore_all_defaults(True)
        for param in SCAN_SETTINGS.params.values():
            self.param_widgets[param.refkey].set_value(param.value)


if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.s
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.constants.STANDARD_FONT_SIZE

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'),
                       ScanSettingsFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()
