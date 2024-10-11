# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Subpackage with unittest objects. These object are included in the main
distribution to have them in correct version control. They have no use
apart from substituting for other object in unittests.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import __all__ items from modules:
from .create_dummy_plugins import *
from .create_hdf5_io_file_ import *
from .dummy_loader import *
from .dummy_proc import *
from .dummy_proc_new_dataset import *
from .local_plugin_collection import *
from .mp_test_app import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import create_dummy_plugins

__all__.extend(create_dummy_plugins.__all__)
del create_dummy_plugins

from . import create_hdf5_io_file_

__all__.extend(create_hdf5_io_file_.__all__)
del create_hdf5_io_file_

from . import dummy_loader

__all__.extend(dummy_loader.__all__)
del dummy_loader

from . import dummy_proc

__all__.extend(dummy_proc.__all__)
del dummy_proc

from . import dummy_proc_new_dataset

__all__.extend(dummy_proc_new_dataset.__all__)
del dummy_proc_new_dataset

from . import local_plugin_collection

__all__.extend(local_plugin_collection.__all__)
del local_plugin_collection

from . import mp_test_app

__all__.extend(mp_test_app.__all__)
del mp_test_app
