# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the GlobalSettings class which is used to manage global
information independant from the individual frames."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSettings']

from .global_settings import _GlobalSettings
from .parameter import Parameter

_tooltips = {
    'scan_dim': ('The scan_dimensionality. This is relevant for mosaic and '
                 'and mesh images.'),
    'scan_dir_1': ('The axis name for scan direction 1. This information will'
                   ' only be used for labelling.'),
    'scan_dir_2': ('The axis name for scan direction 2. This information will'
                   ' only be used for labelling.'),
    'scan_dir_3': ('The axis name for scan direction 3. This information will'
                   ' only be used for labelling.'),
    'scan_dir_4': ('The axis name for scan direction 4. This information will'
                   ' only be used for labelling.'),
    'n_points_1': 'The number of scan points in scan direction 1.',
    'n_points_2': 'The number of scan points in scan direction 2.',
    'n_points_3': 'The number of scan points in scan direction 3.',
    'n_points_4': 'The number of scan points in scan direction 4.',
    'delta_1': 'The step width between two scan points in scan direction 1.',
    'delta_2': 'The step width between two scan points in scan direction 2.',
    'delta_3': 'The step width between two scan points in scan direction 3.',
    'delta_4': 'The step width between two scan points in scan direction 4.',
    'unit_1': 'The unit of the movement / steps / offset in scan direction 1.',
    'unit_2': 'The unit of the movement / steps / offset in scan direction 2.',
    'unit_3': 'The unit of the movement / steps / offset in scan direction 3.',
    'unit_4': 'The unit of the movement / steps / offset in scan direction 4.',
    'offset_1': ('The offset of the movement in scan direction 1 '
                 '(i.e. the position for scan step #0).'),
    'offset_2': ('The offset of the movement in scan direction 2 '
                 '(i.e. the position for scan step #0).'),
    'offset_3': ('The offset of the movement in scan direction 3 '
                 '(i.e. the position for scan step #0).'),
    'offset_4': ('The offset of the movement in scan direction 4 '
                 '(i.e. the position for scan step #0).'),


    'detector_name': 'The detector name in pyFAI nomenclature.',
    'detector_npixx': ('The number of detector pixels in x direction '
                       '(horizontal).'),
    'detector_npixy': ('The number of detector pixels in y direction '
                       '(vertical).'),
    'detector_dx': 'The detector pixel size in X-direction in micrometer.',
    'detector_dy': 'The detector pixel size in Y-direction in micrometer.',
    'detector_dist': 'The sample-detector distance (in m).',
    'detector_poni1': ('The detector PONI1 (point of normal incidence; '
                       'in y direction). This is measured in meters from the'
                       'detector origin.'),
    'detector_poni2': ('The detector PONI2 (point of normal incidence; '
                       'in x direction). This is measured in meters from the'
                       'detector origin.'),
    'detector_rot1': ('The detector rotation 1 (lefthanded around the '
                      '"up"-axis), given in rad.'),
    'detector_rot2': ('The detector rotation 2 (pitching the detector; '
                      'positive direction is tilting the detector towards the'
                      ' floor, i.e. left-handed), given in rad.'),
    'detector_rot3': ('The detector rotation 3 (around the beam axis; '
                      'right-handed when looking downstream with the beam.'
                      'Given in rad.'),
    }

_params = {
    'scan_dim':  Parameter('Scan dimension', int, default=2, refkey='scan_dim',
                           unit='', tooltip=_tooltips['scan_dim'],
                           choices=[1, 2, 3, 4]),
    'scan_dir_1': Parameter('Name of scan direction 1', str, default='', refkey='scan_dir_1',
                           unit='', tooltip=_tooltips['scan_dir_1']),
    'n_points_1': Parameter('Number of scan points (dir. 1)', int, default=0, refkey='n_points_1',
                            unit='', tooltip=_tooltips['n_points_1']),
    'delta_1': Parameter('Step width in direction 1', float, default=0, refkey='delta_1',
                         unit='', tooltip=_tooltips['n_points_1']),
    'unit_1': Parameter('Unit of direction 1', str, default='', refkey='unit_1',
                        unit='', tooltip=_tooltips['unit_1']),
    'offset_1': Parameter('Offset of direction 1', float, default=0, refkey='offset_1',
                          unit='', tooltip=_tooltips['offset_1']),
    'scan_dir_2': Parameter('Name of scan direction 2', str, default='', refkey='scan_dir_2',
                           unit='', tooltip=_tooltips['scan_dir_2']),
    'n_points_2': Parameter('Number of scan points (dir. 2)', int, default=0, refkey='n_points_2',
                            unit='', tooltip=_tooltips['n_points_2']),
    'delta_2': Parameter('Step width in direction 2', float, default=0, refkey='delta_2',
                         unit='', tooltip=_tooltips['n_points_2']),
    'unit_2': Parameter('Unit of direction 2', str, default='', refkey='unit_2',
                        unit='', tooltip=_tooltips['unit_2']),
    'offset_2': Parameter('Offset of direction 2', float, default=0, refkey='offset_2',
                          unit='', tooltip=_tooltips['offset_2']),
    'scan_dir_3': Parameter('Name of scan direction 3', str, default='', refkey='scan_dir_3',
                           unit='', tooltip=_tooltips['scan_dir_3']),
    'n_points_3': Parameter('Number of scan points (dir. 3)', int, default=0, refkey='n_points_3',
                            unit='', tooltip=_tooltips['n_points_3']),
    'delta_3': Parameter('Step width in direction 3', float, default=0, refkey='delta_3',
                         unit='', tooltip=_tooltips['n_points_3']),
    'unit_3': Parameter('Unit of direction 3', str, default='', refkey='unit_3',
                        unit='', tooltip=_tooltips['unit_3']),
    'offset_3': Parameter('Offset of direction 3', float, default=0, refkey='offset_3',
                          unit='', tooltip=_tooltips['offset_3']),
    'scan_dir_4': Parameter('Name of scan direction 4', str, default='', refkey='scan_dir_4',
                           unit='', tooltip=_tooltips['scan_dir_4']),
    'n_points_4': Parameter('Number of scan points (dir. 4)', int, default=0, refkey='n_points_4',
                            unit='', tooltip=_tooltips['n_points_4']),
    'delta_4': Parameter('Step width in direction 4', float, default=0, refkey='delta_4',
                         unit='', tooltip=_tooltips['n_points_4']),
    'unit_4': Parameter('Unit of direction 4', str, default='', refkey='unit_4',
                        unit='', tooltip=_tooltips['unit_4']),
    'offset_4': Parameter('Offset of direction 4', float, default=0, refkey='offset_4',
                          unit='', tooltip=_tooltips['offset_4']),
    }

class _ScanSettings(_GlobalSettings):
    """
    Class which holds experimental settings. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.
    """
    def __init__(self, **kwargs):
        """Setup method"""
        self._params = kwargs.get('params', {})
        for key in _params:
            if not self.key_exists(key):
                self.register_param(key, default_entry=_params[key])


class _ScanSettingsFactory:
    """
    Factory to create a Singleton.
    """
    def __init__(self):
        """
        Setup method.
        """
        self._instance = None

    def __call__(self):
        """
        Get the instance of ExperimentalSettings

        Returns
        -------
        ExperimentalSettings
            The instance of the ExperimentalSettings class.
        """
        if not self._instance:
            self._instance = _ScanSettings()
        return self._instance


ScanSettings = _ScanSettingsFactory()
