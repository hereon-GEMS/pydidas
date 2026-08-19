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
#
# Parts of this file are adapted from the pyFAI.gui.CalibrationWindow
# widget which is distributed under the MIT license.

"""
Module with the PyfaiCalibFrame which is roughly based on the pyfai-calib2 window
to be used within pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_calib_tasks", "populate_menu"]


from functools import partial

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QListWidget, QToolBar

from pydidas.core.lazy_imports.pyFAI import (
    AbstractCalibrationTask,
    CalibWindowMenuItem,
    ExperimentTask,
    GeometryTask,
    IntegrationTask,
    MaskTask,
    PeakPickingTask,
)
from pydidas.core.lazy_imports.silx import ImageToolBar
from pydidas.widgets import PydidasFileDialog, icon_with_inverted_colors
from pydidas.widgets.silx_plot import actions
from pydidas.widgets.silx_plot.silx_actions import PydidasLoadImageAction


# ------------------------------------
# public functions:
# ------------------------------------


def create_calib_tasks() -> list[AbstractCalibrationTask]:
    """
    Create the tasks for the calibration.

    This function will also overload the generic tasks and add a CropHistogramOutlier
    action to the toolbars and change the default file dialog to use the pydidas
    file dialog.

    Returns
    -------
    tasks : list[AbstractCalibrationTask]
        The list with the task instances.
    """
    import pyFAI.gui.ApplicationContext as ApplicationContext_module

    # Patch the relevant pyFAI modules to use the pydidas dialogs:
    ApplicationContext_module.qt.QFileDialog = PydidasFileDialog

    _exp_task: ExperimentTask = ExperimentTask()
    _replace_exp_task_button_actions(_exp_task)

    _mask_task: MaskTask = MaskTask()

    _peak_task: PeakPickingTask = PeakPickingTask()
    _disable_new_ring_option(_peak_task)
    _peak_task.widgetShow.connect(
        partial(_update_peak_picking_task_menu_width, _peak_task)
    )

    _geo_task: GeometryTask = GeometryTask()

    _update_toolbar_entries(_exp_task, _mask_task, _peak_task, _geo_task)

    _integration_task: IntegrationTask = IntegrationTask()
    _add_update_pydidas_diff_exp_button(_integration_task)
    _integration_task.setNextStepVisible(False)

    return [_exp_task, _mask_task, _peak_task, _geo_task, _integration_task]


def populate_menu(
    list_widget: QListWidget, tasks: list[AbstractCalibrationTask]
) -> None:
    for _task in tasks:
        _inverted_icon = icon_with_inverted_colors(_task.windowIcon())
        _menu_item = CalibWindowMenuItem(list_widget)
        _menu_item.setText(_task.windowTitle())
        _menu_item.setIcon(_inverted_icon)
        _task.warningUpdated.connect(partial(_update_task_state, _task, _menu_item))


# ------------------------------------
# private helper functions and slots:
# ------------------------------------


@QtCore.Slot()
def _update_peak_picking_task_menu_width(task: PeakPickingTask) -> None:
    """
    Update the width of the PeakPickingTask to show all items.

    Parameters
    ----------
    task : PeakPickingTask
    """
    _splitter: QtWidgets.QSplitter = task.splitter  # type: ignore[attr-defined]
    _sizes = _splitter.sizes()
    _splitter.setSizes([_sizes[0], int(1.2 * _sizes[1])])
    # disconnect slot to make sure the modification is only applied once:
    task.widgetShow.disconnect(_update_peak_picking_task_menu_width)


def _replace_exp_task_button_actions(exp_task: ExperimentTask) -> None:
    """
    Replace the LoadImageToolButton actions with pydidas actions.

    This function modifies the ExperimentTask in place.

    Note: This modification must be done after initialization to prevent
    breaking the uic.loadUi references.

    Parameters
    ----------
    exp_task : ExperimentTask
        The instance to be modified.
    """
    for _item in ["_imageLoader", "_maskLoader", "_darkLoader", "_flatLoader"]:
        _btn = getattr(exp_task, _item)
        while _btn.actions():
            _btn.removeAction(_btn.actions()[0])
        _action = PydidasLoadImageAction(_btn)
        _btn.addAction(_action)
        _btn.setDefaultAction(_action)


def _disable_new_ring_option(task: PeakPickingTask) -> None:
    """
    Disable the pre-selected new ring option.

    Parameters
    ----------
    task : PeakPickingTask
        The peak picking task
    """
    task._PeakPickingTask__createNewRingOption.setChecked(False)  # type: ignore[attr]


def _add_update_pydidas_diff_exp_button(task: IntegrationTask) -> None:
    """
    Add a button to update the pydidas diffraction experiment context.

    Parameters
    ----------
    task : IntegrationTask
        The task to be updated.
    """
    _save_poni_button = task._savePoniButton  # type: ignore[attr-defined]
    _save_poni_button_parent_layout = _save_poni_button.parent().layout()
    task._update_context_button = QtWidgets.QPushButton(  # type: ignore[attr-defined]
        "Update pydidas diffraction setup from calibration"
    )
    _save_poni_button_parent_layout.addWidget(task._update_context_button)
    task._savePoniButton.clicked.disconnect()  # type: ignore[attr-defined]


def _update_toolbar_entries(
    *tasks: ExperimentTask | MaskTask | PeakPickingTask | GeometryTask,
) -> None:
    """
    Add toolbar entries to adjust the histogram to the given tasks.

    Parameters
    ----------
    tasks : ExperimentTask or MaskTask or PeakPickingTask or GeometryTask
        The tasks to be updated.
    """
    for _task in tasks:
        _plot = getattr(_task, f"_{_task.__class__.__name__}__plot")
        _toolbar = _plot.findChildren(ImageToolBar.resolve())[0]  # type: ignore[attr-defined]
        _histo_crop_action = actions.CropHistogramOutliersAction(
            _plot, parent=_plot, forced_image_legend="image"
        )
        _autoscale_min_max_action = actions.AutoscaleToMinMaxAction(
            _plot, parent=_plot, forced_image_legend="image"
        )
        _autoscale_mean_3sigma_action = actions.AutoscaleToMeanAndThreeSigmaAction(
            _plot, parent=_plot, forced_image_legend="image"
        )
        _widget_action = next(
            _action
            for _action in _toolbar.actions()
            if isinstance(_action, QtWidgets.QWidgetAction)
        )
        _toolbar.addAction(_histo_crop_action)
        _toolbar.addAction(_autoscale_min_max_action)
        _toolbar.addAction(_autoscale_mean_3sigma_action)
        _toolbar.insertAction(_widget_action, _histo_crop_action)
        _toolbar.insertAction(_widget_action, _autoscale_min_max_action)
        _toolbar.insertAction(_widget_action, _autoscale_mean_3sigma_action)
        # explicitly hide the "3D visualization" action:
        for tb in _plot.findChildren(QToolBar):
            for _action in tb.actions():
                if _action.text() == "3D visualization":
                    _action.setVisible(False)


@QtCore.Slot()
def _update_task_state(
    task: AbstractCalibrationTask, item: "CalibWindowMenuItem"
) -> None:
    """
    Update the task state.

    This method re-implements the generic CalibrationWindow method which
    would be missing in the pydidas implementation.
    """
    item.setWarnings(task.nextStepWarning())
