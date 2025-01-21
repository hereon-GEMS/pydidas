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
Module with the DEFAULT_FRAMES which lists all of pydidas's generic frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DEFAULT_FRAMES"]


from pydidas.gui.frames.data_browsing_frame import DataBrowsingFrame
from pydidas.gui.frames.define_diffraction_exp_frame import DefineDiffractionExpFrame
from pydidas.gui.frames.define_scan_frame import DefineScanFrame
from pydidas.gui.frames.home_frame import HomeFrame
from pydidas.gui.frames.image_math_frame import ImageMathFrame
from pydidas.gui.frames.pyfai_calib_frame import PyfaiCalibFrame
from pydidas.gui.frames.quick_integration_frame import QuickIntegrationFrame
from pydidas.gui.frames.utilities_frame import UtilitiesFrame
from pydidas.gui.frames.view_results_frame import ViewResultsFrame
from pydidas.gui.frames.workflow_edit_frame import WorkflowEditFrame
from pydidas.gui.frames.workflow_run_frame import WorkflowRunFrame
from pydidas.gui.frames.workflow_test_frame import WorkflowTestFrame


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
