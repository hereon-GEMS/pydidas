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

"""
The multiprocessing module includes functionalities to run scripts and
applications in parallel procesing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


from . import _processor
from ._processor import *

from . import worker_controller
from .worker_controller import *

from . import app_runner
from .app_runner import *

from . import _app_processor
from ._app_processor import *

__all__ += _processor.__all__
__all__ += worker_controller.__all__
__all__ += app_runner.__all__
__all__ += _app_processor.__all__


# unclutter namespace and delete imported modules
del _processor
del worker_controller
del app_runner
del _app_processor
