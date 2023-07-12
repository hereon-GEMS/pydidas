# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .button_factory import *
from .check_box_factory import *
from .combobox_factory import *
from .create_widgets_mixin import *
from .empty_widget_factory import *
from .label_factory import *
from .line_factory import *
from .lineedit_factory import *
from .progress_bar_factory import *
from .radio_button_group_factory import *
from .spacer_factory import *
from .spin_box_factory import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import button_factory

__all__.extend(button_factory.__all__)
del button_factory

from . import check_box_factory

__all__.extend(check_box_factory.__all__)
del check_box_factory

from . import combobox_factory

__all__.extend(combobox_factory.__all__)
del combobox_factory

from . import create_widgets_mixin

__all__.extend(create_widgets_mixin.__all__)
del create_widgets_mixin

from . import empty_widget_factory

__all__.extend(empty_widget_factory.__all__)
del empty_widget_factory

from . import label_factory

__all__.extend(label_factory.__all__)
del label_factory

from . import line_factory

__all__.extend(line_factory.__all__)
del line_factory

from . import lineedit_factory

__all__.extend(lineedit_factory.__all__)
del lineedit_factory

from . import progress_bar_factory

__all__.extend(progress_bar_factory.__all__)
del progress_bar_factory

from . import radio_button_group_factory

__all__.extend(radio_button_group_factory.__all__)
del radio_button_group_factory

from . import spacer_factory

__all__.extend(spacer_factory.__all__)
del spacer_factory

from . import spin_box_factory

__all__.extend(spin_box_factory.__all__)
del spin_box_factory
