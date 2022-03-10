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
The apps.parsers subpackage includes parsers to allow running apps on the
command line with command-line calling arguments.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []




# import __all__ items from modules:
from .composite_creator_app_parser_ import *
from .directory_spy_app_parser_ import *
from .execute_workflow_app_parser_ import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import composite_creator_app_parser_
__all__.extend(composite_creator_app_parser_.__all__)
del composite_creator_app_parser_

from . import directory_spy_app_parser_
__all__.extend(directory_spy_app_parser_.__all__)
del directory_spy_app_parser_

from . import execute_workflow_app_parser_
__all__.extend(execute_workflow_app_parser_.__all__)
del execute_workflow_app_parser_
