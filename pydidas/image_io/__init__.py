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
The image_io subpackage includes functionality to load and save data in
various formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import sub-packages:
from . import implementations
from . import low_level_readers

# import __all__ items from modules:
from .composite_image import *
from .export_image_ import *
from .image_reader import *
from .image_reader_collection import *
from .read_image_ import *
from .rebin_2d import *
from .roi_controller import *
from .roi_controller_1d import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import composite_image
__all__.extend(composite_image.__all__)
del composite_image

from . import export_image_
__all__.extend(export_image_.__all__)
del export_image_

from . import image_reader
__all__.extend(image_reader.__all__)
del image_reader

from . import image_reader_collection
__all__.extend(image_reader_collection.__all__)
del image_reader_collection

from . import read_image_
__all__.extend(read_image_.__all__)
del read_image_

from . import rebin_2d
__all__.extend(rebin_2d.__all__)
del rebin_2d

from . import roi_controller
__all__.extend(roi_controller.__all__)
del roi_controller

from . import roi_controller_1d
__all__.extend(roi_controller_1d.__all__)
del roi_controller_1d
