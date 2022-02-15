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
Module with the ScanSetup_FrameBuilder mix-in class which is used to populate
the ScanSetupFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSetup_FrameBuilder']

from PyQt5 import QtCore

from ...experiment import ScanSetup
from ...widgets.factory import CreateWidgetsMixIn
from ...widgets.parameter_config import ParameterWidgetsMixIn


SCAN_SETTINGS = ScanSetup()


class ScanSetup_FrameBuilder(CreateWidgetsMixIn, ParameterWidgetsMixIn):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.ScanSetupFrame
        The ScanSetupFrame instance.
    """
    TEXT_WIDTH = 200
    PARAM_INPUT_WIDTH = 120

    def __init__(self):
        CreateWidgetsMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
        _width_total = self.TEXT_WIDTH + self.PARAM_INPUT_WIDTH + 10

        self.create_label('label_title', 'Scan settings\n', fontsize=14,
                          bold=True, underline=True, gridPos=(0, 0, 1, 1))
        self.create_button('but_load', 'Load scan settings from file',
                           gridPos=(-1, 0, 1, 1), alignment=None,
                           icon=self.style().standardIcon(42),
                           fixedWidth=_width_total)
        self.create_button('but_import', 'Open scan parameter import dialogue',
                           gridPos=(-1, 0, 1, 1), alignment=None,
                           icon=self.style().standardIcon(42),
                           fixedWidth=_width_total)
        self.create_button('but_reset', 'Reset all scan settings',
                           gridPos=(-1, 0, 1, 1), alignment=None,
                           icon=self.style().standardIcon(59),
                           fixedWidth=_width_total)
        self.create_label('scan_global', '\nGlobal scan parameters:',
                          fontsize=11, bold=True,
                          gridPos=(self.next_row(), 0, 1, 1))

        self.create_param_widget(
            SCAN_SETTINGS.get_param('scan_dim'), width_text = self.TEXT_WIDTH,
            width_io=self.PARAM_INPUT_WIDTH, width_total=_width_total,
            width_unit=0)
        self.create_param_widget(
            SCAN_SETTINGS.get_param('scan_name'), width_text = self.TEXT_WIDTH,
            width_io=_width_total - 20, linebreak=True,
            width_total=_width_total, width_unit=0)

        _rowoffset = self.next_row()
        _prefixes = ['scan_dir_', 'n_points_', 'delta_', 'unit_', 'offset_']
        for i_dim in range(4):
            self.create_label(
                f'title_{i_dim + 1}', f'\nScan dimension {i_dim+1}:',
                fontsize=11, bold=True,
                gridPos=(_rowoffset + 6 * (i_dim % 2), 2 * (i_dim // 2), 1, 2))
            for i_item, basename in enumerate(_prefixes):
                _row = i_item + _rowoffset + 1 + 6 * (i_dim % 2)
                _column = 2 * (i_dim // 2)
                pname = f'{basename}{i_dim+1}'
                param = SCAN_SETTINGS.get_param(pname)
                self.create_param_widget(
                    param, row=_row, column=_column,
                    width_text=self.TEXT_WIDTH + 5, width_unit=0,
                    width_io=self.PARAM_INPUT_WIDTH, width_total=_width_total,
                    halign=QtCore.Qt.AlignCenter)

        self.create_button('but_save', 'Save scan settings',
                            gridPos=(-1, 0, 1, 1), fixedWidth=_width_total,
                            icon=self.style().standardIcon(43))

        self.create_spacer('final_spacer', gridPos=(_rowoffset + 1, 2, 1, 1))
