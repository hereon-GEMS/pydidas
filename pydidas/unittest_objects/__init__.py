# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Subpackage with unittest objects."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import dummy_loader
from .dummy_loader import *

from . import dummy_plugin_collection
from .dummy_plugin_collection import *

from . import dummy_proc
from .dummy_proc import *

from . import mp_test_app
from .mp_test_app import *

__all__ += dummy_loader.__all__
__all__ += dummy_plugin_collection.__all__
__all__ += dummy_proc.__all__
__all__ += mp_test_app.__all__

# Unclutter namespace: remove modules from namespace
del dummy_loader
del dummy_plugin_collection
del dummy_proc
del mp_test_app
