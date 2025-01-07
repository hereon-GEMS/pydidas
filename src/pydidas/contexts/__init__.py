# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import sub-packages:
from . import diff_exp, scan

# explicitly import the main context items from the subpackages:
from .diff_exp import (
    DiffractionExperiment,
    DiffractionExperimentContext,
    DiffractionExperimentIo,
)
from .scan import Scan, ScanContext, ScanIo


__all__ = [
    "diff_exp",
    "scan",
    "DiffractionExperimentContext",
    "DiffractionExperiment",
    "DiffractionExperimentIo",
    "ScanContext",
    "ScanIo",
    "Scan",
    "GLOBAL_CONTEXTS",
]

GLOBAL_CONTEXTS = {
    "diffraction_experiment_context": diff_exp.DiffractionExperimentContext(),
    "scan_context": scan.ScanContext(),
}
