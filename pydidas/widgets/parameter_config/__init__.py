# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
Package with individual QWidgets used editing pydidas Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .parameter_widget import *
from .parameter_edit_canvas import *
from .parameter_widgets_mixin import *
from .edit_plugin_parameters_widget import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import parameter_widget

__all__.extend(parameter_widget.__all__)
del parameter_widget

from . import parameter_edit_canvas

__all__.extend(parameter_edit_canvas.__all__)
del parameter_edit_canvas

from . import parameter_widgets_mixin

__all__.extend(parameter_widgets_mixin.__all__)
del parameter_widgets_mixin

from . import edit_plugin_parameters_widget

__all__.extend(edit_plugin_parameters_widget.__all__)
del edit_plugin_parameters_widget
