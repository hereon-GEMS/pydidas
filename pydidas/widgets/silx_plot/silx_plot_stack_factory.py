# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with a function to create a QStackedWidget with 1d and 2d plots and add it to
a Pydidas Frame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_silx_plot_stack"]


from functools import partial

from qtpy import QtWidgets

from ...core.constants import POLICY_EXP_EXP
from .pydidas_plot1d import PydidasPlot1D
from .pydidas_plot2d import PydidasPlot2D


def create_silx_plot_stack(
    frame, gridPos=None, use_data_info_action=False, diffraction_exp=None
):
    """
    Create a QStackedWidget with 1D and 2D plot widgets in the input frame.


    Parameters
    ----------
    frame : pydidas.widgets.framework.BaseFrame
        The input frame.
    gridPos : Union[tuple, None], optional
        The gridPos for the new widget. The default is None.
    use_data_info_action : bool, optional
        Flag to use the PydidasGetDataInfoAction to display information about a
        result datapoint. The default is False.
    diffraction_exp : DiffractionExperiment
        The DiffractionExperiment instance to be used in the PydidasPlot2D for
        the coordinate system.

    Returns
    -------
    frame : pydidas.widgets.framework.BaseFrame
        The updated frame.
    """
    frame._widgets["plot1d"] = PydidasPlot1D()
    frame._widgets["plot2d"] = PydidasPlot2D(
        use_data_info_action=use_data_info_action, diffraction_exp=diffraction_exp
    )
    if hasattr(frame, "sig_this_frame_activated"):
        frame.sig_this_frame_activated.connect(
            partial(frame._widgets["plot2d"].cs_transform.check_detector_is_set, True)
        )
    frame.add_any_widget(
        "plot_stack",
        QtWidgets.QStackedWidget(),
        alignment=None,
        gridPos=gridPos,
        visible=True,
        stretch=(1, 1),
        sizePolicy=POLICY_EXP_EXP,
    )
    frame._widgets["plot_stack"].addWidget(frame._widgets["plot1d"])
    frame._widgets["plot_stack"].addWidget(frame._widgets["plot2d"])
