# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Package with subclassed silx widgets and actions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import __all__ items from modules:
from .pydidas_masktools_widget import *
from pydidas.widgets.silx_plot.pydidas_plot1d import *
from pydidas.widgets.silx_plot.pydidas_plot2d import *
from .pydidas_plot_stack import *
from pydidas.widgets.silx_plot.pydidas_plot2d_with_integration_regions import *
from .silx_actions import *
from .utilities import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import pydidas_masktools_widget

__all__.extend(pydidas_masktools_widget.__all__)
del pydidas_masktools_widget

from . import pydidas_plot1d

__all__.extend(pydidas_plot1d.__all__)
del pydidas_plot1d

from . import pydidas_plot2d

__all__.extend(pydidas_plot2d.__all__)
del pydidas_plot2d

from . import pydidas_plot_stack

__all__.extend(pydidas_plot_stack.__all__)
del pydidas_plot_stack

from . import pydidas_plot2d_with_integration_regions

__all__.extend(pydidas_plot2d_with_integration_regions.__all__)
del pydidas_plot2d_with_integration_regions

from . import silx_actions

__all__.extend(silx_actions.__all__)
del silx_actions

from . import utilities

__all__.extend(utilities.__all__)
del utilities
