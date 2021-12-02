# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ParameterCollectionEditWidget class used to edit a collection
of Plugin Parameters.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParameterCollectionEditWidget']


from PyQt5 import QtWidgets, QtCore

from .parameter_widgets_mixin import ParameterWidgetsMixIn
from ..utilities import apply_widget_properties


class ParameterCollectionEditWidget(QtWidgets.QFrame,
                                    ParameterWidgetsMixIn):
    """
    The ParameterCollectionEditWidget widget can be used to create a composite
    widget for updating multiple Parameter values.
    """
    def __init__(self, parent=None, **kwargs):
        """
        Setup method.

        Create an instance on the ParameterConfigWidget class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.
        initLayout : bool, optional
            Flag to toggle layout creation (with a VBoxLayout). The default
            is True.
        **kwargs : dict
            Additional keyword arguments
        """
        QtWidgets.QFrame.__init__(self, parent)
        ParameterWidgetsMixIn.__init__(self)
        initLayout = kwargs.get('initLayout', True)
        kwargs['lineWidth'] = kwargs.get('lineWidth', 2)
        kwargs['frameStyle'] = kwargs.get('frameStyle',
                                          QtWidgets.QFrame.Raised)
        kwargs['autoFillBackground'] = kwargs.get('autoFillBackground', True)
        apply_widget_properties(self, **kwargs)
        if initLayout:
            _layout = QtWidgets.QGridLayout()
            _layout.setContentsMargins(5, 5, 0, 0)
            _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.setLayout(_layout)

    def next_row(self):
        """
        Get the next empty row in the layout.

        Returns
        -------
        int
            The next empty row.
        """
        return self.layout().rowCount() + 1
