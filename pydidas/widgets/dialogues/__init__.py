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

"""Subpackage with PyQt dialogues."""


from . import warning_box
from .warning_box import *

from . import error_message_box
from .error_message_box import *

from . import hdf5_dataset_selection_popup
from .hdf5_dataset_selection_popup import *

from . import critical_warning
from .critical_warning import *

__all__ = []
__all__ += warning_box.__all__
__all__ += error_message_box.__all__
__all__ += hdf5_dataset_selection_popup.__all__
__all__ += critical_warning.__all__


# remove modules from namespace after importing their content
del warning_box
del error_message_box
del hdf5_dataset_selection_popup
del critical_warning
