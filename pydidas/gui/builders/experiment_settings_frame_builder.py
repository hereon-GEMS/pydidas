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
Module with the create_experiment_settings_frame_widgets_and_layout
function which is used to populate the ExperimentSettingsFrame with
widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_experiment_settings_frame_widgets_and_layout']


def create_experiment_settings_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.ExperimentSettingsFrame
        The ExperimentSettingsFrame instance.
    """
    def __create_xray_header():
        """Create header items (label / buttons) for X-ray energy settings."""
        frame.create_label(None, '\nBeamline X-ray energy:', fontsize=11,
                          bold=True, gridPos=(-1, 0, 1, 3))
        frame.create_button('but_copy_energy_from_pyfai',
                           'Copy X-ray energy from pyFAI calibration',
                           gridPos=(-1, 0, 1, 3), alignment=None)

    def __create_detector_header():
        """Create header items (label / buttons) for the detector."""
        frame.create_label(None, '\nX-ray detector:', fontsize=11, bold=True,
                          gridPos=(-1, 0, 1, 3))
        frame.create_button('but_select_detector',
                           'Select X-ray detector', gridPos=(-1, 0, 1, 3),
                           alignment=None)
        frame.create_button('but_copy_det_from_pyfai',
                           'Copy X-ray detector from pyFAI calibration',
                           gridPos=(-1, 0, 1, 3), alignment=None)

    def __create_geometry_header():
        """Create header items (label / buttons) for the detector."""
        frame.create_label(None, '\nDetector geometry:', fontsize=11,
                         bold=True, gridPos=(-1, 0, 1, 3))
        frame.create_button(
            'but_copy_geo_from_pyfai',
            'Copy X-ray detector geometry from pyFAI calibration',
            gridPos=(-1, 0, 1, 3))

    def __create_param_widgets(param_key):
        """Create widgets for a Parameter."""
        _row = frame.next_row()
        _param = frame.get_param(param_key)
        frame.create_param_widget(_param, row=_row, textwidth = 180,
                                 width=150)
        frame.create_label(None, _param.unit, gridPos=(_row, 2, 1, 1),
                          fixedWidth=24)
    frame._widgets = {}
    frame.layout().setContentsMargins(5, 5, 0, 0)

    frame.create_label(None, 'Experimental settings\n', fontsize=14,
                       bold=True, underline=True, gridPos=(0, 0, 1, 0))
    frame.create_button('but_load_from_file',
                        'Load experimental parameters from file',
                        icon=frame.style().standardIcon(42),
                        gridPos=(-1, 0, 1, 3), alignment=None)
    frame.create_button('but_copy_from_pyfai',
                        'Copy all experimental parameters from calibration',
                        gridPos=(-1, 0, 1, 3), alignment=None)

    for _param_key in frame.params.keys():
        if _param_key == 'xray_wavelength':
            __create_xray_header()
        if _param_key == 'detector_name':
            __create_detector_header()
        if _param_key == 'detector_dist':
            __create_geometry_header()
        __create_param_widgets(_param_key)

    frame.create_spacer(None, gridPos=(-1, 0, 1, 3))
    frame.create_button('but_save_to_file',
                        'Save experimental parameters to file',
                        gridPos=(-1, 0, 1, 3), alignment=None,
                        icon=frame.style().standardIcon(43))
