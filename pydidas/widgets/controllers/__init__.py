# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Package with widget controllers.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .manually_set_beamcenter_controller import *
from .manually_set_integration_roi_controller import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import manually_set_beamcenter_controller

__all__.extend(manually_set_beamcenter_controller.__all__)
del manually_set_beamcenter_controller

from . import manually_set_integration_roi_controller

__all__.extend(manually_set_integration_roi_controller.__all__)
del manually_set_integration_roi_controller
