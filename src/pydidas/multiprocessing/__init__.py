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
The pydidas.multiprocessing module includes functionalities to run scripts and
applications in parallel procesing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import __all__ items from modules:
from .app_processor_ import *
from .processor_ import *
from .app_runner import *
from .worker_controller import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import app_processor_

__all__.extend(app_processor_.__all__)
del app_processor_

from . import processor_

__all__.extend(processor_.__all__)
del processor_

from . import app_runner

__all__.extend(app_runner.__all__)
del app_runner

from . import worker_controller

__all__.extend(worker_controller.__all__)
del worker_controller
