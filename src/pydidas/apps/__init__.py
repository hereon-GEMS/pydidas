# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import sub-packages:
from . import parsers

# import __all__ items from modules:
from .composite_creator_app import *
from .directory_spy_app import *
from .execute_workflow_app import *
from .execute_workflow_runner import *


__all__ = ["parsers"] + (
    composite_creator_app.__all__
    + directory_spy_app.__all__
    + execute_workflow_app.__all__
    + execute_workflow_runner.__all__
)

del (
    composite_creator_app,
    directory_spy_app,
    execute_workflow_app,
    execute_workflow_runner,
)
