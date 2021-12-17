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
Package with widgets required for editing the workflow and selecting plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .plugin_collection_browser import *
from .plugin_collection_tree_widget import *
from .plugin_in_workflow_box import *
from .workflow_tree_canvas import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import plugin_collection_browser
__all__.extend(plugin_collection_browser.__all__)
del plugin_collection_browser

from . import plugin_collection_tree_widget
__all__.extend(plugin_collection_tree_widget.__all__)
del plugin_collection_tree_widget

from . import plugin_in_workflow_box
__all__.extend(plugin_in_workflow_box.__all__)
del plugin_in_workflow_box

from . import workflow_tree_canvas
__all__.extend(workflow_tree_canvas.__all__)
del workflow_tree_canvas
