# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with Warning class for showing notifications."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Hdf5DatasetSelector']


from functools import partial

import h5py
import hdf5plugin

from PyQt5 import QtWidgets, QtCore
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser

from .._exceptions import FrameConfigError
from ..utils import get_hdf5_populated_dataset_keys

DEFAULT_FILTERS = {'/entry/instrument/detector/detectorSpecific/':
                   '"detectorSpecific"\nkeys (Eiger detector)'}

# create a matrix with button names for the view / preview button based on
# activation of autoUpdate (0th index) and activation of preview (1st index):
PREVIEW_TEXT = [['Show frame preview', 'Show frame preview'],
                ['Activate frame preview', 'Deactivate frame preview']]
VIEW_TEXT = [['Show full frame', 'Show full frame'],
             ['Activate full frame view', 'Deactivate full frame view']]


class Hdf5DatasetSelector(QtWidgets.QWidget):
    """
    The Hdf5DatasetSelector is a compound widget which allows to select
    an hdf5 dataset key and the frame number. By convention, the first
    dimension of a n-dimensional (n >= 3) dataset is the frame number. Any
    2-dimensional datasets will be interpreted as single frames.
    """
    new_frame_signal = QtCore.pyqtSlot(object)

    def __init__(self, parent=None, previewWidget=None, viewWidget=None,
                 datasetKeyFilters=None):
        """
        Instanciation method.

        Setup the Hdf5DatasetSelector class with widgets and slots.

        Parameters
        ----------
        parent : Union[QWidget, None], optional
            The parent widget. The default is None.
        previewWidget : Union[QWidget, None], optional
            A preview widget. It can also be registered later using the
            *register_preview_widget* method. The default is None.
        viewWidget : Union[QWidget, None], optional
            A widget for a full view. It can also be registered later using
            the  *register_view_widget* method. The default is None.
        datasetKeyFilters : Union[dict, None], optional
            A dictionary with dataset keys to be filtered from the list
            of displayed datasets. Entries must be in the format
            {<Key to filter>: <Descriptive text for checkbox>}.
            The default is None.

        Returns
        -------
        None.
        """
        super().__init__(parent)

        self.params = dict(activeDsetFilters = [],
                           currentDset = None,
                           dsetFilterMinSize = 50,
                           dsetFilterMinDim = 3,
                           currentFname = None,
                           currentIndex = None,
                           dsetFilters = (datasetKeyFilters
                                          if datasetKeyFilters is not None
                                          else DEFAULT_FILTERS))
        # setup flags for autoUpdate, previewActive and viewActive as int
        # to allow using them directly to select the entries in
        # (PRE)VIEW_TEXT

        self.flags = dict(slotActive = False,
                          autoUpdate = 0,
                          previewActive = 0,
                          viewActive = 0)
        self.w_view = viewWidget
        self.w_preview = previewWidget
        self._frame = None

        self.__create_widgets_and_layout()

        # connect all required widget slots (except for the filter keys
        # which are set up dynamically along their widgets):
        self.w_min_datasize.valueChanged.connect(self.__populate_dataset_list)
        self.w_min_datadim.valueChanged.connect(self.__populate_dataset_list)
        self.w_select_dataset.currentTextChanged.connect(self.__select_dataset)
        self.w_frame_browser.valueChanged.connect(self._index_changed)
        self.w_but_preview.clicked.connect(self.click_preview_button)
        self.w_but_view.clicked.connect(self.click_view_button)
        self.w_auto_update.clicked.connect(self._toggle_auto_update)

    def __create_widgets_and_layout(self):
        """
        Create all required widgets and the layout.

        This private method will create all the required and widgets and
        the layout.

        Returns
        -------
        None.
        """
        # create checkboxes and links for all filter keys:
        _w_filter_keys = []
        for key in self.params['dsetFilters']:
            _text = self.params['dsetFilters'][key]
            _widget = QtWidgets.QCheckBox(f'Ignore {_text}')
            _widget.setChecked(False)
            _widget.stateChanged.connect(
                partial(self._toggle_filter_key, _widget, key))
            _w_filter_keys.append(_widget)
        # determine the layout row offset for the other widgets based on
        # the number of filter key checkboxes:
        _row_offset = len(_w_filter_keys) // 2 + len(_w_filter_keys) % 2

        self.w_min_datasize = QtWidgets.QSpinBox()
        self.w_min_datasize.setValue(50)
        self.w_min_datasize.setRange(0, int(1e9))
        self.w_min_datasize.setFixedWidth(50)

        self.w_min_datadim = QtWidgets.QSpinBox()
        self.w_min_datadim.setValue(2)
        self.w_min_datadim.setRange(0, 3)
        self.w_min_datadim.setFixedWidth(50)

        self.w_select_dataset = QtWidgets.QComboBox()
        self.w_select_dataset.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.w_select_dataset.setMinimumContentsLength(25)

        self.w_frame_browser = HorizontalSliderWithBrowser()

        self.w_but_preview = QtWidgets.QPushButton('Show frame preview')

        self.w_but_view = QtWidgets.QPushButton('Show full frame')

        self.w_auto_update = QtWidgets.QCheckBox('Auto update')

        _label1 = QtWidgets.QLabel('Min. dataset\nsize: ')
        _label2 = QtWidgets.QLabel('Min. dataset\ndimensions: ')
        _label3 = QtWidgets.QLabel('Filtered datasets: ')

        _layout = QtWidgets.QGridLayout()
        _layout.setHorizontalSpacing(15)
        for i, widget in enumerate(_w_filter_keys):
            _layout.addWidget(widget, i // 2, i % 2, 1, 2)
        _layout.addWidget(_label1, 0 + _row_offset, 0, 1, 1)
        _layout.addWidget(self.w_min_datasize, 0 + _row_offset, 1, 1, 1)
        _layout.addWidget(_label2, 0 + _row_offset, 3, 1, 1)
        _layout.addWidget(self.w_min_datadim, 0 + _row_offset, 4, 1, 1)
        _layout.addWidget(_label3, 1 + _row_offset, 0, 1, 1)
        _layout.addWidget(self.w_select_dataset, 1 + _row_offset, 1, 1, 4)
        _layout.addWidget(self.w_frame_browser, 2 + _row_offset, 0, 1, 5)
        _layout.addWidget(self.w_but_preview, 3 + _row_offset, 0, 1, 2)
        _layout.addWidget(self.w_auto_update, 3 + _row_offset, 2, 1, 1)
        _layout.addWidget(self.w_but_view, 3 + _row_offset, 3, 1, 2)
        self.setLayout(_layout)
        self.setVisible(False)

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

        Returns
        -------
        None.
        """
        if widget.isChecked() and key not in self.params['activeDsetFilters']:
            self.params['activeDsetFilters'].append(key)
        if not widget.isChecked() and key in self.params['activeDsetFilters']:
            self.params['activeDsetFilters'].remove(key)
        self.__populate_dataset_list()

    def _toggle_auto_update(self):
        """
        Toggle automatic updates based on the state of the checkbox widget.

        This method will set the internal flag for automatic updates and
        select the appropriate text for the selection buttons.
        Note: This method should never be called by the user but it is
        connected to the checkbox and called automatically.

        Returns
        -------
        None.
        """
        self.flags['autoUpdate'] = int(self.w_auto_update.isChecked())
        self.w_but_preview.setText(
            PREVIEW_TEXT[self.flags['autoUpdate']][self.flags['previewActive']])
        self.w_but_view.setText(
            VIEW_TEXT[self.flags['autoUpdate']][self.flags['viewActive']])

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

        Returns
        -------
        None.
        """
        self.flags['slotActive'] = enable if enable is True else False

    def register_view_widget(self, widget):
        """
        Register a view widget to be used for full visualization of data.

        This method registers an external view widget for data visualization.
        Note that the widget must accept frames through a <setData> method.

        Parameters
        ----------
        widget : QWidget*
            A widget with a <setData> method to pass frames.

        Returns
        -------
        None.
        """
        self.w_view = widget

    def register_preview_widget(self, widget):
        """
        Register a preview widget to create data previews.

        Note that the widget must accept frames through a <setData> method.

        Parameters
        ----------
        widget : QWidget*
            A widget with a <setData> method to pass frames.

        Returns
        -------
        None.
        """
        self.w_preview = widget

    def set_filename(self, name):
        """
        Set the filename of the hdf5 file to be used.

        This method stores the filename and calls the internal method to
        populate the list of datasets included in the file.

        Parameters
        ----------
        name : str
            The full file system path to the hdf5 file.

        Returns
        -------
        None.
        """
        self.params['currentFname'] = name
        self.__populate_dataset_list()

    def _index_changed(self, index):
        """
        Store the new index from the frame selector.

        This method is connected to the frame selector (slider/field) and
        calls for an update of the frame if the index has changed.

        Parameters
        ----------
        index : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.params['currentIndex'] = index
        self.__update()

    def __update(self):
        """
        Propagate an update to any consumers.

        This method will read a new frame from the file if any consumers
        demand it (consumers must active the signal slot or the automatic
        update). The new frame will be passed to any active view/preview
        widgets and a signal emitted if the slot is active.

        Returns
        -------
        None.
        """
        if self.flags['autoUpdate'] or self.flags['slotActive']:
            self.__get_frame()
        if self.flags['slotActive']:
            self.new_frame_signal.emit(self._frame)
        if (self.flags['autoUpdate']
                and self.flags['previewActive']
                and self.w_preview is not None):
            self.__set_view(self.w_preview)
        if (self.flags['autoUpdate']
                and self.flags['viewActive']
                and self.w_view is not None):
            self.__set_view(self.w_view)

    def __populate_dataset_list(self):
        """
        Populate the dateset selection with a filtered list of datasets.

        This method reads the structure of the hdf5 file and filters the
        list of datasets according to the selected criteria. The filtered list
        is used to populate the selection drop-down menu.

        Returns
        -------
        None.
        """
        self.params['dsetFilterMinSize'] = self.w_min_datasize.value()
        self.params['dsetFilterMinDim'] = self.w_min_datadim.value()
        _datasets = get_hdf5_populated_dataset_keys(
            self.params['currentFname'],
            minDataSize=self.params['dsetFilterMinSize'],
            minDataDim=self.params['dsetFilterMinDim'],
            ignoreKeys=self.params['activeDsetFilters'])
        self.w_select_dataset.currentTextChanged.disconnect()
        self.w_select_dataset.clear()
        self.w_select_dataset.addItems(_datasets)
        self.w_select_dataset.currentTextChanged.connect(self.__select_dataset)
        if len(_datasets) > 0:
            self.__select_dataset()
        else:
            self.w_but_preview.setEnabled(False)
            self.w_but_view.setEnabled(False)

    def __get_frame(self):
        """
        Get and store a frame.

        This internal method reads an image frame from the hdf5 dataset and
        stores it internally for further processing (passing to other widgets
        / signals)

        Returns
        -------
        None.
        """
        with h5py.File(self.params['currentFname'], 'r') as f:
            _dset = f[self.params['currentDset']]
            _ndim = len(_dset.shape)
            if _ndim >= 3:
                self._frame = _dset[self.params['currentIndex']]
            elif _ndim == 2:
                self._frame = _dset[...]

    def __select_dataset(self):
        """
        Select a dataset from the drop-down list.

        This internal method is called by the Qt event system if the QComBoBox
        text has changed to notify the main program that the user has selected
        a different dataset to be visualized. This method also updates the
        accepted frame range for the sliders.

        Returns
        -------
        None.
        """
        self.params['currentDset'] = self.w_select_dataset.currentText()
        with h5py.File(self.params['currentFname'], 'r') as f:
            _shape = f[self.params['currentDset']].shape
        n_frames = _shape[0] if len(_shape) >= 3 else 0
        self.w_frame_browser.setRange(0, n_frames - 1)
        self.params['currentIndex'] = 0
        self.w_but_preview.setEnabled(True)
        self.w_but_view.setEnabled(True)

    def click_preview_button(self):
        """
        Process clicking the preview button.

        This method is connected to the clicked event of the Preview button.

        Returns
        -------
        None.
        """
        self.__process_click('previewActive', self.w_but_preview,
                             self.w_preview, PREVIEW_TEXT)

    def click_view_button(self):
        """
        Process clicking the view button.

        This method is connected to the clicked event of the View button.

        Returns
        -------
        None.
        """
        self.__process_click('viewActive', self.w_but_view,
                             self.w_view, VIEW_TEXT)

    def __process_click(self, flag, but_widget, view_widget, text):
        """
        Process clicking the button.

        This method is a wrapper to handle clicks on either the View of
        Preview button. It

        Parameters
        ----------
        flag : str
            The name of the flag for the respective (pre)view state.
        but_widget : QWidget
            The instance of the pressed Button.
        view_widget : QWidget
            The instance of the output widget.
        text : list
            A list with button name entries encoded by the flag states.

        Returns
        -------
        None.
        """
        if self.flags['autoUpdate']:
            self.flags[flag] = int(not self.flags[flag])
        but_widget.setText(
            text[self.flags['autoUpdate']][self.flags[flag]])
        # show new frame except when autoUpdate and update has been disabled:
        if not (self.flags['autoUpdate'] and not self.flags[flag]):
            self.__get_frame()
            self.__set_view(view_widget)

    def __set_view(self, widget):
        """
        Pass data to a widget.

        This method passes the current image frame data on to the (pre)view
        widget to display the data.

        Parameters
        ----------
        widget : QWidget
            The widget to receive the data through its <setData> method.

        Raises
        ------
        FrameConfigError
            Raised id the widget is not an instance of a QWidget.

        Returns
        -------
        None.
        """
        if not isinstance(widget, QtWidgets.QWidget):
            raise FrameConfigError('The reference is not a widget')
        widget.setData(self._frame)
