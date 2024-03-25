# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
Subpackage with pydidas contexts.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import sub-packages:
from . import diff_exp
from . import scan

__all__.extend(["diff_exp", "scan"])


# import __all__ items from modules:

# explicitly import the singleton factories from the subpackages
from .diff_exp import (
    DiffractionExperiment,
    DiffractionExperimentContext,
    DiffractionExperimentIo,
)
from .scan import ScanContext, ScanIo, Scan

__all__.extend(
    [
        "DiffractionExperimentContext",
        "DiffractionExperimentIo",
        "ScanContext",
        "ScanIo",
    ]
)

GLOBAL_CONTEXTS = {
    "diffraction_experiment_context": DiffractionExperimentContext(),
    "scan_context": ScanContext(),
}

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
