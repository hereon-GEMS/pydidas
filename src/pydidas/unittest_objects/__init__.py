# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .create_dataset_ import *
from .create_dummy_plugins import *
from .create_hdf5_io_file_ import *
from .dummy_loader import *
from .dummy_proc import *
from .dummy_proc_new_dataset import *
from .local_plugin_collection import *
from .mp_test_app import *


__all__ = (
    create_dataset_.__all__
    + create_dummy_plugins.__all__
    + create_hdf5_io_file_.__all__
    + dummy_loader.__all__
    + dummy_proc.__all__
    + dummy_proc_new_dataset.__all__
    + local_plugin_collection.__all__
    + mp_test_app.__all__
)

del (
    create_dataset_,
    create_dummy_plugins,
    create_hdf5_io_file_,
    dummy_loader,
    dummy_proc,
    dummy_proc_new_dataset,
    local_plugin_collection,
    mp_test_app,
)
