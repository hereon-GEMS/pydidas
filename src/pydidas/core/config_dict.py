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
Module with the ConfigDict class, a dict subclass which only allows str keys
and allows access to its items as attributes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ConfigDict"]


from typing import Any


class ConfigDict(dict):
    """
    A dict which only allows str keys and supports attribute access to items.

    Keys which clash with attributes of dict (e.g. "items" or "keys") can only
    be accessed through item access (``cfg["items"]``).

    Parameters
    ----------
    *args : Any
        Positional arguments as accepted by dict.
    **kwargs : Any
        Keyword arguments as accepted by dict.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__()
        self.update(*args, **kwargs)

    @staticmethod
    def _check_key(key: Any) -> str:
        if not isinstance(key, str):
            raise TypeError(
                f"ConfigDict keys must be of type str, not {type(key).__name__}."
            )
        return key

    def __setitem__(self, key: str, value: Any):
        super().__setitem__(self._check_key(key), value)

    def __getattr__(self, name: str) -> Any:
        # Only called if normal attribute lookup fails.
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from None

    def __setattr__(self, name: str, value: Any):
        if hasattr(type(self), name):
            raise AttributeError(
                f"Cannot set attribute '{name}' because it is a reserved name of "
                f"'{type(self).__name__}'. Use item access instead."
            )
        self[name] = value

    def __delattr__(self, name: str):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __or__(self, other: Any) -> "ConfigDict":
        if not isinstance(other, dict):
            return NotImplemented
        new = self.copy()
        new.update(other)
        return new

    def __ror__(self, other: Any) -> "ConfigDict":
        if not isinstance(other, dict):
            return NotImplemented
        new = type(self)(other)
        new.update(self)
        return new

    def __ior__(self, other: Any) -> "ConfigDict":
        self.update(other)
        return self

    def __reduce__(self):
        return (type(self), (dict(self),))

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(self))

    def update(self, *args: Any, **kwargs: Any):
        """Update the ConfigDict, checking that all keys are str."""
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def setdefault(self, key: str, default: Any = None) -> Any:
        """Get the value for key, inserting default if key is missing."""
        if key not in self:
            self[key] = default
        return self[key]

    def copy(self) -> "ConfigDict":
        """Get a shallow copy of the ConfigDict."""
        return type(self)(self)

    @classmethod
    def fromkeys(cls, iterable, value=None) -> "ConfigDict":
        """Create a new ConfigDict from an iterable of keys."""
        return cls(dict.fromkeys(iterable, value))
