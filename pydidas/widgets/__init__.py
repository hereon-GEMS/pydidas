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

"""Package with modified widgets required for creating the graphical user
interface"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import windows

from . import factory

from . import dialogues

from . import parameter_config

from . import workflow_edit

# from . import confirmation_bar
# from .confirmation_bar import *

from . import plugin_collection_presenter
from .plugin_collection_presenter import *

from . import scroll_area
from .scroll_area import *

from . import utilities
from .utilities import *

from . import workflow_tree_canvas
from .workflow_tree_canvas import *

from . import central_widget_stack
from .central_widget_stack import *

# from . import hdf_dataset_selector
# from .hdf_dataset_selector import *

from . import hdf5_dataset_selector
from .hdf5_dataset_selector import *

from . import qta_button
from .qta_button import *

from . import directory_explorer
from .directory_explorer import *

from . import info_widget
from .info_widget import *

from . import read_only_text_widget
from .read_only_text_widget import *

from . import create_widgets_mixin
from .create_widgets_mixin import *

from . import base_frame
from .base_frame import *

from . import base_frame_with_app
from .base_frame_with_app import *

# __all__ += confirmation_bar.__all__
__all__ += plugin_collection_presenter.__all__
__all__ += scroll_area.__all__
__all__ += utilities.__all__
__all__ += workflow_tree_canvas.__all__
__all__ += central_widget_stack.__all__
# __all__ += hdf_dataset_selector.__all__
__all__ += hdf5_dataset_selector.__all__
__all__ += qta_button.__all__
__all__ += directory_explorer.__all__
__all__ += info_widget.__all__
__all__ += read_only_text_widget.__all__
__all__ += create_widgets_mixin.__all__
__all__ += base_frame.__all__
__all__ += base_frame_with_app.__all__



# unclutter namespace and remove modules:
# del confirmation_bar
del plugin_collection_presenter
del scroll_area
del utilities
del workflow_tree_canvas
del central_widget_stack
# del hdf_dataset_selector
del hdf5_dataset_selector
del qta_button
del directory_explorer
del info_widget
del read_only_text_widget
del create_widgets_mixin
del base_frame
del base_frame_with_app
