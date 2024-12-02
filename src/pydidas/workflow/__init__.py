# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The workflow package defines classes to create and manage the workflow and
to import / export.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import sub-packages:
from . import result_io
from . import processing_tree_io

__all__.extend(["result_io", "processing_tree_io"])

# import __all__ items from modules:
from .generic_node import *
from .generic_tree import *
from .plugin_position_node import *
from .processing_tree import *
from .workflow_node import *
from .workflow_results import *
from .workflow_results_selector import *
from .workflow_tree import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import generic_node

__all__.extend(generic_node.__all__)
del generic_node

from . import generic_tree

__all__.extend(generic_tree.__all__)
del generic_tree

from . import plugin_position_node

__all__.extend(plugin_position_node.__all__)
del plugin_position_node

from . import processing_tree

__all__.extend(processing_tree.__all__)
del processing_tree

from . import workflow_node

__all__.extend(workflow_node.__all__)
del workflow_node

from . import workflow_results

__all__.extend(workflow_results.__all__)
del workflow_results

from . import workflow_results_selector

__all__.extend(workflow_results_selector.__all__)
del workflow_results_selector

from . import workflow_tree

__all__.extend(workflow_tree.__all__)
del workflow_tree
