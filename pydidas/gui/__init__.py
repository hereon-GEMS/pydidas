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
Subpackage with GUI elements.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

#import subpackages
from . import builders

from . import mixins

# import modules:
from . import main_window
from .main_window import *

from . import workflow_tree_edit_manager
from .workflow_tree_edit_manager import *

from . import data_browsing_frame
from .data_browsing_frame import *

from . import workflow_edit_frame
from .workflow_edit_frame import *

from . import experiment_settings_frame
from .experiment_settings_frame import *

from . import scan_settings_frame
from .scan_settings_frame import *

from . import processing_single_plugin_frame
from .processing_single_plugin_frame import *

from . import execute_workflow_frame
from .execute_workflow_frame import *

from . import composite_creator_frame
from .composite_creator_frame import *

from . import global_configuration_frame
from .global_configuration_frame import *

# Add all modules' __all__ to the package's __all__
for _module in [
        main_window, workflow_tree_edit_manager, data_browsing_frame,
        workflow_edit_frame, experiment_settings_frame, scan_settings_frame,
        processing_single_plugin_frame, execute_workflow_frame,
        composite_creator_frame, global_configuration_frame]:
    __all__ += _module.__all__

# Unclutter namespace: remove modules from namespace
del main_window
del workflow_tree_edit_manager
del data_browsing_frame
del workflow_edit_frame
del experiment_settings_frame
del scan_settings_frame
del processing_single_plugin_frame
del execute_workflow_frame
del composite_creator_frame
del global_configuration_frame
