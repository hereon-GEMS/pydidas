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

from numbers import Integral, Real
from functools import partial
from copy import copy

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
from pydidas.utils import SignalBlocker

RESULTS = WorkflowResults()
SCAN = ScanSettings()


def _param_widget_config(param_key):
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


def _get_range_as_formatted_string(_range):
    """
    Get a formatted string representation of an iterable range.

    Parameters
    ----------
    _range : Union[np.ndarray, list, tuple]
        The input range.

    Returns
    -------
    str :
        The formatted string representation
    """
    try:
        _min, _max = _range[0], _range[-1]
        _str_items = []
        for _item in [_min, _max]:
            if isinstance(_item, Integral):
                _item = f'{_item:d}'
            elif isinstance(_item, Real):
                _item = f'{_item:.6f}'
            else:
                _item = str(_item)
            _str_items.append(_item)
        return _str_items[0] + ' ... ' + _str_items[1]
    except:
        return 'unknown range'


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
        self._config = {'widget_visibility': False,
                        'scan_use_timeline': False,
                        # 'scan_n': -1,
                        # 'scan_shape': (),
                        '2d_plot': False,
                        'plot_dim': 1,
                        }
        self._active_node = -1
        self.add_param(select_results_param)
        self.set_default_params()
        self.__create_widgets()
        self.__connect_signals()
        self.get_and_store_result_node_infos()
        # self.get_and_store_latest_scan_settings()

    def __create_widgets(self):
        """
        Create all sub-widgets and populate the UI.
        """
        _layout = QtWidgets.QGridLayout()
        _layout.setContentsMargins(5, 5, 0, 0)
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(_layout)

        self.create_label('label_results', 'Results:', fontsize=11,
                          underline=True)
        self.create_param_widget(self.get_param('selected_results'),
                                 **_param_widget_config('selected_results'))
        self.create_radio_button_group(
            'radio_arrangement', ['by scan shape', 'as a timeline'],
            vertical=False, gridPos=(-1, 0, 1, 1), visible=False,
            title='Arrangement of results:')
        self.create_any_widget(
            'result_info',  ReadOnlyTextWidget, gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,fixedHeight=200,
            alignment=QtCore.Qt.AlignTop, visible=False)
        self.create_radio_button_group(
            'radio_datashape', ['1D plot', '2D image'], vertical=False,
            gridPos=(-1, 0, 1, 1), visible=False, title='Result plot type:')
        self.create_param_widget(self.get_param('plot_ax1'),
                                 **_param_widget_config('plot_ax1'))
        self.create_param_widget(self.get_param('plot_ax2'),
                                 **_param_widget_config('plot_ax2'))

    def __connect_signals(self):
        """
        Connect all required signals.
        """
        self.param_widgets['selected_results'].currentIndexChanged.connect(
            self.__selected_new_node)
        self._widgets['radio_datashape'].new_button.connect(
            self.__new_selection_of_plot_dimension)
        self._widgets['radio_arrangement'].new_button.connect(
            self.__new_selection_of_scan_result_arrangement)
        self.param_widgets['plot_ax1'].currentIndexChanged.connect(
            partial(self.__select_plot_axis, 1))
        self.param_widgets['plot_ax2'].currentIndexChanged.connect(
            partial(self.__select_plot_axis, 2))

    # def get_and_store_latest_scan_settings(self):
    #     """
    #     Get and store the latest settings from the global ScanSettings.
    #     """
    #     self._config['scan_n'] = SCAN.n_total
    #     self._config['scan_shape'] = SCAN.shape

    def get_and_store_result_node_infos(self):
        """
        Get and store the labels of the current nodes in the WorkflowResults.

        This method will also update the choice of selections based on these
        items.
        """
        _curr_choice = self.get_param_value('selected_results')
        _new_choices = (['No selection'] +
                        [f'{_val} (node #{_key:03d})'
                         for _key, _val in RESULTS.labels.items()])
        if _curr_choice not in _new_choices:
            _curr_choice = 'No selection'
            self.set_param_value('selected_results', _curr_choice)
        self.params['selected_results'].choices = _new_choices
        with SignalBlocker(self.param_widgets['selected_results']):
            self.param_widgets['selected_results'].update_choices(_new_choices)
            self.param_widgets['selected_results'].setCurrentText(_curr_choice)

    @QtCore.pyqtSlot(int)
    def __selected_new_node(self, index):
        """
        Received signal that the selection in the results combo box has
        changed.

        Parameters
        ----------
        index : int
            The new QComboBox selection index.
        """
        if index == 0:
            self._active_node = -1
            self.__change_derived_widget_visibility(False)
        elif index > 0:
            self._active_node = self.__get_active_node_from_selected_results()
            self.__calc_and_store_ndim_of_results()
            self.__update_text_description_of_node_results()
            self.__update_dim_choices_for_plot_selection()

    def __get_active_node_from_selected_results(self):
        """
        Get the nodeID of the active node from the "selected_results"
        Parameter.

        Returns
        -------
        int :
            The nodeID of the selected node.
        """
        _i = int(self.param_widgets["selected_results"].currentText()[-4:-1])
        return _i

    def __calc_and_store_ndim_of_results(self):
        """
        Update the number of dimensions the results will have and store the
        new number.
        """
        _ndim = RESULTS.ndims[self._active_node]
        if self._config['scan_use_timeline']:
            _ndim -= SCAN.ndim - 1
        self._config['result_ndim'] = _ndim

    @QtCore.pyqtSlot(int, str)
    def __new_selection_of_plot_dimension(self, dim_index, dim_label):
        """
        Update the selection

        Parameters
        ----------
        dim_index : int
            THe index of the dimension selection.
        dim_label : str
            The label of the dimension selection.
        """
        self._config['2d_plot'] = bool(dim_index)
        self.param_composite_widgets['plot_ax2'].setVisible(
            dim_index and self._config['widget_visibility'])
        self._config['plot_dim'] = dim_index + 1

    def __update_dim_choices_for_plot_selection(self):
        """
        Calculate and update the basic dimension choices for the plot
        slicing.
        """
        _new_choices = list(np.arange((self._config['result_ndim'])))
        for _ax in range(1, self._config['plot_dim'] + 1):
            _axwidget = self.param_widgets[f'plot_ax{_ax}']
            _axparam = self.params[f'plot_ax{_ax}']
            _curr_choices = _axparam.choices
            if _ax == 2:
                _new_choices.remove(self.get_param_value('plot_ax1'))
            if _axparam.value not in _new_choices:
                _axparam.choices = (_curr_choices + [_new_choices[0]])
                _axparam.value = _new_choices[0]
            _axparam.choices = _new_choices
            with SignalBlocker(_axwidget):
                _axwidget.update_choices(_new_choices)



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
        self._widgets['radio_arrangement'].setVisible(visible)
        self.param_composite_widgets['plot_ax1'].setVisible(visible)
        self.param_composite_widgets['plot_ax2'].setVisible(
            visible and self._config['2d_plot'])

    @QtCore.pyqtSlot(int, str)
    def __new_selection_of_scan_result_arrangement(self, index, label):
        """
        Get and store the current selection for the organization of the
        scan results in a timeline or using the ScanSettings shape.

        This method also updates the text in the ReadOnlyTextWidget to
        reflect the selection of the dimensions of the scan.

        Parameters
        ----------
        index : int
            The index of the newly activated button.
        label : str
            The label of the newly activated button.
        """
        self._config['scan_use_timeline'] = bool(index)
        self.__update_text_description_of_node_results()

    def __update_text_description_of_node_results(self):
        """
        Update the text in the "result_info" ReadOnlyTextWidget based on the
        selection of the "selected_results" Parameter.
        """
        _txt = self.get_param_value('selected_results')
        # print(_txt, self.get_param_value('selected_results'))
        # if _txt in ['None', 'No selection', '']:
        #     print('No selection: ', _txt)
        #     self._widgets['result_info'].setVisible(False)
        #     return
        # _id = int(_txt[-4:-1])
        _txt = self.__get_edited_result_metadata_string()
        self._widgets['result_info'].setText(_txt)
        self.__change_derived_widget_visibility(True)

    def __get_edited_result_metadata_string(self):
        """
        Get the edited metadata from WorkflowResults as a formatted string.

        Returns
        -------
        str :
            The formatted string with a representation of all the metadata.
        """
        _meta = RESULTS.get_result_metadata(self._active_node)
        _scandim = SCAN.get_param_value('scan_dim')
        _ax_labels = copy(_meta['axis_labels'])
        _ax_units= copy(_meta['axis_units'])
        _ax_ranges = {_key: _get_range_as_formatted_string(_range)
                         for _key, _range in _meta['axis_ranges'].items()}
        _ax_types = {_key: ('(scan)' if _key < _scandim else '(data)')
                     for _key in _meta['axis_labels'].keys()}
        if self._config['scan_use_timeline']:
            _ax_labels[0] = 'chronological frame number'
            _ax_units[0] = ''
            _ax_ranges[0] = f'0 ... {SCAN.n_total - 1}'
            if _scandim > 1:
                _dims_to_edit = RESULTS.ndims[self._active_node] - _scandim
                for _index in range(_dims_to_edit):
                    for _item in [_ax_labels, _ax_units, _ax_ranges,
                                  _ax_types]:
                        _item[_index + 1] = _item[_index + _scandim]
                        del _item[_index + _scandim]
        return ''.join([(f'Axis #{_axis:02d} {_ax_types[_axis]}:\n'
                         f'  Label: {_ax_labels[_axis]}\n'
                         f'  Range: {_ax_ranges[_axis]} {_ax_units[_axis]}\n')
                        for _axis in _ax_labels])

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
    _w.get_and_store_result_node_infos()
    gui.setCentralWidget(_w)

    gui.show()
    sys.exit(app.exec_())

    # app.deleteLater()
