# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The pydidas_basic_widgets module definitions of subclassed QWidgets with additional
convenience functionality.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasLabel", "PydidasCheckBox", "PydidasComboBox", "PydidasLineEdit"]


from qtpy import QtWidgets

from .pydidas_widget_mixin import PydidasWidgetMixin


class PydidasLabel(PydidasWidgetMixin, QtWidgets.QLabel):
    """
    Create a QLabel with automatic font formatting.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        QtWidgets.QLabel.__init__(self, *args)
        kwargs["wordWrap"] = kwargs.get("wordWrap", True)
        PydidasWidgetMixin.__init__(self, **kwargs)


class PydidasCheckBox(PydidasWidgetMixin, QtWidgets.QCheckBox):
    """
    Create a QCheckBox with automatic font formatting.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        QtWidgets.QCheckBox.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)


class PydidasComboBox(PydidasWidgetMixin, QtWidgets.QComboBox):
    """
    Create a QSpinBox with automatic font formatting.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        QtWidgets.QComboBox.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)


class PydidasLineEdit(PydidasWidgetMixin, QtWidgets.QLineEdit):
    """
    Create a QLineEdit with automatic font formatting.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        QtWidgets.QLineEdit.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)
