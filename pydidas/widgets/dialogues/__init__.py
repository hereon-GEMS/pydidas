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
Subpackage with PyQt dialogues.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .critical_warning_ import *
from .error_message_box import *
from .hdf5_dataset_selection_popup import *
from .question_box import *
from .warning_box import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import critical_warning_
__all__.extend(critical_warning_.__all__)
del critical_warning_

from . import error_message_box
__all__.extend(error_message_box.__all__)
del error_message_box

from . import hdf5_dataset_selection_popup
__all__.extend(hdf5_dataset_selection_popup.__all__)
del hdf5_dataset_selection_popup

from . import question_box
__all__.extend(question_box.__all__)
del question_box

from . import warning_box
__all__.extend(warning_box.__all__)
del warning_box
