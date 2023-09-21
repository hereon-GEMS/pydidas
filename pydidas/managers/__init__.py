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
The pydidas.managers sub-package includes manager classes which handle certain
aspects of pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import __all__ items from modules:
from .composite_image_manager import *
from .filelist_manager import *
from .image_metadata_manager import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import composite_image_manager

__all__.extend(composite_image_manager.__all__)
del composite_image_manager

from . import filelist_manager

__all__.extend(filelist_manager.__all__)
del filelist_manager

from . import image_metadata_manager

__all__.extend(image_metadata_manager.__all__)
del image_metadata_manager
