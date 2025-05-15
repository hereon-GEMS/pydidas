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
The get_documentation_targets module includes functions to get the directories or
URLs for the documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "configure_pyFAI",
    "check_documentation",
    "initialize_qsetting_values",
]


import logging
import os
import sys
from pathlib import Path

from qtpy import QtCore
from qtpy.QtCore import QStandardPaths

from pydidas.core import constants, get_generic_parameter
from pydidas.core.utils import sphinx_html
from pydidas.version import VERSION


def check_documentation():
    """
    Check whether the sphinx documentation has been built and build it if it has not
    """
    if not sphinx_html.check_sphinx_html_docs() and "--no-sphinx" not in sys.argv:
        sphinx_html.run_sphinx_html_build()


def configure_pyFAI():
    """
    Configure pyFAI to be used with pydidas.
    """
    for _key in [QStandardPaths.AppDataLocation, QStandardPaths.ConfigLocation]:
        _pyFAI_calib2_config = (
            Path(QStandardPaths.writableLocation(_key)).parents[1]
            / "pyfai"
            / "pyfai-calib2.ini"
        )
        if _pyFAI_calib2_config.is_file():
            _pyFAI_calib2_config.unlink()

    # Disable the pyFAI logging to console
    os.environ["PYFAI_NO_LOGGING"] = "1"
    # Change the pyFAI logging level to ERROR and above:
    pyFAI_azi_logger = logging.getLogger("pyFAI.azimuthalIntegrator")
    pyFAI_azi_logger.setLevel(logging.ERROR)
    pyFAI_logger = logging.getLogger("pyFAI")
    pyFAI_logger.setLevel(logging.ERROR)
    silx_opencl_logger = logging.getLogger("silx.opencl.processing")
    silx_opencl_logger.setLevel(logging.ERROR)


def initialize_qsetting_values():
    """
    Initialize the QSettings values for pydidas.
    """

    # if not existing, initialize all QSettings with the default values from the
    # default Parameters to avoid having "None" keys returned.
    __settings = QtCore.QSettings("Hereon", "pydidas")
    for _prefix, _keys in (
        ("global", constants.QSETTINGS_GLOBAL_KEYS),
        ("user", constants.QSETTINGS_USER_KEYS),
        ("user", constants.QSETTINGS_USER_SPECIAL_KEYS),
    ):
        for _key in _keys:
            _val = __settings.value(f"{VERSION}/{_prefix}/{_key}")
            if _val is None:
                _param = get_generic_parameter(_key)
                __settings.setValue(f"{VERSION}/{_prefix}/{_key}", _param.default)
    del __settings
