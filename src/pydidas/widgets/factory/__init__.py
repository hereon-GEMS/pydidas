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


from .create_widgets_mixin import CreateWidgetsMixIn
from .empty_widget import EmptyWidget
from .pydidas_checkbox import PydidasCheckBox
from .pydidas_combobox import PydidasComboBox
from .pydidas_label import PydidasLabel
from .pydidas_lineedit import PydidasLineEdit
from .pydidas_pushbutton import PydidasPushButton
from .radio_button_group import RadioButtonGroup
from .square_button import SquareButton


__all__ = [
    "CreateWidgetsMixIn",
    "EmptyWidget",
    "PydidasCheckBox",
    "PydidasComboBox",
    "PydidasLabel",
    "PydidasLineEdit",
    "PydidasPushButton",
    "SquareButton",
    "RadioButtonGroup",
]
