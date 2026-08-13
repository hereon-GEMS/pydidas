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
from typing import Any


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

    def __repr__(self) -> str:
        return f"<lazy proxy for {self._module_path}.{self._attr_name}>"


class LazySet(set):
    """
    A set subclass that populates itself with entries on the first access.

    This defers the import of the initialization function (and therefore
    any heavy imports) until the set is actually queried, rather than at
    module import time.
    """

    def __init__(self, init_function: callable) -> None:
        super().__init__()
        self._initialized = False
        self._init_function = init_function

    def _ensure_initialized(self) -> None:
        """Call the initialization function to populate the set."""
        if not self._initialized:
            _members = self._init_function()
            self.update(_members)
            self._initialized = True

    def __contains__(self, item: object) -> bool:
        self._ensure_initialized()
        return super().__contains__(item)

    def __iter__(self):
        self._ensure_initialized()
        return super().__iter__()

    def __len__(self) -> int:
        self._ensure_initialized()
        return super().__len__()

    def __bool__(self) -> bool:
        self._ensure_initialized()
        return len(self) > 0


class LazyDict(dict):
    """
    A dict subclass that populates itself with entries on the first access.

    This defers the import of the initialization function (and therefore
    any heavy imports) until the dict is actually queried, rather than at
    module import time.
    """

    def __init__(self, init_function: callable) -> None:
        super().__init__()
        self._initialized = False
        self._init_function = init_function

    def _ensure_initialized(self) -> None:
        """Call the initialization function to populate the dict."""
        if not self._initialized:
            _members = self._init_function()
            self.update(_members)
            self._initialized = True

    def __getitem__(self, key: object) -> Any:
        self._ensure_initialized()
        return super().__getitem__(key)

    def __setitem__(self, key: object, value: Any) -> None:
        self._ensure_initialized()
        super().__setitem__(key, value)

    def __contains__(self, key: object) -> bool:
        self._ensure_initialized()
        return super().__contains__(key)

    def __iter__(self):
        self._ensure_initialized()
        return super().__iter__()

    def __len__(self) -> int:
        self._ensure_initialized()
        return super().__len__()

    def __bool__(self) -> bool:
        self._ensure_initialized()
        return len(self) > 0
