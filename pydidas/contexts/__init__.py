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
Subpackage with pydidas contexts.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import sub-packages:
from . import experiment_context
from . import scan_context

__all__.extend(["experiment_context", "scan_context"])


# import __all__ items from modules:
from .file_dialogues import *


# explicitly import the singleton factories from the subpackages
from .experiment_context import ExperimentContext, ExperimentContextIoMeta
from .scan_context import ScanContext, ScanContextIoMeta

__all__.extend(
    ["ExperimentContext", "ExperimentContextIoMeta", "ScanContext", "ScanContextIoMeta"]
)


# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import file_dialogues

__all__.extend(file_dialogues.__all__)
del file_dialogues