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
Package with the workflow tree canvas manager which organizes the widgets
for the individual workflow processing steps.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


from . import plugin_collection_presenter
from .plugin_collection_presenter import *

from . import workflow_plugin_label
from .workflow_plugin_label import *

from . import workflow_tree_canvas
from .workflow_tree_canvas import *

__all__ += plugin_collection_presenter.__all__
__all__ += workflow_plugin_label.__all__
__all__ += workflow_tree_canvas.__all__

# unclutter namespace and remove modules:
del plugin_collection_presenter
del workflow_plugin_label
del workflow_tree_canvas
