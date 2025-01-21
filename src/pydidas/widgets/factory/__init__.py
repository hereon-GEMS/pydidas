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
The pydidas.widgets.factory subpackage includes factory functions for widget creation.
It also includes the CreateWidgetsMixin class which allows other classes easy access
to simplified widget creation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .create_widgets_mixin import *
from .empty_widget import *
from .pydidas_checkbox import *
from .pydidas_combobox import *
from .pydidas_label import *
from .pydidas_lineedit import *
from .pydidas_pushbutton import *
from .radio_button_group import *
from .square_button import *


__all__ = (
    create_widgets_mixin.__all__
    + empty_widget.__all__
    + pydidas_checkbox.__all__
    + pydidas_combobox.__all__
    + pydidas_label.__all__
    + pydidas_lineedit.__all__
    + pydidas_pushbutton.__all__
    + square_button.__all__
    + radio_button_group.__all__
)

del (
    create_widgets_mixin,
    empty_widget,
    pydidas_checkbox,
    pydidas_combobox,
    pydidas_label,
    pydidas_lineedit,
    pydidas_pushbutton,
    square_button,
    radio_button_group,
)
