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
Script to reset all stored QSettings to default in case a setting breaks
the GUI startup.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['clear_pydidas_QSettings']

import sys
import os

from qtpy.QtCore import QSettings

_path = os.path.dirname(__file__)
sys.path.insert(0, _path)


def clear_pydidas_QSettings():
    """
    Clear all stored pydidas QSetting values and write None.
    """
    qs = QSettings('Hereon', 'pydidas')
    for _key in qs.allKeys():
        qs.setValue(_key, None)


if __name__ == '__main__':
    clear_pydidas_QSettings()
