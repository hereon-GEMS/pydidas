# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the Hdf5DatasetSelector widget which allows to select a dataset
from an Hdf5 file and to browse through its data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Hdf5DatasetSelector']

from functools import partial

import h5py
import hdf5plugin
from qtpy import QtWidgets, QtCore
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser

from ...core import FrameConfigError
from ...core.utils import get_hdf5_populated_dataset_keys
from ...core.constants import QT_COMBO_BOX_SIZE_POLICY
from ..factory import CreateWidgetsMixIn
from ..utilities import apply_widget_properties


DEFAULT_FILTERS = {'/entry/instrument/detector/detectorSpecific/':
                   '"detectorSpecific"\nkeys (Eiger detector)'}


class Hdf5DatasetSelector(QtWidgets.QWidget, CreateWidgetsMixIn):
    """
    The Hdf5DatasetSelector is a compound widget which allows to select
    an hdf5 dataset key and the frame number. By convention, the first
    dimension of a n-dimensional (n >= 3) dataset is the frame number. Any
    2-dimensional datasets will be interpreted as single frames.

    Parameters
    ----------
    parent : Union[QWidget, None], optional
        The parent widget. The default is None.
    viewWidget : Union[QWidget, None], optional
        A widget for a full view. It can also be registered later using
        the  *register_view_widget* method. The default is None.
    datasetKeyFilters : Union[dict, None], optional
        A dictionary with dataset keys to be filtered from the list
        of displayed datasets. Entries must be in the format
        {<Key to filter>: <Descriptive text for checkbox>}.
        The default is None.
    **kwargs : dict
        Any additional keyword arguments. See below for supported arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the generic QWidget. Use the
        Qt attribute name with a lowercase first character. Examples are
        ``fixedWidth``, ``fixedHeight``.
    """
    new_frame_signal = QtCore.Signal(object)

    def __init__(self, parent=None, viewWidget=None, datasetKeyFilters=None,
                 **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        apply_widget_properties(self, **kwargs)

        self._config = dict(activeDsetFilters = [],
                            currentDset = None,
                            currentFname = None,
                            currentIndex = None,
                            dsetFilters = (datasetKeyFilters
                                           if datasetKeyFilters is not None
                                           else DEFAULT_FILTERS))
        self.flags = dict(slotActive = False,
                          autoUpdate = 0)
        self._widgets['viewer'] = viewWidget
        self._frame = None
        self.__create_widgets_and_layout()
        self.__connect_slots()

    def __create_widgets_and_layout(self):
        """
        Create all required widgets and the layout.

        This private method will create all the required and widgets and
        the layout.
        """
        _layout = QtWidgets.QGridLayout()
        _layout.setHorizontalSpacing(15)
        self.setLayout(_layout)

        # create checkboxes and links for all filter keys:
        _w_filter_keys = []
        for key, text in self._config['dsetFilters'].items():
            _widget = QtWidgets.QCheckBox(f'Ignore {text}')
            _widget.setChecked(False)
            _widget.stateChanged.connect(
                partial(self._toggle_filter_key, _widget, key))
            _w_filter_keys.append(_widget)
        for i, widget in enumerate(_w_filter_keys):
            _layout.addWidget(widget, i // 2, i % 2, 1, 2)

        # Determine the layout row offset for the other widgets based on
        # the number of filter key checkboxes:
        _row_offset = len(_w_filter_keys) // 2 + len(_w_filter_keys) % 2

        self.create_label(None, 'Min. dataset\nsize: ',
                          gridPos=(_row_offset, 0, 1, 1))
        self.create_label(None, 'Min. dataset\ndimensions: ',
                          gridPos=(_row_offset, 3, 1, 1))
        self.create_label(None, 'Filtered datasets: ',
                          gridPos=(1 + _row_offset, 0, 1, 1))
        self.create_spin_box('min_datasize', value=50,
                             valueRange=(0, int(1e9)),
                             gridPos=(_row_offset, 1, 1, 1))
        self.create_spin_box('min_datadim', value=2, valueRange=(0, 3),
                             gridPos=(_row_offset, 4, 1, 1))
        self.create_combo_box(
            'select_dataset', minimumContentsLength=25,
            sizeAdjustPolicy=QT_COMBO_BOX_SIZE_POLICY,
            gridPos=(1 + _row_offset, 1, 1, 4))
        self.add_any_widget('frame_browser', HorizontalSliderWithBrowser(),
                            gridPos=(2 + _row_offset, 0, 1, 5))
        self.create_button(
            'but_view', 'Show full frame', gridPos=(3 + _row_offset, 3, 1, 2),
            alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.create_check_box('auto_update', 'Auto update',
                              gridPos=(3 + _row_offset, 0, 1, 2))
        self.setVisible(False)

    def __connect_slots(self):
        """
        Connect all required widget slots (except for the filter keys
        which are set up dynamically along their widgets)
        """
        self._widgets['min_datasize'].valueChanged.connect(
            self.__populate_dataset_list)
        self._widgets['min_datadim'].valueChanged.connect(
            self.__populate_dataset_list)
        self._widgets['select_dataset'].currentTextChanged.connect(
            self.__select_dataset)
        self._widgets['frame_browser'].valueChanged.connect(
            self._index_changed)
        self._widgets['but_view'].clicked.connect(self.click_view_button)
        self._widgets['auto_update'].clicked.connect(self._toggle_auto_update)

    def __populate_dataset_list(self):
        """
        Populate the dateset selection with a filtered list of datasets.

        This method reads the structure of the hdf5 file and filters the
        list of datasets according to the selected criteria. The filtered list
        is used to populate the selection drop-down menu.
        """
        _dset_filter_min_size = self._widgets['min_datasize'].value()
        _dset_filter_min_dim = self._widgets['min_datadim'].value()
        _datasets = get_hdf5_populated_dataset_keys(
            self._config['currentFname'],
            min_size=_dset_filter_min_size,
            min_dim=_dset_filter_min_dim,
            ignore_keys=self._config['activeDsetFilters'])
        self._widgets['select_dataset'].currentTextChanged.disconnect()
        self._widgets['select_dataset'].clear()
        self._widgets['select_dataset'].addItems(_datasets)
        self._widgets['select_dataset'].currentTextChanged.connect(
            self.__select_dataset)
        if len(_datasets) > 0:
            self.__select_dataset()
        else:
            self._widgets['but_view'].setEnabled(False)

    def __select_dataset(self):
        """
        Select a dataset from the drop-down list.

        This internal method is called by the Qt event system if the QComBoBox
        text has changed to notify the main program that the user has selected
        a different dataset to be visualized. This method also updates the
        accepted frame range for the sliders.
        """
        _dset = self._widgets['select_dataset'].currentText()
        with h5py.File(self._config['currentFname'], 'r') as _file:
            _shape = _file[_dset].shape
        n_frames = _shape[0] if len(_shape) >= 3 else 1
        self._widgets['frame_browser'].setRange(0, n_frames - 1)
        self._config['currentIndex'] = 0
        self._widgets['but_view'].setEnabled(True)
        self.__update()

    def __update(self, new_frame=False):
        """
        Propagate an update to any consumers.

        This method will read a new frame from the file if any consumers
        demand it (consumers must active the signal slot or the automatic
        update). The new frame will be passed to any active view/preview
        widgets and a signal emitted if the slot is active.

        Parameters
        ----------
        new_frame : bool
            A flag to tell __updateto process a new frame, e.g. after changing
            the dataset.
        """
        if self.flags['autoUpdate'] or self.flags['slotActive'] or new_frame:
            self.__get_frame()
        if self.flags['slotActive']:
            self.new_frame_signal.emit(self._frame)
        if (self.flags['autoUpdate']
                and self._widgets['viewer'] is not None):
            self._widgets['viewer'].setData(self._frame)

    def __get_frame(self):
        """
        Get and store a frame.

        This internal method reads an image frame from the hdf5 dataset and
        stores it internally for further processing (passing to other widgets
        / signals)
        """
        _dset = self._widgets['select_dataset'].currentText()
        with h5py.File(self._config['currentFname'], 'r') as _file:
            _dset = _file[_dset]
            _ndim = len(_dset.shape)
            if _ndim >= 3:
                self._frame = _dset[self._config['currentIndex']]
            elif _ndim == 2:
                self._frame = _dset[...]

    def register_view_widget(self, widget):
        """
        Register a view widget to be used for full visualization of data.

        This method registers an external view widget for data visualization.
        Note that the widget must accept frames through a ``setData`` method.

        Parameters
        ----------
        widget : QWidget
            A widget with a ``setData`` method to pass frames.

        Raises
        ------
        TypeError
            If the widget does not have a ``setData`` method.
        """
        if (isinstance(widget, QtWidgets.QWidget) and
                hasattr(widget, 'setData')):
            self._widgets['viewer'] = widget
            return
        raise TypeError('Error: Object must be a widget with a setData '
                        'method.')

    def _toggle_filter_key(self, widget, key):
        """
        Add or remove the filter key from the active dataset key filters.

        This method will add or remove the <key> which is associated with the
        checkbox widget <widget> from the active dataset filters.
        Note: This method should never be called by the user but it is
        connected to the checkboxes which activate or deactive the respective
        filters.

        Parameters
        ----------
        widget : QWidget
            The checkbox widget which is associated with enabling/disabling
            the filter key.
        key : str
            The dataset filter string.
        """
        if widget.isChecked() and key not in self._config['activeDsetFilters']:
            self._config['activeDsetFilters'].append(key)
        if not widget.isChecked() and key in self._config['activeDsetFilters']:
            self._config['activeDsetFilters'].remove(key)
        self.__populate_dataset_list()

    def _toggle_auto_update(self):
        """
        Toggle automatic updates based on the state of the checkbox widget.
        """
        self.flags['autoUpdate'] = self._widgets['auto_update'].isChecked()

    def enable_signal_slot(self, enable):
        """
        Toggle the signal slot to emit the selected frame as signal for other
        widgets.

        Parameters
        ----------
        enable : bool
            Flag to enable the signal slot. If True, a signal is emitted every
            time a new frame is selected. If False, the signal slot is not
            used.
        """
        self.flags['slotActive'] = enable

    def set_filename(self, name):
        """
        Set the filename of the hdf5 file to be used.

        This method stores the filename and calls the internal method to
        populate the list of datasets included in the file.

        Parameters
        ----------
        name : str
            The full file system path to the hdf5 file.
        """
        self._config['currentFname'] = name
        self.__populate_dataset_list()

    def _index_changed(self, index):
        """
        Store the new index from the frame selector.

        This method is connected to the frame selector (slider/field) and
        calls for an update of the frame if the index has changed.

        Parameters
        ----------
        index : int
            The index in the image dataset.
        """
        self._config['currentIndex'] = index
        self.__update(True)

    def click_view_button(self):
        """
        Process clicking the view button.

        This method is connected to the clicked event of the View button.
        """
        if not self.flags['autoUpdate']:
            self.__get_frame()
        if not isinstance(self._widgets['viewer'], QtWidgets.QWidget):
            raise FrameConfigError('The reference is not a widget')
        self._widgets['viewer'].setData(self._frame)
