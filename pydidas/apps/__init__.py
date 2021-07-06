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

"""Subpackage with GUI elements."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import app_utils

from . import composite_creator_app
from .composite_creator_app import *

from . import base_app
from .base_app import *

# from . import parameter
# from .parameter import *

# from . import parameter_collection
# from .parameter_collection import *

# from . import dataset
# from .dataset import *

# from . import global_settings
# from .global_settings import *

# from . import experimental_settings
# from .experimental_settings import *

# from . import scan_settings
# from .scan_settings import *

# from . import hdf_key
# from .hdf_key import *

__all__ += composite_creator_app.__all__
__all__ += base_app.__all__
# __all__ += parameter_collection.__all__
# __all__ += parameter.__all__
# __all__ += dataset.__all__
# __all__ += global_settings.__all__
# __all__ += experimental_settings.__all__
# __all__ += scan_settings.__all__
# __all__ += hdf_key.__all__

# Unclutter namespace: remove modules from namespace
del composite_creator_app
del base_app
# del dataset
# del global_settings
# del experimental_settings
# del scan_settings
# del hdf_key
# del parameter_collection
