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
The multiprocessing module includes functionalities to run scripts and
applications in parallel procesing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .app_processor_ import *
from .app_processor_without_tasks_ import *
from .processor_ import *
from .app_runner import *
from .worker_controller import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import app_processor_
__all__.extend(app_processor_.__all__)
del app_processor_

from . import app_processor_without_tasks_
__all__.extend(app_processor_without_tasks_.__all__)
del app_processor_without_tasks_

from . import processor_
__all__.extend(processor_.__all__)
del processor_

from . import app_runner
__all__.extend(app_runner.__all__)
del app_runner

from . import worker_controller
__all__.extend(worker_controller.__all__)
del worker_controller
