# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
Module with the ConfigDictMixin class, a mixin which provides a ConfigDict property.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ConfigDictMixin"]


from typing import Any

from pydidas.core.config_dict import ConfigDict


class ConfigDictMixin:
    """
    Expose an object's ConfigDict through a non-replaceable public property.

    This mixin class provides a ``config`` property that returns a mutable
    ConfigDict instance. The ConfigDict is initialized from a ``config`` keyword
    argument passed to the constructor. The property cannot be replaced, but its
    contents can be modified.

    Parameters
    ----------
    *args : Any
        Positional arguments passed to the superclass constructor.
    **kwargs : Any
        Keyword arguments passed to the superclass constructor. The ``config``
        keyword argument is consumed by this mixin and should be a dictionary.
        The ``super_init`` keyword is also passed through so downstream mixins
        can apply their own initialization rules.

        Used kwargs are:

        config : dict
            A dictionary to initialize the ConfigDict content. This kwargs
            is consumed by the mix-in.
        super_init : bool
            Flag to determine whether to call the superclass constructor.
            Defaults to True.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the mixin with a ConfigDict."""
        _config = kwargs.pop("config", {})
        if not isinstance(_config, dict):
            raise TypeError(
                f"Expected a dict for 'config', got {type(_config).__name__}."
            )
        self._config = ConfigDict(**_config)
        if kwargs.get("super_init", True):
            super().__init__(*args, **kwargs)

    @property
    def config(self) -> ConfigDict:
        """Return this object's mutable configuration mapping."""
        return self._config

    @config.setter
    def config(self, value: Any) -> None:
        """Reject replacement of the configuration mapping."""
        raise AttributeError("The config mapping cannot be replaced.")
