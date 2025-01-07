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
#
# ruff : noqa: I001
"""
The pydidas.plugins subpackage includes the base classes for plugins as well as the
PluginCollection singleton which holds all registered plugins and allows to
get new instances of these plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .base_input_plugin import *
from .base_input_plugin_1d import *
from .base_output_plugin import *
from .base_plugin import *
from .base_proc_plugin import *
from .plugin_collection import *
from .plugin_getter_ import *

# The base plugins with references to widgets must be imported last:
from .base_fit_plugin import *
from .pyfai_integration_base import *  # noqa: I001


__all__ = (
    base_fit_plugin.__all__
    + base_input_plugin.__all__
    + base_input_plugin_1d.__all__
    + base_output_plugin.__all__
    + base_plugin.__all__
    + base_proc_plugin.__all__
    + plugin_collection.__all__
    + plugin_getter_.__all__
    + pyfai_integration_base.__all__
)

del (
    base_plugin,
    base_input_plugin,
    base_input_plugin_1d,
    base_output_plugin,
    base_proc_plugin,
    plugin_collection,
    plugin_getter_,
    pyfai_integration_base,
)
