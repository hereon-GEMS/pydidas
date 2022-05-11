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
The gui.windows subpackage includes stand-alone main windows which can
be opened by the main GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .about_window import *
from .average_images_window import *
from .feedback_window import *
from .global_config_window import *
from .export_eiger_pixelmask import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import about_window

__all__.extend(about_window.__all__)
del about_window

from . import average_images_window

__all__.extend(average_images_window.__all__)
del average_images_window

from . import global_config_window

__all__.extend(global_config_window.__all__)
del global_config_window

from . import feedback_window

__all__.extend(feedback_window.__all__)
del feedback_window

from . import export_eiger_pixelmask

__all__.extend(export_eiger_pixelmask.__all__)
del export_eiger_pixelmask
