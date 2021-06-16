# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Package with modified widgets required for creating the graphical user
interface"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# from . import factory

from . import dialogues

from . import param_config

from . import workflow_edit

from . import confirmation_bar
from .confirmation_bar import *

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

from . import hdf_dataset_selector
from .hdf_dataset_selector import *

from . import hdf_dataset_selector_view_only
from .hdf_dataset_selector_view_only import *

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

__all__ += confirmation_bar.__all__
__all__ += plugin_collection_presenter.__all__
__all__ += scroll_area.__all__
__all__ += utilities.__all__
__all__ += workflow_tree_canvas.__all__
__all__ += central_widget_stack.__all__
__all__ += hdf_dataset_selector.__all__
__all__ += hdf_dataset_selector_view_only.__all__
__all__ += qta_button.__all__
__all__ += directory_explorer.__all__
__all__ += info_widget.__all__
__all__ += read_only_text_widget.__all__
__all__ += create_widgets_mixin.__all__
__all__ += base_frame.__all__


# unclutter namespace and remove modules:
del confirmation_bar
del plugin_collection_presenter
del scroll_area
del utilities
del workflow_tree_canvas
del central_widget_stack
del hdf_dataset_selector
del hdf_dataset_selector_view_only
del qta_button
del directory_explorer
del info_widget
del read_only_text_widget
del create_widgets_mixin
del base_frame
