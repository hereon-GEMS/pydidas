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
Module with the create_global_configurataion_frame_widgets_and_layout
function which is used to populate the GlobalConfigurationFrame with
widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_global_configuratation_frame_widgets_and_layout']


from PyQt5 import QtCore


def create_global_configuratation_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.GlobalConfigurationFrame
        The GlobalConfigurationFrame instance.
    """
    frame._widgets = {}
    _twoline_options = dict(width_text=frame.TEXT_WIDTH, width_io=240,
                            linebreak=True, width_total=300,
                            halign_text=QtCore.Qt.AlignLeft,
                            valign_text=QtCore.Qt.AlignBottom)
    _options = dict(width_text=frame.TEXT_WIDTH, width_io=80, width_total=300)
    _section_options = dict(fontsize=13, bold=True, gridPos=(-1, 0, 1, 0))

    frame.create_label('title', 'Global settings\n', fontsize=14,
                      bold=True, gridPos=(0, 0, 1, 0))

    frame.create_button('but_reset', 'Restore defaults',
                       icon=frame.style().standardIcon(59),
                       gridPos=(-1, 0, 1, 0), alignment=None)

    frame.create_label('section_multiprocessing',
                      'Multiprocessing settings', **_section_options)
    frame.create_param_widget(frame.params.get_param('mp_n_workers'),
                              **_options)
    frame.create_param_widget(frame.params.get_param('shared_buffer_size'),
                              **_options)
    frame.create_spacer('spacer_1')

    frame.create_label('section_detector', 'Detector settings',
                      **_section_options)
    frame.create_param_widget(frame.params.get_param('det_mask'),
                              **_twoline_options)
    frame.create_param_widget(frame.params.get_param('det_mask_val'),
                              **_options)
    frame.create_spacer('spacer_2')

    frame.create_label('section_mosaic', 'Composite creator settings',
                      **_section_options)
    frame.create_param_widget(frame.params.get_param('mosaic_border_width'),
                              **_options)
    frame.create_param_widget(frame.params.get_param('mosaic_border_value'),
                              **_options)
    frame.create_param_widget(frame.params.get_param('mosaic_max_size'),
                              **_options)
    frame.create_spacer('spacer_3')
