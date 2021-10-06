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

"""
Module with the create_scan_settings_frame_widgets_and_layout function
which is used to populate the ScanSettingsFrame with widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_scan_settings_frame_widgets_and_layout']


from pydidas.core import ScanSettings

SCAN_SETTINGS = ScanSettings()


def create_scan_settings_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.ScanSettingsFrame
        The ScanSettingsFrame instance.
    """
    frame._widgets = {}
    _width_total = frame.TEXT_WIDTH + frame.PARAM_INPUT_WIDTH + 10

    frame.create_label('label_title', 'Scan settings\n', fontsize=14,
                      bold=True, underline=True, gridPos=(0, 0, 1, 1))
    frame.create_button('but_load', 'Load scan parameters from file',
                       gridPos=(-1, 0, 1, 1), alignment=None,
                       icon=frame.style().standardIcon(42))
    frame.create_button('but_import', 'Open scan parameter import dialogue',
                       gridPos=(-1, 0, 1, 1), alignment=None,
                       icon=frame.style().standardIcon(42))
    frame.create_label('scan_dim', '\nScan dimensionality:', fontsize=11,
                     bold=True, gridPos=(frame.next_row(), 0, 1, 1))

    param = SCAN_SETTINGS.get_param('scan_dim')
    frame.create_param_widget(param, width_text = frame.TEXT_WIDTH,
                             width_io=frame.PARAM_INPUT_WIDTH,
                             width_total=_width_total, width_unit=0)
    frame.param_widgets['scan_dim'].currentTextChanged.connect(
        frame.toggle_dims)

    _rowoffset = frame.next_row()
    _prefixes = ['scan_dir_', 'n_points_', 'delta_', 'unit_', 'offset_']
    for i_dim in range(4):
        frame.create_label(
            f'title_{i_dim + 1}', f'\nScan dimension {i_dim+1}:',
            fontsize=11, bold=True,
            gridPos=(_rowoffset + 6 * (i_dim % 2), 2 * (i_dim // 2), 1, 2))
        for i_item, basename in enumerate(_prefixes):
            _row = i_item + _rowoffset + 1 + 6 * (i_dim % 2)
            _column = 2 * (i_dim // 2)
            pname = f'{basename}{i_dim+1}'
            param = SCAN_SETTINGS.get_param(pname)
            frame.create_param_widget(param, row=_row, column=_column,
                                     width_text=frame.TEXT_WIDTH,
                                     width_io=frame.PARAM_INPUT_WIDTH,
                                     width_unit=0,
                                     width_total=_width_total)
    frame.create_spacer('final_spacer', gridPos=(_rowoffset + 1, 2, 1, 1))
