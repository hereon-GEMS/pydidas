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
Package with individual Parameter configuration widgets used for generic plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .edit_plugin_parameters_widget import *
from .fit_plugin_config_widget import *
from .generic_plugin_config_widget import *
from .pyfai_integration_config_widget import *


__all__ = (
    edit_plugin_parameters_widget.__all__
    + generic_plugin_config_widget.__all__
    + fit_plugin_config_widget.__all__
    + pyfai_integration_config_widget.__all__
)

del (
    edit_plugin_parameters_widget,
    generic_plugin_config_widget,
    fit_plugin_config_widget,
    pyfai_integration_config_widget,
)
