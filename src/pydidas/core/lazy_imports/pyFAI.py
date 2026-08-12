# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
The pyfai_names module holds names (constants) extracted from pyFAI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "AzimuthalIntegrator",
    "Detector",
    "Distortion",
    "Geometry",
    "PoniFile",
    "convert_from_Fit2d",
    "convert_to_Fit2d",
]

from typing import TYPE_CHECKING

from pydidas.core.lazy_imports.lazy_objects import LazyObject


if TYPE_CHECKING:
    from pyFAI.detectors import Detector
    from pyFAI.distortion import Distortion
    from pyFAI.geometry import Geometry
    from pyFAI.geometry.fit2d import convert_from_Fit2d, convert_to_Fit2d
    from pyFAI.integrator.azimuthal import AzimuthalIntegrator
    from pyFAI.io.ponifile import PoniFile
else:
    Detector = LazyObject("pyFAI.detectors", "Detector")
    Distortion = LazyObject("pyFAI.distortion", "Distortion")
    Geometry = LazyObject("pyFAI.geometry.core", "Geometry")
    AzimuthalIntegrator = LazyObject(
        "pyFAI.integrator.azimuthal", "AzimuthalIntegrator"
    )
    PoniFile = LazyObject("pyFAI.io.ponifile", "PoniFile")
    convert_from_Fit2d = LazyObject("pyFAI.geometry.fit2d", "convert_from_Fit2d")
    convert_to_Fit2d = LazyObject("pyFAI.geometry.fit2d", "convert_to_Fit2d")
