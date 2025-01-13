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
Subpackage with PyQt dialogues.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .acknowledge_box import *
from .critical_warning_ import *
from .error_message_box import *
from .hdf5_dataset_selection_popup import *
from .item_in_list_selection_widget import *
from .pydidas_exception_message_box import *
from .question_box import *
from .warning_box import *


__all__ = (
    acknowledge_box.__all__
    + critical_warning_.__all__
    + error_message_box.__all__
    + hdf5_dataset_selection_popup.__all__
    + item_in_list_selection_widget.__all__
    + pydidas_exception_message_box.__all__
    + question_box.__all__
    + warning_box.__all__
)

del (
    acknowledge_box,
    critical_warning_,
    error_message_box,
    hdf5_dataset_selection_popup,
    item_in_list_selection_widget,
    pydidas_exception_message_box,
    question_box,
    warning_box,
)
