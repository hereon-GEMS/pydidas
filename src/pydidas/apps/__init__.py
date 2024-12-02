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
The apps package includes stand-alone applications which can be run from
the command line to perform specific tasks. Integration of apps in the
GUI is included in the gui module.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import sub-packages:
from . import parsers

# import __all__ items from modules:
from .composite_creator_app import *
from .directory_spy_app import *
from .execute_workflow_app import *
from .execute_workflow_runner import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import composite_creator_app

__all__.extend(composite_creator_app.__all__)
del composite_creator_app

from . import directory_spy_app

__all__.extend(directory_spy_app.__all__)
del directory_spy_app

from . import execute_workflow_app

__all__.extend(execute_workflow_app.__all__)
del execute_workflow_app

from . import execute_workflow_runner

__all__.extend(execute_workflow_runner.__all__)
del execute_workflow_runner
