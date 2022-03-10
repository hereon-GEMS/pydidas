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
The gui.builders sub-package includes builders for all GUI classes. The
builders to create and arrange the widgets have been separated simply for
improved code organisation. They will create the user interface "shells"
without any connections and functionality.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .composite_creator_frame_builder import *
from .data_browsing_frame_builder import *
from .execute_workflow_frame_builder import *
from .experimental_setup_frame_builder import *
from .global_configuration_frame_builder import *
from .image_math_frame_builder import *
from .processing_single_plugin_frame_builder import *
from .scan_setup_frame_builder import *
from .workflow_edit_frame_builder import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import composite_creator_frame_builder
__all__.extend(composite_creator_frame_builder.__all__)
del composite_creator_frame_builder

from . import data_browsing_frame_builder
__all__.extend(data_browsing_frame_builder.__all__)
del data_browsing_frame_builder

from . import execute_workflow_frame_builder
__all__.extend(execute_workflow_frame_builder.__all__)
del execute_workflow_frame_builder

from . import experimental_setup_frame_builder
__all__.extend(experimental_setup_frame_builder.__all__)
del experimental_setup_frame_builder

from . import global_configuration_frame_builder
__all__.extend(global_configuration_frame_builder.__all__)
del global_configuration_frame_builder

from . import image_math_frame_builder
__all__.extend(image_math_frame_builder.__all__)
del image_math_frame_builder

from . import processing_single_plugin_frame_builder
__all__.extend(processing_single_plugin_frame_builder.__all__)
del processing_single_plugin_frame_builder

from . import scan_setup_frame_builder
__all__.extend(scan_setup_frame_builder.__all__)
del scan_setup_frame_builder

from . import workflow_edit_frame_builder
__all__.extend(workflow_edit_frame_builder.__all__)
del workflow_edit_frame_builder
