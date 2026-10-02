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


import warnings
from collections.abc import Iterable
from typing import Any, ClassVar, Self

import yaml


class ConfigDict(dict):
    """
    A dict which only allows str keys and supports attribute access to items.

    Keys which clash with attributes of dict (e.g. "items" or "keys") can only
    be accessed through item access (``cfg["items"]``).

    The mapping can be pickled and exported with json.dumps and yaml.safe_dump
    (the latter through a representer registered for the yaml.SafeDumper). Loading
    JSON or YAML data gives plain dicts which can be converted with
    ``ConfigDict(data)``.

    Parameters
    ----------
    *args : Any
        Positional arguments as accepted by dict.
    **kwargs : Any
        Keyword arguments as accepted by dict.
    """

    restricted_value_types: ClassVar[None | tuple[type, ...]] = None
    restricted_key_types: ClassVar[tuple[type, ...]] = (str,)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the mapping from positional and keyword arguments."""
        super().__init__()
        self.update(*args, **kwargs)

    def _check_key(self, key: Any) -> None:
        """
        Raise a TypeError if a mapping key is not of an allowed type.

        Parameters
        ----------
        key : Any
            The key to check.
        """
        if not isinstance(key, self.restricted_key_types):
            _name = type(self).__name__
            raise TypeError(
                f"{_name} keys must be of type {self.restricted_key_types}, "
                f"not {type(key).__name__}."
            )

    def _check_value(self, value: Any) -> None:
        """
        Raise a TypeError if a mapping value is not of an allowed type.

        Parameters
        ----------
        value : Any
            The value to check.
        """
        if not self.restricted_value_types:
            return
        if not isinstance(value, self.restricted_value_types):
            _name = type(self).__name__
            raise TypeError(
                f"{_name} values must be of type {self.restricted_value_types}, "
                f"not {type(value).__name__}."
            )

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value after checking that key and value are valid."""
        self._check_key(key)
        self._check_value(value)
        super().__setitem__(key, value)

    def __getattr__(self, name: str) -> Any:
        """Return the value associated with an attribute-style key lookup."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from None

    def __setattr__(self, name: str, value: Any) -> None:
        """Set a non-reserved attribute as a mapping item."""
        if hasattr(type(self), name):
            raise AttributeError(
                f"Cannot set attribute '{name}' because it is a reserved name of "
                f"'{type(self).__name__}'. Use item access instead."
            )
        self[name] = value

    def __delattr__(self, name: str) -> None:
        """Delete a non-reserved attribute by removing its mapping item."""
        if hasattr(type(self), name):
            raise AttributeError(
                f"Cannot delete attribute '{name}' because it is a reserved name "
                f"of '{type(self).__name__}'. Use item access instead."
            )
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __or__(self, other: Any) -> Self:
        """Return a new mapping containing this mapping and ``other``."""
        if not isinstance(other, dict):
            return NotImplemented
        new = self.copy()
        new.update(other)
        return new

    def __ror__(self, other: Any) -> Self:
        """Return a new mapping containing ``other`` and this mapping."""
        if not isinstance(other, dict):
            return NotImplemented
        new = type(self)(other)
        new.update(self)
        return new

    def __ior__(self, other: Any) -> Self:
        """Update this mapping in place with ``other``."""
        self.update(other)
        return self

    def __reduce__(self) -> tuple[type[Self], tuple[dict[str, Any]]]:
        """Return the pickle reconstruction callable and its arguments."""
        return type(self), (dict(self),)

    def __dir__(self) -> list[str]:
        """Return normal attributes together with the mapping's string keys."""
        return sorted(set(super().__dir__()) | set(self))

    def __repr__(self) -> str:
        """Return a string representation of the mapping."""
        _dict_repr = dict.__repr__(self).strip("{}")
        return f"{type(self).__name__}({_dict_repr})"

    def __copy__(self) -> Self:
        """Return a shallow copy of the mapping."""
        return type(self)(self)

    def __hash__(self) -> int:
        """Return a hash of the mapping."""
        return ConfigDict.__hash_dict(self)

    @staticmethod
    def __hash_dict(item: dict) -> int:
        """
        Get a hash value for a dictionary.

        Parameters
        ----------
        item : dict
            The dictionary to hash.
        """
        if item == {}:
            return 0
        _key_value_hashes = []
        for _key, _val in item.items():
            try:
                _key_value_hashes.append((_key, ConfigDict.__hash_value(_val)))
            except TypeError:
                warnings.warn(f'Could not hash the dictionary value "{_val}".')
        return hash(frozenset(_key_value_hashes))

    @staticmethod
    def __hash_value(value: Any) -> int:
        """Hash nested dictionaries and sequences recursively."""
        if isinstance(value, dict):
            return ConfigDict.__hash_dict(value)
        if isinstance(value, (list, tuple)):
            return hash(tuple(ConfigDict.__hash_value(item) for item in value))
        return hash(value)

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update the mapping after checking that all keys are strings."""
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def setdefault(self, key: str, default: Any = None) -> Any:
        """Return a key's value, inserting ``default`` if the key is missing."""
        if key not in self:
            self[key] = default
        return self[key]

    def copy(self) -> Self:
        """Return a shallow copy of this mapping."""
        return type(self)(self)

    @classmethod
    def fromkeys(cls, iterable: Iterable[str], value: Any = None) -> Self:
        """Create a new mapping from an iterable of string keys."""
        return cls(dict.fromkeys(iterable, value))


def _represent_config_dict(dumper: yaml.SafeDumper, data: ConfigDict) -> yaml.Node:
    """Represent a ConfigDict (or subclass) as a plain YAML mapping."""
    return dumper.represent_dict(dict(data))


yaml.SafeDumper.add_multi_representer(ConfigDict, _represent_config_dict)
