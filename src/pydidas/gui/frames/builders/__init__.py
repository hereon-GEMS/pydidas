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
The gui.frames.builders sub-package includes builders for all GUI frame classes.

The builders to create and arrange the widgets have been separated simply for
improved code organisation. They will create the user interface "shells"
without any connections and functionality.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .composite_creator_frame_builder import *
from .data_browsing_frame_builder import *
from .define_diffraction_exp_frame_builder import *
from .define_scan_frame_builder import *
from .image_math_frame_builder import *
from .quick_integration_frame_builder import *
from .utilities_frame_builder import *
from .workflow_edit_frame_builder import *
from .workflow_run_frame_builder import *
from .workflow_test_frame_builder import *


__all__ = (
    composite_creator_frame_builder.__all__
    + data_browsing_frame_builder.__all__
    + image_math_frame_builder.__all__
    + define_diffraction_exp_frame_builder.__all__
    + define_scan_frame_builder.__all__
    + quick_integration_frame_builder.__all__
    + utilities_frame_builder.__all__
    + workflow_edit_frame_builder.__all__
    + workflow_run_frame_builder.__all__
    + workflow_test_frame_builder.__all__
)

# Clean up the namespace
del (
    composite_creator_frame_builder,
    data_browsing_frame_builder,
    image_math_frame_builder,
    define_diffraction_exp_frame_builder,
    define_scan_frame_builder,
    quick_integration_frame_builder,
    utilities_frame_builder,
    workflow_edit_frame_builder,
    workflow_run_frame_builder,
    workflow_test_frame_builder,
)
