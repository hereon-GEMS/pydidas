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

from pydidas.core.generic_params.generic_params_scan import GENERIC_PARAMS_SCAN
from pydidas.core.utils import format_input_to_multiline_str


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

__SCAN_PARAMS_HEADER = """..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

List of all ScanContext Parameters
----------------------------------
"""

__SCAN_DIM_PARAMS = """

The following Parameters exist for each scan dimension, i.e. scan_dim{i}_label 
stands for scan_dim0_label, scan_dim1_label, scan_dim2_label, 
scan_dim3_label. For clarity, only the generic form is described here.

- scan_dim{i}_label (type: str, default: "")
    The axis name for scan direction *{i}*. This information will only be used
    for labelling.
- scan_dim{i}_n_points (type: int, default: 0)
    The number of scan points in scan direction *{i}*.
- scan_dim{i}_delta (type: float, default: 1)
    The step width between two scan points in scan direction *{i}*.
- scan_dim{i}_offset (type: float, default: 0)
    The coordinate offset of the movement in scan direction *{i}* (i.e. the
    counter / motor position for scan step #0).
- scan_dim{i}_unit (type: str, default: "")
    The unit of the movement / steps / offset in scan direction *{i}*.
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


def create_scan_context_params_rst_docs(filename: Path):
    """
    Creates a reStructuredText documentation file for the scan context parameters.

    This function generates a reStructuredText file that documents the scan context
    parameters of the codebase. It writes the documentation to the file located at
    `./dev_guide/generic_params_scan.rst`.

    Parameters
    ----------
    filename : Path
        The path of the file to which the documentation will be written.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(__SCAN_PARAMS_HEADER)
        for _key, _description in GENERIC_PARAMS_SCAN.items():
            if _key.startswith("scan_dim") or _key.startswith("scan_index"):
                continue
            _type = _description["type"]
            f.write(
                f"\n- {_key} (type: "
                f"{_type if isinstance(_type, str) else _type.__name__}"
                f", default: {_description['default']}, "
                f"unit: {_description.get('unit', '')})\n"
            )
            f.write(
                format_input_to_multiline_str(
                    _description["tooltip"], max_line_length=84, indent=4
                )
            )
        f.write(__SCAN_DIM_PARAMS)
