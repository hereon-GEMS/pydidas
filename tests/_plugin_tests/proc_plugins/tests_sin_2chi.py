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
Tests for the DspacingSin_2chi class / plugin.
"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"

import pytest

import numpy as np
import numpy.testing as npt
from typing import Callable
from numbers import Real
from dataclasses import dataclass

from pydidas.plugins import PluginCollection
from pydidas.plugins import ProcPlugin
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED

from pydidas.core import Dataset, UserConfigError

from pydidas_plugins.proc_plugins.sin2chi_grouping import PARAMETER_KEEP_RESULTS, LABELS_SIN2CHI, LABELS_SIN_2CHI


