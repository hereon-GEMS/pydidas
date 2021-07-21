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

"""
image_reader subpackage which is used for loading images.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import implementations

from . import image_reader_factory
from .image_reader_factory import *

from . import image_reader
from .image_reader import *

from . import _read_image
from ._read_image import *

from . import _export_image
from ._export_image import *

from . import rebin_2d
from .rebin_2d import *

__all__ += image_reader_factory.__all__
__all__ += image_reader.__all__
__all__ += _read_image.__all__
__all__ += _export_image.__all__
__all__ += rebin_2d.__all__

# Unclutter namespace: remove modules from namespace
del image_reader_factory
del image_reader
del _read_image
del _export_image
del rebin_2d
