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
Subpackage with GUI element and managers to access all of pydidas's
functionality from within a graphical user interface.
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
from . import managers
from . import mixins
from . import windows
__all__.extend(['builders', 'managers', 'mixins', 'windows'])

# import __all__ items from modules:
from .composite_creator_frame import *
from .data_browsing_frame import *
from .execute_workflow_frame import *
from .experimental_setup_frame import *
from .global_configuration_frame import *
from .home_frame import *
from .main_window import *
from .processing_single_plugin_frame import *
from .pyfai_calib_frame import *
from .scan_setup_frame import *
from .workflow_edit_frame import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import composite_creator_frame
__all__.extend(composite_creator_frame.__all__)
del composite_creator_frame

from . import data_browsing_frame
__all__.extend(data_browsing_frame.__all__)
del data_browsing_frame

from . import execute_workflow_frame
__all__.extend(execute_workflow_frame.__all__)
del execute_workflow_frame

from . import experimental_setup_frame
__all__.extend(experimental_setup_frame.__all__)
del experimental_setup_frame

from . import global_configuration_frame
__all__.extend(global_configuration_frame.__all__)
del global_configuration_frame

from . import home_frame
__all__.extend(home_frame.__all__)
del home_frame

from . import main_window
__all__.extend(main_window.__all__)
del main_window

from . import processing_single_plugin_frame
__all__.extend(processing_single_plugin_frame.__all__)
del processing_single_plugin_frame

from . import pyfai_calib_frame
__all__.extend(pyfai_calib_frame.__all__)
del pyfai_calib_frame

from . import scan_setup_frame
__all__.extend(scan_setup_frame.__all__)
del scan_setup_frame

from . import workflow_edit_frame
__all__.extend(workflow_edit_frame.__all__)
del workflow_edit_frame
