# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
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


def create_generic_params_rst_docu():
    """
    Creates a reStructuredText documentation file for the generic parameters.

    This function generates a reStructuredText file that documents the generic parameters
    of the codebase. It writes the documentation to the file located at `./dev_guide/generic_params.rst`.

    Parameters:
        None

    Returns:
        None
    """
    doc_path = "./dev_guide/generic_params.rst"

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(".. _generic_params:\n\n")
        f.write("Generic Parameters\n")
        f.write("==================\n\n")
        f.write("Params sorted by use case:\n\n")
        f.write(".. contents::\n")
        f.write("   :local:\n")
        for module_name, module_items in _metadata_by_module.items():
            _name = (
                module_name.removeprefix("generic_params_")
                .capitalize()
                .replace("_", " ")
            )
            f.write("\n" + _name + "\n")
            f.write("-" * len(_name) + "\n\n")
            f.write(
                ".. list-table::\n"
                "   :widths: 20 80\n"
                "   :header-rows: 1\n"
                "   :class: tight-table\n\n"
                "   * - Parameter\n"
                "     - Description\n"
            )
            for param_key, param in module_items.items():
                f.write(f"   * - :py:data:`{param_key}`\n")
                f.write("     - | ")
                if isinstance(param["type"], str):
                    pass
                elif param["type"] is None:
                    param["type"] = "None"
                else:
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
