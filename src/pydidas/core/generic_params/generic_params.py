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
The generic_params module holds the dictionary with information required for creating
generic Parameters.
"""

__author__ = "Malte Storm, Nonni Heere"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_METADATA"]


import importlib
from pathlib import Path


_prefix = "pydidas.core.generic_params."

_metadata_by_module = dict()
for _module_name in [
    _object.stem
    for _object in Path(__file__).parent.iterdir()
    if _object.name.startswith("generic_params_")
]:
    _metadata_by_module[_module_name] = getattr(
        importlib.import_module(_prefix + _module_name, __package__),
        _module_name.upper(),
    )

GENERIC_PARAMS_METADATA = dict()
for key, value in _metadata_by_module.items():
    for key2, value2 in value.items():
        GENERIC_PARAMS_METADATA[key2] = value2


__DOC_FILE_HEADER = """
.. |parameters| replace:: :py:class:`Parameters <pydidas.core.Parameter>`
.. |param_collection| replace:: :py:class:`ParameterCollection <pydidas.core.ParameterCollection>`

.. _generic_params:

Generic Parameters
==================

This page gives a full list of all available generic |parameters| as a reference.

Introduction
------------

For accessing generic |parameters|, use 
:py:func:`~pydidas.core.get_generic_parameter` to access individual |parameters| 
and :py:func:`~pydidas.core.get_generic_param_collection` to create a new
|param_collection| from generic |parameters|.

Examples are given below:

.. code-block:: python

    >>> from pydidas.core import get_generic_parameter
    >>> from pydidas.core import get_generic_param_collection
    >>> filename_param = get_generic_parameter('filename')
    >>> filename_param
    Parameter <filename: . (type: Path, default: .)>
    >>> generic_params = get_generic_param_collection('filename', 'n_files')
    >>> generic_params
    {'filename': Parameter <filename: . (type: Path, default: .)>,
    'n_files': Parameter <n_files: 0 (type: Integral, default: 0)>}

List of generic Parameters
--------------------------

Generic |parameters| are sorted by their *use case*. The following sections are 
available: 

.. contents::
   :local:

"""


def create_generic_params_rst_docs(filename: Path):
    """
    Creates a reStructuredText documentation file for the generic parameters.

    This function generates a reStructuredText file that documents the generic
    parameters of the codebase. It writes the documentation to the file located at
    `./dev_guide/generic_params.rst`.

    Parameters
    ----------
    filename : Path
        The path of the file to which the documentation will be written.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(__DOC_FILE_HEADER)
        for module_name, module_items in _metadata_by_module.items():
            _name = (
                module_name.removeprefix("generic_params_")
                .capitalize()
                .replace("_", " ")
            )
            f.write(
                f"\n{_name}\n{'~' * len(_name)}\n\n"
                ".. list-table::\n"
                "   :widths: 20 80\n"
                "   :header-rows: 1\n"
                "   :class: tight-table\n\n"
                "   * - Parameter\n"
                "     - Description\n"
            )
            for param_key, param in module_items.items():
                f.write(f"   * - :py:data:`{param_key}`\n     - | ")
                if param["type"] is None:
                    param["type"] = "None"
                elif not isinstance(param["type"], str):
                    param["type"] = param["type"].__name__
                f.write(
                    ("\n       | ").join(
                        f"**{key}** : "
                        + str(val.__name__ if hasattr(val, __name__) else val).replace(
                            "\n", "\n       | "
                        )
                        for key, val in param.items()
                    )
                )
                f.write("\n")
