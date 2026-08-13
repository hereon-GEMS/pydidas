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
The lazy_objects module provides a mechanism to lazily import classes and callables
from 3rd party packages (e.g. pyFAI) to avoid unnecessary imports and reduce
startup time.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import importlib
from functools import partial, partialmethod
from typing import Any


# Named (non-dunder) public methods that are bound lazily at instance level
# in __init__ and replaced with native C-level bound methods after first init.
_NAMED_SET_METHODS: tuple[str, ...] = (
    "add",
    "clear",
    "copy",
    "difference",
    "difference_update",
    "discard",
    "intersection",
    "intersection_update",
    "isdisjoint",
    "issubset",
    "issuperset",
    "pop",
    "remove",
    "symmetric_difference",
    "symmetric_difference_update",
    "union",
    "update",
)

_NAMED_DICT_METHODS: tuple[str, ...] = (
    "copy",
    "get",
    "items",
    "keys",
    "pop",
    "popitem",
    "setdefault",
    "update",
    "values",
)

# Dunder methods that exist in the native type's __dict__ and are wired up
# via partialmethod after each class definition.  __bool__ is excluded because
# neither set nor dict define it (both derive truthiness from __len__).
_DUNDER_SET_METHODS: tuple[str, ...] = (
    "__contains__",
    "__iter__",
    "__len__",
    "__eq__",
    "__ne__",
    "__le__",
    "__lt__",
    "__ge__",
    "__gt__",
    "__or__",
    "__and__",
    "__sub__",
    "__xor__",
    "__ior__",
    "__iand__",
    "__isub__",
    "__ixor__",
)

_DUNDER_DICT_METHODS: tuple[str, ...] = (
    "__getitem__",
    "__setitem__",
    "__contains__",
    "__iter__",
    "__len__",
    "__eq__",
    "__ne__",
    "__or__",
    "__ior__",
)


class LazyObject:
    """
    A proxy that defers importing a class or callable until first use.

    An instance of this class holds only the dotted module path and the
    attribute name within that module.  The real object is resolved (and then
    cached) the first time any of the following happens:

    * The proxy is **called** (instantiation or function call).
    * An **attribute** is accessed on the proxy.
    * The proxy is used in an **isinstance** or **issubclass** check.

    Parameters
    ----------
    module_path : str
        Dotted import path of the module, e.g. ``"pyFAI.detectors"``.
    attr_name : str
        Name of the class or callable inside that module,
        e.g. ``"Detector"``.

    Examples
    --------
    >>> Detector = LazyObject("pyFAI.detectors", "Detector")
    >>> det = Detector()          # pyFAI is imported here for the first time
    >>> isinstance(det, Detector) # True — works like the real class
    """

    def __init__(self, module_path: str, attr_name: str) -> None:
        self._module_path = module_path
        self._attr_name = attr_name
        self._real_obj = None

    def _resolve(self) -> object:
        """Return the real object, importing it if necessary."""
        if self._real_obj is None:
            _module = importlib.import_module(self._module_path)
            self._real_obj = getattr(_module, self._attr_name)
        return self._real_obj

    def resolve(self) -> object:
        """
        Return the real underlying object, importing it if necessary.

        Use this when the proxy must be passed to code that requires an
        actual Python type (e.g. Qt's ``findChildren``).

        Returns
        -------
        object
            The resolved class or callable.
        """
        return self._resolve()

    def __call__(self, *args: object, **kwargs: object) -> object:
        _object = self._resolve()
        return _object(*args, **kwargs)

    def __getattr__(self, name: str) -> object:
        return getattr(self._resolve(), name)

    def __instancecheck__(self, instance: object) -> bool:
        return isinstance(instance, self._resolve())  # type: ignore[arg-type]

    def __subclasscheck__(self, subclass: type) -> bool:
        return issubclass(subclass, self._resolve())  # type: ignore[arg-type]

    def __mro_entries__(self, bases: tuple) -> tuple:
        """Support using a LazyObject as a base class."""
        return (self._resolve(),)

    def __or__(self, other: object) -> object:
        """Support the | operator for type union expressions."""
        _other = other._resolve() if isinstance(other, LazyObject) else other
        return self._resolve() | _other

    def __ror__(self, other: object) -> object:
        """Support the | operator when LazyObject is on the right-hand side."""
        _other = other._resolve() if isinstance(other, LazyObject) else other
        return _other | self._resolve()

    def __repr__(self) -> str:
        return f"<lazy proxy for {self._module_path}.{self._attr_name}>"


class LazySet(set):
    """
    A set subclass that populates itself with entries on the first access.

    This defers the import of the initialization function (and therefore
    any heavy imports) until the set is actually queried, rather than at
    module import time.

    Named public methods are bound as lazy wrappers at instance level during
    ``__init__`` and replaced with native ``set`` methods after the first
    access.  All dunder methods (except ``__bool__``) are wired up via
    ``partialmethod`` after the class definition so the class body stays
    compact.
    """

    def __init__(self, init_function: callable) -> None:
        super().__init__()
        self._initialized = False
        self._init_function = init_function
        for _name in _NAMED_SET_METHODS:
            object.__setattr__(self, _name, partial(self._lazy_call, _name))

    def _ensure_initialized(self) -> None:
        """Populate the set on first use and replace lazy wrappers with native methods."""
        if not self._initialized:
            super().update(self._init_function())
            self._initialized = True
            for _name in _NAMED_SET_METHODS:
                object.__setattr__(self, _name, set.__dict__[_name].__get__(self))

    def _lazy_call(self, method_name: str, /, *args: Any, **kwargs: Any) -> Any:
        """Ensure initialized, then delegate to the named ``set`` method."""
        self._ensure_initialized()
        return set.__dict__[method_name](self, *args, **kwargs)

    def __bool__(self) -> bool:
        self._ensure_initialized()
        return super().__len__() > 0


for _name in _DUNDER_SET_METHODS:
    setattr(LazySet, _name, partialmethod(LazySet._lazy_call, _name))


class LazyDict(dict):
    """
    A dict subclass that populates itself with entries on the first access.

    This defers the import of the initialization function (and therefore
    any heavy imports) until the dict is actually queried, rather than at
    module import time.

    Named public methods are bound as lazy wrappers at instance level during
    ``__init__`` and replaced with native ``dict`` methods after the first
    access.  All dunder methods (except ``__bool__``) are wired up via
    ``partialmethod`` after the class definition so the class body stays
    compact.
    """

    def __init__(self, init_function: callable) -> None:
        super().__init__()
        self._initialized = False
        self._init_function = init_function
        for _name in _NAMED_DICT_METHODS:
            object.__setattr__(self, _name, partial(self._lazy_call, _name))

    def _ensure_initialized(self) -> None:
        """Populate the dict on first use and replace lazy wrappers with native methods."""
        if not self._initialized:
            super().update(self._init_function())
            self._initialized = True
            for _name in _NAMED_DICT_METHODS:
                object.__setattr__(self, _name, dict.__dict__[_name].__get__(self))

    def _lazy_call(self, method_name: str, /, *args: Any, **kwargs: Any) -> Any:
        """Ensure initialized, then delegate to the named ``dict`` method."""
        self._ensure_initialized()
        return dict.__dict__[method_name](self, *args, **kwargs)

    def __bool__(self) -> bool:
        self._ensure_initialized()
        return super().__len__() > 0


for _name in _DUNDER_DICT_METHODS:
    setattr(LazyDict, _name, partialmethod(LazyDict._lazy_call, _name))
