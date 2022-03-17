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
Subpackage with unittest objects. These object are included in the main
distribution to have them in correct version control. They have no use
apart from substituting for other object in unittests.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .create_dummy_plugins import *
from .dummy_loader import *
from .dummy_plugin_collection import *
from .dummy_proc import *
from .mp_test_app import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import create_dummy_plugins
__all__.extend(create_dummy_plugins.__all__)
del create_dummy_plugins

from . import dummy_loader
__all__.extend(dummy_loader.__all__)
del dummy_loader

from . import dummy_plugin_collection
__all__.extend(dummy_plugin_collection.__all__)
del dummy_plugin_collection

from . import dummy_proc
__all__.extend(dummy_proc.__all__)
del dummy_proc

from . import mp_test_app
__all__.extend(mp_test_app.__all__)
del mp_test_app
