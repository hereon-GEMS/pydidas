# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ResultSelectorForOutput widget which can handle the selection
of choices from the WorkflowResults and returns a signal with new data
selection.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ResultSelectorForOutput']

from functools import partial

import numpy as np
from PyQt5 import QtWidgets, QtCore

from pydidas.core import (ScanSettings, Parameter, ParameterCollection,
                          ParameterCollectionMixIn, get_generic_parameter)
from pydidas.constants import CONFIG_WIDGET_WIDTH
from pydidas.workflow_tree import WorkflowResults
from pydidas.widgets.create_widgets_mixin import CreateWidgetsMixIn
from pydidas.widgets.read_only_text_widget import ReadOnlyTextWidget
from pydidas.widgets.parameter_config.parameter_widgets_mixin import (
    ParameterWidgetsMixIn)

RESULTS = WorkflowResults()
SCAN = ScanSettings()


def _get_param_widget_config(param_key):
    """
    Get Formatting options for create_param_widget instances.
    """
    if param_key in ['selected_results']:
        return  dict(linebreak=True,
                     halign_text=QtCore.Qt.AlignLeft,
                     valign_text=QtCore.Qt.AlignBottom,
                     width_total=CONFIG_WIDGET_WIDTH,
                     width_io=CONFIG_WIDGET_WIDTH - 50,
                     width_text=CONFIG_WIDGET_WIDTH - 20,
                     width_unit=0)
    return dict(width_io=100, width_unit=0,
                width_text=CONFIG_WIDGET_WIDTH - 100,
                width_total=CONFIG_WIDGET_WIDTH,
                visible=False)


class ResultSelectorForOutput(QtWidgets.QWidget,
                              CreateWidgetsMixIn,
                              ParameterWidgetsMixIn,
                              ParameterCollectionMixIn):
    """
    Widgets for I/O during plugin parameter editing with predefined
    choices.
    """
    new_selection = QtCore.pyqtSignal(int, object)
    default_params = ParameterCollection(
        Parameter('n_dim', int, -1, name='Total result dimensionality'),
        Parameter('plot_ax1', int, 0, name='Data axis no. 1 for plot',
                  choices=[0]),
        Parameter('plot_ax2', int, 1, name='Data axis no. 2 for plot',
                  choices=[0, 1]),)

    def __init__(self, parent=None, select_results_param=None):
        """


        Parameters
        ----------
        parent : QtWidgets.QWidget
            The parent widget.
        select_results_param : pydidas.core.Parameter
            The select_results Parameter instance. This instance should be
            shared between the ResultSelectorForOutput and the parent.
        """
        QtWidgets.QWidget.__init__(self, parent)
        ParameterWidgetsMixIn.__init__(self)
        self.params = ParameterCollection()
        self._config = {}
        self._active_node = -1
        self._2d_plot = False
        self.add_param(select_results_param)
        self.set_default_params()
        self.__create_widgets()
        self.__connect_signals()

    def __create_widgets(self):
        _layout = QtWidgets.QGridLayout()
        _layout.setContentsMargins(5, 5, 0, 0)
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(_layout)

        self.create_label('label_results', 'Results:', fontsize=11,
                          underline=True)
        self.create_param_widget(
            self.get_param('selected_results'),
            **_get_param_widget_config('selected_results'))

        self.create_any_widget(
            'result_info',  ReadOnlyTextWidget, gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,fixedHeight=200,
            alignment=QtCore.Qt.AlignTop, visible=False)
        self.create_radio_button_group(
            'radio_datashape', ['1D plot', '2D image'], vertical=False,
            gridPos=(-1, 0, 1, 1), visible=False)
        self.create_param_widget(
            self.get_param('plot_ax1'), **_get_param_widget_config('plot_ax1'))
        self.create_param_widget(
            self.get_param('plot_ax2'), **_get_param_widget_config('plot_ax2'))

    def __connect_signals(self):
        self.param_widgets['selected_results'].currentIndexChanged.connect(
            self.__result_selection_changed)
        self._widgets['radio_datashape'].new_button.connect(
            self.__update_plot_dimension_selection)
        self.param_widgets['plot_ax1'].currentIndexChanged.connect(
            partial(self.__select_plot_axis, 1))
        self.param_widgets['plot_ax2'].currentIndexChanged.connect(
            partial(self.__select_plot_axis, 2))

    @QtCore.pyqtSlot()
    def update_selection_choices(self):
        """
        Update the choice of selections based on the current items in the
        WorkflowResults.
        """
        _curr_choice = self.get_param_value('selected_results')
        _new_choices = (['No selection'] +
                        [f'{_val} (node #{_key:03d})'
                         for _key, _val in RESULTS.labels.items()])
        if _curr_choice not in _new_choices:
            _curr_choice = 'No selection'
            self.set_param_value('selected_results', _curr_choice)
        self.params['selected_results'].choices = _new_choices
        self.param_widgets['selected_results'].currentIndexChanged.disconnect(
            self.__result_selection_changed)
        self.param_widgets['selected_results'].update_choices(_new_choices)
        self.param_widgets['selected_results'].setCurrentText(_curr_choice)
        self.param_widgets['selected_results'].currentIndexChanged.connect(
            self.__result_selection_changed)


    @QtCore.pyqtSlot(int)
    def __result_selection_changed(self, index):
        """
        Received signal that the selection in the results combo box has
        changed.

        Parameters
        ----------
        index : int
            The new QComboBox selection index.
        """
        print('New index: ', index)
        print(('Combo entry: '
               f'"{self.param_widgets["selected_results"].currentText()}"'))
        print(f'Param value: "{self.get_param_value("selected_results")}"')
        if index == 0:
            self._active_node = -1
            self.__change_derived_widget_visibility(False)
        elif index > 0:
            self._active_node = int(
                self.param_widgets["selected_results"].currentText()[-4:-1])
            self.set_param_value('n_dim',
                                 len(RESULTS.shapes[self._active_node]))
            self.__update_text_description_of_node_results()
            self.__update_dim_choices_for_plot_selection()

    @QtCore.pyqtSlot(int, str)
    def __update_plot_dimension_selection(self, dim_index, dim_label):
        """
        Update the selection

        Parameters
        ----------
        dim_index : TYPE
            DESCRIPTION.
        dim_label : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if dim_index == 0:
            self._2d_plot = False
            if self.param_composite_widgets['plot_ax2'].isVisible():
                self.param_composite_widgets['plot_ax2'].setVisible(False)
        elif dim_index == 1:
            self._2d_plot = True
            if self._config['widget_visibility']:
                self.param_composite_widgets['plot_ax2'].setVisible(True)
        self._config['plot_dim'] = dim_index + 1
        print('Updated plot dimension to ', dim_label)

    def __update_dim_choices_for_plot_selection(self):
        _new_choices = np.arange((self.get_param_value('n_dim')))


    def __change_derived_widget_visibility(self, visible):
        """
        Change the visibility of all 'derived' widgets.

        This method changes the visibility of the InfoBox and selection
        widgets.

        Parameters
        ----------
        visible : bool
            Keyword to toggle visibility.
        """
        self._config['widget_visibility'] = visible
        self._widgets['result_info'].setVisible(visible)
        self._widgets['radio_datashape'].setVisible(visible)
        self.param_composite_widgets['plot_ax1'].setVisible(visible)
        self.param_composite_widgets['plot_ax2'].setVisible(
            visible and self._2d_plot)


    def __update_text_description_of_node_results(self):
        _txt = self.param_widgets["selected_results"].currentText()
        if _txt in ['None', 'No selection', '']:
            self._widgets['result_info'].setVisible(False)
            return
        _id = int(_txt[-4:-1])
        _meta = RESULTS.get_result_metadata(_id)
        _dim = len(RESULTS.shapes[_id])
        _scandim = SCAN.get_param_value('scan_dim')
        _ax_labels = _meta['axis_labels']
        _ax_units= _meta['axis_units']
        _ax_ranges = _meta['axis_ranges']
        _txt = ''
        for _axis in range(_dim):
            if isinstance(_ax_ranges[_axis], (np.ndarray, list, tuple)):
                _range = (f'{_ax_ranges[_axis][0]:.6f} .. '
                          f'{_ax_ranges[_axis][-1]:.6f} {_ax_units[_axis]}')
            else:
                _range = f'unknown range (unit: {_ax_units[_axis]}'
            if _axis < _scandim:
                _txt += f'Axis #{_axis:02d} (scan):\n'
            else:
                _txt += f'Axis #{_axis:02d} (data):\n'
            _txt += (f'  Label: {_ax_labels[_axis]}\n'
                     f'  Range: {_range}\n')
        self._widgets['result_info'].setText(_txt)
        self.__change_derived_widget_visibility(True)

    def __select_plot_axis(self, plot_dim):
        ...


if __name__ == '__main__':
    import pickle
    import sys
    from pydidas.core import Dataset
    from pydidas.constants import STANDARD_FONT_SIZE
    RESULTS.__dict__ = pickle.load(
        open('d:/tmp/saved_results/results.pickle', 'rb'))
    for _i in [1, 2]:
        _data = Dataset(np.load(f'd:/tmp/saved_results/node_{_i:02d}.npy'))
        _meta = pickle.load(
            open(f'd:/tmp/saved_results/node_{_i:02d}.pickle', 'rb'))
        _data.axis_labels = _meta['axis_labels']
        _data.axis_units = _meta['axis_units']
        _data.axis_ranges = _meta['axis_ranges']
        RESULTS._WorkflowResults__composites[_i] = _data

    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = QtWidgets.QMainWindow()
    _w = ResultSelectorForOutput(
        None, get_generic_parameter('selected_results'))
    _w.update_selection_choices()
    gui.setCentralWidget(_w)

    gui.show()
    sys.exit(app.exec_())

    # app.deleteLater()
