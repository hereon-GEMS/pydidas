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
Module with the SelectPointsForBeamcenterWindow class which allows to select points
in an image to define the beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WidgetWithParameterCollection"]


from qtpy import QtWidgets

from pydidas.core import (
    ParameterCollection,
    ParameterCollectionMixIn,
    PydidasQsettingsMixin,
)
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn


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

    init_kwargs = ["parent"]

    def __init__(self, **kwargs: dict):
        self.params = ParameterCollection()
        self._config = {}
        QtWidgets.QWidget.__init__(self, kwargs.get("parent", None))
        PydidasQsettingsMixin.__init__(self)
        ParameterCollectionMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        CreateWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        apply_qt_properties(self.layout(), contentsMargins=(0, 0, 0, 0))
        apply_qt_properties(self, **kwargs)
