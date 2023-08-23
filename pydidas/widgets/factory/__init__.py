# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The pydidas.widgets.factory subpackage includes factory functions for widget creation.
It also includes the CreateWidgetsMixin class which allows other classes easy access
to simplified widget creation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import __all__ items from modules:
from .create_widgets_mixin import *
from .empty_widget import *
from .pydidas_checkbox import *
from .pydidas_combobox import *
from .pydidas_label import *
from .pydidas_lineedit import *
from .pydidas_square_button import *
from .pydidas_widget_with_gridlayout import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:

from . import create_widgets_mixin

__all__.extend(create_widgets_mixin.__all__)
del create_widgets_mixin

from . import empty_widget

__all__.extend(empty_widget.__all__)
del empty_widget

from . import pydidas_checkbox

__all__.extend(pydidas_checkbox.__all__)
del pydidas_checkbox

from . import pydidas_combobox

__all__.extend(pydidas_combobox.__all__)
del pydidas_combobox

from . import pydidas_label

__all__.extend(pydidas_label.__all__)
del pydidas_label

from . import pydidas_lineedit

__all__.extend(pydidas_lineedit.__all__)
del pydidas_lineedit

from . import pydidas_square_button

__all__.extend(pydidas_square_button.__all__)
del pydidas_square_button

from . import pydidas_widget_with_gridlayout

__all__.extend(pydidas_widget_with_gridlayout.__all__)
del pydidas_widget_with_gridlayout
