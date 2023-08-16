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
Module with a factory function to create formatted QSpinBoxes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_spin_box"]


from qtpy.QtWidgets import QSpinBox

from ...core.utils import apply_qt_properties


def create_spin_box(**kwargs):
    """
    Create a QSpinBox widget and set properties.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments. See below for supported arguments.
    **valueRange: tuple, optional
        The range for the QSpinBox, given as a 2-tuple of (min, max). The
        default is (0, 1).
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the QSpinBox. Use the Qt
        attribute name with a lowercase first character. Examples are
        ``fixedWidth``, ``visible``.

    Returns
    -------
    box : QtWidgets.QSpinBox
        The instantiated spin box widget.
    """
    kwargs["range"] = kwargs.get("valueRange", (0, 1))
    # kwargs["fixedWidth"] = kwargs.get("fixedWidth", 50)
    _box = QSpinBox()
    apply_qt_properties(_box, **kwargs)
    return _box
