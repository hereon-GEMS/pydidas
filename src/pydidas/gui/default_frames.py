# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
Module with the DEFAULT_FRAMES which lists all of pydidas's generic frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_default_frames"]


import importlib

from pydidas.widgets.base_classes import BaseFrame


FRAME_MODULE_PATHS: dict[str, str] = {
    "HomeFrame": "pydidas.gui.frames.home_frame",
    "DataBrowsingFrame": "pydidas.gui.frames.data_browsing_frame",
    "PyfaiCalibFrame": "pydidas.gui.frames.pyfai_calib_frame",
    "ImageMathFrame": "pydidas.gui.frames.image_math_frame",
    "QuickIntegrationFrame": "pydidas.gui.frames.quick_integration_frame",
    "SinSquareChiResultsFrame": "pydidas.gui.frames.sin_square_chi_results_frame",
    "DefineDiffractionExpFrame": "pydidas.gui.frames.define_diffraction_exp_frame",
    "DefineScanFrame": "pydidas.gui.frames.define_scan_frame",
    "WorkflowEditFrame": "pydidas.gui.frames.workflow_edit_frame",
    "WorkflowTestFrame": "pydidas.gui.frames.workflow_test_frame",
    "WorkflowRunFrame": "pydidas.gui.frames.workflow_run_frame",
    "ViewResultsFrame": "pydidas.gui.frames.view_results_frame",
    "UtilitiesFrame": "pydidas.gui.frames.utilities_frame",
}

DEFAULT_FRAMES: list[str] = [
    "HomeFrame",
    "DataBrowsingFrame",
    "PyfaiCalibFrame",
    "ImageMathFrame",
    "QuickIntegrationFrame",
    "SinSquareChiResultsFrame",
    "DefineDiffractionExpFrame",
    "DefineScanFrame",
    "WorkflowEditFrame",
    "WorkflowTestFrame",
    "WorkflowRunFrame",
    "ViewResultsFrame",
    "UtilitiesFrame",
]


def _load_frame_class(class_name: str) -> type[BaseFrame]:
    """
    Load a frame class from the default frames.

    This function dynamically imports the module containing the specified
    frame class and returns the class itself. It is useful for loading
    frames based on their names without having to import all frame classes
    at once.

    Parameters
    ----------
    class_name : str
        The name of the frame class to load.

    Returns
    -------
    type[BaseFrame]
        The frame class corresponding to the given class name.
    """
    _path = FRAME_MODULE_PATHS[class_name]
    try:
        _module = importlib.import_module(_path)
    except ImportError as e:
        raise ImportError(f"Could not import module {_path}") from e
    _cls = getattr(_module, class_name)
    if not issubclass(_cls, BaseFrame):
        raise TypeError(f"{_path}.{class_name} is not a BaseFrame subclass")
    return _cls


def get_default_frames() -> tuple[type[BaseFrame], ...]:
    """
    Return a tuple of the default frame classes.

    Returns
    -------
    tuple[type[BaseFrame], ...]
        A tuple of the default frame classes.
    """
    return tuple(_load_frame_class(name) for name in DEFAULT_FRAMES)
