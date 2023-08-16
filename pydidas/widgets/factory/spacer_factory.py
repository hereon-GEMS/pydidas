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
Module with a factory function to create a QSpacerItem.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_spacer"]


from qtpy.QtWidgets import QSizePolicy, QSpacerItem

from ...core.utils import apply_qt_properties


def create_spacer(**kwargs):
    """
    Create a spacer item.

    A QSpacerItem will be created. Its size policy is "Minimal" unless
    overridden.

    Parameters
    ----------
    **kwargs : dict
        Any aditional keyword arguments. See below for supported arguments.
    **height : int, optional
        The height of the spacer in pixel. The default is 20.
    **width : int, optional
        The width of the spacer in pixel. The default is 20.
    **policy : QtWidgets.QSizePolicy, optional
        The size policy for the spacer (applied both horizontally and
        vertically). The default is QtWidgets.QSizePolicy.Minimum.
    **vertical_policy : QtWidgets.QSizePolicy, optional
        The vertical size policy for the spacer. This setting will overwrite
        the general "policy" settings. The default is
        QtWidgets.QSizePolicy.Minimum.
    **QtAttribute : depends on the attribute
        Any Qt attributes are supported by the QSpacerItem. Use the Qt
        attribute name with a lowercase first character. Examples are
        ``fixedWidth``, ``visible``.


    Returns
    -------
    spacer : QSpacerItem
        The new spacer.
    """
    _policy = kwargs.get("policy", QSizePolicy.Minimum)
    _vertical_policy = kwargs.get("vertical_policy", _policy)
    _spacer = QSpacerItem(
        kwargs.get("fixedWidth", 20),
        kwargs.get("fixedHeight", 20),
        _policy,
        _vertical_policy,
    )

    apply_qt_properties(_spacer, **kwargs)
    return _spacer
