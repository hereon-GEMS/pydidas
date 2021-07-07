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

"""Subpackage with GUI elements."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import builders

from . import workflow_tree_edit_manager
from .workflow_tree_edit_manager import *

from . import data_browsing_frame
from .data_browsing_frame import *

from . import workflow_edit_frame
from .workflow_edit_frame import *

from . import base_frame
from .base_frame import *

from . import experiment_settings_frame
from .experiment_settings_frame import *

from . import scan_settings_frame
from .scan_settings_frame import *

from . import processing_single_plugin_frame
from .processing_single_plugin_frame import *

from . import processing_full_workflow
from .processing_full_workflow import *

from . import composite_creator_frame
from .composite_creator_frame import *

__all__ += workflow_tree_edit_manager.__all__
__all__ += data_browsing_frame.__all__
__all__ += workflow_edit_frame.__all__
__all__ += base_frame.__all__
__all__ += experiment_settings_frame.__all__
__all__ += scan_settings_frame.__all__
__all__ += processing_single_plugin_frame.__all__
__all__ += processing_full_workflow.__all__
__all__ += composite_creator_frame.__all__

# Unclutter namespace: remove modules from namespace
del workflow_tree_edit_manager
del data_browsing_frame
del workflow_edit_frame
del base_frame
del experiment_settings_frame
del scan_settings_frame
del processing_single_plugin_frame
del processing_full_workflow
del composite_creator_frame
