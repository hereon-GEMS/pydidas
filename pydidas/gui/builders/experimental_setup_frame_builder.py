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
Module with the ExperimentalSetupself_BuilderMixin class which is used to
populate the ExperimentSettingsself with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSetupFrameBuilder']

from ...widgets import BaseFrame


class ExperimentalSetupFrameBuilder(BaseFrame):
    """
    Mix-in class which includes the build_self method to populate the
    base class's UI and initialize all widgets.
    """
    def __init__(self, parent=None):
        BaseFrame.__init__(self, parent)
        self.layout().setContentsMargins(5, 5, 0, 0)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(None, 'Experimental settings\n', fontsize=14,
                          bold=True, underline=True, gridPos=(0, 0, 1, 0))
        self.create_button('but_load_from_file',
                           'Load experimental parameters from file',
                           icon=self.style().standardIcon(42),
                           gridPos=(-1, 0, 1, 1), alignment=None)
        self.create_button('but_copy_from_pyfai',
                           'Copy all experimental parameters from calibration',
                           gridPos=(-1, 0, 1, 1), alignment=None)

        for _param in self.params.values():
            if _param.refkey == 'xray_wavelength':
                self.__create_xray_header()
            if _param.refkey == 'detector_name':
                self.__create_detector_header()
            if _param.refkey == 'detector_dist':
                self.__create_geometry_header()
            self.create_param_widget(_param, width_text=180, width_io=150,
                                     width_total=360)

        self.create_spacer(None, gridPos=(-1, 0, 1, 1))
        self.create_button('but_save_to_file',
                           'Save experimental parameters to file',
                           gridPos=(-1, 0, 1, 1), alignment=None,
                           icon=self.style().standardIcon(43))

    def __create_xray_header(self):
        """
        Create header items (label / buttons) for X-ray energy settings.
        """
        self.create_label(None, '\nBeamline X-ray energy:', fontsize=11,
                          bold=True, gridPos=(-1, 0, 1, 1))
        self.create_button('but_copy_energy_from_pyfai',
                           'Copy X-ray energy from pyFAI calibration',
                           gridPos=(-1, 0, 1, 1), alignment=None)

    def __create_detector_header(self):
        """
        Create header items (label / buttons) for the detector.
        """
        self.create_label(None, '\nX-ray detector:', fontsize=11, bold=True,
                          gridPos=(-1, 0, 1, 1))
        self.create_button('but_select_detector',
                            'Select X-ray detector', gridPos=(-1, 0, 1, 1),
                            alignment=None)
        self.create_button('but_copy_det_from_pyfai',
                            'Copy X-ray detector from pyFAI calibration',
                            gridPos=(-1, 0, 1, 1), alignment=None)

    def __create_geometry_header(self):
        """
        Create header items (label / buttons) for the detector.
        """
        self.create_label(None, '\nDetector geometry:', fontsize=11,
                          bold=True, gridPos=(-1, 0, 1, 1))
        self.create_button(
            'but_copy_geo_from_pyfai',
            'Copy X-ray detector geometry from pyFAI calibration',
            gridPos=(-1, 0, 1, 1))
