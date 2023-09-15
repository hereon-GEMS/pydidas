# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Subpackage with PyQt dialogues.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import __all__ items from modules:
from .acknowledge_box import *
from .critical_warning_ import *
from .error_message_box import *
from .hdf5_dataset_selection_popup import *
from .question_box import *
from .user_config_error_message_box import *
from .warning_box import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import acknowledge_box

__all__.extend(acknowledge_box.__all__)
del acknowledge_box

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

from . import user_config_error_message_box

__all__.extend(user_config_error_message_box.__all__)
del user_config_error_message_box

from . import warning_box

__all__.extend(warning_box.__all__)
del warning_box
