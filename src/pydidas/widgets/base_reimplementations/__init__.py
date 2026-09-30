# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
The base_reimplementations subpackage includes basic QtWidget
re-implementations with extended generic functionality that
 are used throughout the pydidas package.

These widgets are designed to provide scaling based on the system
font and font size to allow a scalability independent of the
monitor resolution.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .font_scaling_toolbar import FontScalingToolbar
from .pydidas_checkbox import PydidasCheckBox
from .pydidas_combobox import PydidasComboBox
from .pydidas_frame_stack import PydidasFrameStack
from .pydidas_label import PydidasLabel
from .pydidas_lineedit import PydidasLineEdit
from .pydidas_list_widget import PydidasListWidget
from .pydidas_pushbutton import PydidasPushButton
from .pydidas_status_widget import PydidasStatusWidget
from .pydidas_svgwidget import PydidasSvgWidget
from .pydidas_table import PydidasTable
from .radio_button_group import RadioButtonGroup
from .read_only_text_edit import ReadOnlyTextEdit
from .square_button import SquareButton


__all__ = [
    "FontScalingToolbar",
    "PydidasCheckBox",
    "PydidasComboBox",
    "PydidasFrameStack",
    "PydidasLabel",
    "PydidasLineEdit",
    "PydidasListWidget",
    "PydidasPushButton",
    "PydidasStatusWidget",
    "PydidasSvgWidget",
    "PydidasTable",
    "RadioButtonGroup",
    "ReadOnlyTextEdit",
    "SquareButton",
]
