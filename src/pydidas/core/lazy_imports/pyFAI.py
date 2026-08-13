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
The pyfai module holds functions and classes exposed by the pyFAI package,
which are lazily imported to reduce initial loading time.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "AzimuthalIntegrator",
    "CalibWindowMenuItem",
    "CalibrationContext",
    "Detector",
    "Distortion",
    "ExperimentTask",
    "Geometry",
    "GeometryTask",
    "IntegrationTask",
    "MaskTask",
    "PeakPickingTask",
    "PixelMarker",
    "PoniFile",
    "convert_from_Fit2d",
    "convert_to_Fit2d",
    "get_documentation_url",
    "silx_integration",
]


from typing import TYPE_CHECKING

from pydidas.core.lazy_imports.lazy_objects import LazyObject


if TYPE_CHECKING:
    from pyFAI.detectors import Detector
    from pyFAI.distortion import Distortion
    from pyFAI.geometry import Geometry
    from pyFAI.geometry.fit2d import convert_from_Fit2d, convert_to_Fit2d
    from pyFAI.gui.CalibrationContext import CalibrationContext
    from pyFAI.gui.CalibrationWindow import MenuItem as CalibWindowMenuItem
    from pyFAI.gui.model.MarkerModel import PixelMarker
    from pyFAI.gui.tasks.ExperimentTask import ExperimentTask
    from pyFAI.gui.tasks.GeometryTask import GeometryTask
    from pyFAI.gui.tasks.IntegrationTask import IntegrationTask
    from pyFAI.gui.tasks.MaskTask import MaskTask
    from pyFAI.gui.tasks.PeakPickingTask import PeakPickingTask
    from pyFAI.gui.utils.projecturl import get_documentation_url
    from pyFAI.integrator.azimuthal import AzimuthalIntegrator
    from pyFAI.io.ponifile import PoniFile
    from pyFAI.resources import silx_integration
else:
    # base classes:
    AzimuthalIntegrator = LazyObject(
        "pyFAI.integrator.azimuthal", "AzimuthalIntegrator"
    )
    Detector = LazyObject("pyFAI.detectors", "Detector")
    Distortion = LazyObject("pyFAI.distortion", "Distortion")
    Geometry = LazyObject("pyFAI.geometry.core", "Geometry")

    # Contexts
    CalibrationContext = LazyObject(
        "pyFAI.gui.CalibrationContext", "CalibrationContext"
    )

    # GUI classes:
    CalibWindowMenuItem = LazyObject("pyFAI.gui.CalibrationWindow", "MenuItem")
    GeometryTask = LazyObject("pyFAI.gui.tasks.GeometryTask", "GeometryTask")
    ExperimentTask = LazyObject("pyFAI.gui.tasks.ExperimentTask", "ExperimentTask")
    IntegrationTask = LazyObject("pyFAI.gui.tasks.IntegrationTask", "IntegrationTask")
    MaskTask = LazyObject("pyFAI.gui.tasks.MaskTask", "MaskTask")
    PeakPickingTask = LazyObject("pyFAI.gui.tasks.PeakPickingTask", "PeakPickingTask")
    PixelMarker = LazyObject("pyFAI.gui.model.MarkerModel", "PixelMarker")

    # utilities:
    PoniFile = LazyObject("pyFAI.io.ponifile", "PoniFile")
    convert_from_Fit2d = LazyObject("pyFAI.geometry.fit2d", "convert_from_Fit2d")
    convert_to_Fit2d = LazyObject("pyFAI.geometry.fit2d", "convert_to_Fit2d")
    get_documentation_url = LazyObject(
        "pyFAI.gui.utils.projecturl", "get_documentation_url"
    )
    silx_integration = LazyObject("pyFAI.resources", "silx_integration")
