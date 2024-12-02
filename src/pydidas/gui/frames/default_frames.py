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
Module with the DEFAULT_FRAMES which lists all of pydidas's generic frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DEFAULT_FRAMES"]


from .data_browsing_frame import DataBrowsingFrame
from .define_diffraction_exp_frame import DefineDiffractionExpFrame
from .define_scan_frame import DefineScanFrame
from .home_frame import HomeFrame
from .image_math_frame import ImageMathFrame
from .pyfai_calib_frame import PyfaiCalibFrame
from .quick_integration_frame import QuickIntegrationFrame
from .utilities_frame import UtilitiesFrame
from .view_results_frame import ViewResultsFrame
from .workflow_edit_frame import WorkflowEditFrame
from .workflow_run_frame import WorkflowRunFrame
from .workflow_test_frame import WorkflowTestFrame


DEFAULT_FRAMES = (
    HomeFrame,
    DataBrowsingFrame,
    PyfaiCalibFrame,
    ImageMathFrame,
    QuickIntegrationFrame,
    DefineDiffractionExpFrame,
    DefineScanFrame,
    WorkflowEditFrame,
    WorkflowTestFrame,
    WorkflowRunFrame,
    ViewResultsFrame,
    UtilitiesFrame,
)
