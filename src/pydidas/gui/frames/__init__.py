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
The pydidas.gui.frames subpackage includes all GUI frames which allow to access all of
pydidas's functionality from within a graphical user interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .composite_creator_frame import *
from .data_browsing_frame import *
from .default_frames import *
from .define_diffraction_exp_frame import *
from .define_scan_frame import *
from .directory_spy_frame import *
from .home_frame import *
from .image_math_frame import *
from .pyfai_calib_frame import *
from .quick_integration_frame import *
from .utilities_frame import *
from .view_results_frame import *
from .workflow_edit_frame import *
from .workflow_run_frame import *
from .workflow_test_frame import *


__all__ = (
    composite_creator_frame.__all__
    + data_browsing_frame.__all__
    + define_diffraction_exp_frame.__all__
    + default_frames.__all__
    + define_scan_frame.__all__
    + directory_spy_frame.__all__
    + home_frame.__all__
    + image_math_frame.__all__
    + pyfai_calib_frame.__all__
    + quick_integration_frame.__all__
    + utilities_frame.__all__
    + view_results_frame.__all__
    + workflow_edit_frame.__all__
    + workflow_run_frame.__all__
    + workflow_test_frame.__all__
)

# Clean up the namespace
del (
    composite_creator_frame,
    data_browsing_frame,
    define_diffraction_exp_frame,
    default_frames,
    define_scan_frame,
    directory_spy_frame,
    home_frame,
    image_math_frame,
    pyfai_calib_frame,
    quick_integration_frame,
    utilities_frame,
    view_results_frame,
    workflow_edit_frame,
    workflow_run_frame,
    workflow_test_frame,
)
