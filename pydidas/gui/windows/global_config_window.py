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
Module with the GlobalConfigWindow class which is a QMainWindow widget
to view and modify the global settings in a seperate Window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GlobalConfigWindow"]


from ..frames.global_configuration_frame import GlobalConfigurationFrame
from .pydidas_window import PydidasWindowMixIn


class GlobalConfigWindow(GlobalConfigurationFrame, PydidasWindowMixIn):
    """
    The GlobalConfigWindow is a standalone QMainWindow with the
    GlobalConfigurationFrame as sole content.
    """

    def __init__(self, parent=None, **kwargs):
        GlobalConfigurationFrame.__init__(self, parent, **kwargs)
        PydidasWindowMixIn.__init__(self)
        self.setWindowTitle("pydidas global configuration")
