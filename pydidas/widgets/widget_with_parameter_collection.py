# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the SelectPointsForBeamcenterWindow class which allows to select points
in an image to define the beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WidgetWithParameterCollection"]


from qtpy import QtWidgets

from ..core import ParameterCollection, ParameterCollectionMixIn, PydidasQsettingsMixin
from ..core.utils import apply_qt_properties
from .factory import CreateWidgetsMixIn
from .parameter_config import ParameterWidgetsMixIn


class WidgetWithParameterCollection(
    QtWidgets.QWidget,
    PydidasQsettingsMixin,
    CreateWidgetsMixIn,
    ParameterCollectionMixIn,
    ParameterWidgetsMixIn,
):
    """
    A widget which has full access to Pydidas's ParameterCollection and widget creation
    methods.
    """

    def __init__(self, parent=None, **kwargs):
        self.params = ParameterCollection()
        self._config = {}
        QtWidgets.QWidget.__init__(self, parent)
        PydidasQsettingsMixin.__init__(self)
        ParameterCollectionMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        CreateWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        apply_qt_properties(self.layout(), contentsMargins=(0, 0, 0, 0))
        apply_qt_properties(self, **kwargs)
