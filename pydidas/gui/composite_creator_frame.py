# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the CompositeCreatorFrame which allows to combine images to
mosaics."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeCreatorFrame']

import os
from functools import partial

import numpy as np

from PyQt5 import QtWidgets, QtCore

from silx.gui.plot import PlotWindow
# from silx.gui.plot.ImageView import ImageView

from pydidas._exceptions import AppConfigError
from pydidas.apps import CompositeCreatorApp
from pydidas.core import ParameterCollectionMixIn
from pydidas.config import HDF5_EXTENSIONS
from pydidas.widgets import (
    ReadOnlyTextWidget, ScrollArea, CreateWidgetsMixIn,
    create_default_grid_layout, BaseFrame, dialogues, param_config)
from pydidas.utils import (get_hdf5_populated_dataset_keys,
                           get_hdf5_metadata)
from pydidas.multiprocessing import AppRunner


class CompositeCreatorFrame(BaseFrame, param_config.ParameterConfigMixIn,
                            ParameterCollectionMixIn, CreateWidgetsMixIn):
    """
    Frame with Parameter setup for the CompositeCreatorApp and result
    visualization.
    """
    CONFIG_WIDGET_WIDTH = 300

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        param_config.ParameterConfigMixIn.__init__(self)

        self._app = CompositeCreatorApp()
        self.params = self._app.params
        self._config = self._app._config
        self._config.update({'hdf5_image_flag': None,
                             'composite_dim': 'x',
                             'n_images_hdf5': 1,
                             'hdf5_dset_shape': None})
        self._widgets = {}
        self._runner = None
        self.init_widgets()
        self.connect_signals()

    def init_widgets(self):
        """
        Create all widgets and initialize their state.
        """
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.w_buttons = {}

        self._widgets['config'] = param_config.ParamConfig(
            self, initLayout=False, midLineWidth=5)
        self._widgets['config'].setLayout(create_default_grid_layout())
        _config_next_row = self._widgets['config'].next_row

        self._widgets['config_area'] = ScrollArea(
            self, widget=self._widgets['config'],
            fixedWidth=self.CONFIG_WIDGET_WIDTH + 55,
            sizePolicy= (QtWidgets.QSizePolicy.Fixed,
                         QtWidgets.QSizePolicy.Expanding))
        self.layout().addWidget(self._widgets['config_area'], self.next_row(),
                                0, 1, 1)

        self.create_label(
            'Composite image creator', fontsize=14, gridPos=(0, 0, 1, 2),
            parent_widget=self._widgets['config'],
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.create_spacer(gridPos=(_config_next_row(), 0, 1, 2),
                            parent_widget=self._widgets['config'])

        self._widgets['but_clear'] = self.create_button(
            'Clear all entries', gridPos=(_config_next_row(), 0, 1, 2),
            parent_widget=self._widgets['config'],
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self._widgets['selection_info'] = ReadOnlyTextWidget(
            fixedWidth=self.CONFIG_WIDGET_WIDTH, fixedHeight=60, visible=False)

        self._widgets['plot_window']= PlotWindow(
            parent=self, resetzoom=True, autoScale=False, logScale=False,
            grid=False, curveStyle=False, colormap=True, aspectRatio=True,
            yInverted=True, copy=True, save=True, print_=True, control=False,
            position=False, roi=False, mask=True)
        self.layout().addWidget(self._widgets['plot_window'], 0, 3,
                                self.next_row() -1, 1)
        self._widgets['plot_window'].setVisible(False)

        for _key in self.params:
            # special formatting for some parameters:
            if _key in ['first_file', 'last_file', 'hdf5_key', 'bg_file',
                        'bg_hdf5_key', 'output_fname']:
                _options = dict(linebreak=True, n_columns=2, n_columns_text=2,
                                halign_text=QtCore.Qt.AlignLeft,
                                valign_text=QtCore.Qt.AlignBottom,
                                width=self.CONFIG_WIDGET_WIDTH,
                                width_text=self.CONFIG_WIDGET_WIDTH - 50,
                                parent_widget=self._widgets['config'],
                                row=_config_next_row())
            else:
                _options = dict(width=100, row=_config_next_row(),
                                parent_widget=self._widgets['config'],
                                width_text=self.CONFIG_WIDGET_WIDTH - 110)
            self.create_param_widget(self.params[_key], **_options)

            # add selection info box after hdf5_key widgets:
            if _key == 'hdf5_key':
                self._widgets['config'].layout().addWidget(
                    self._widgets['selection_info'], _config_next_row(),
                    0, 1, 2)

            # add spacers between groups:
            if _key in ['hdf5_stepping', 'bg_hdf5_num', 'composite_dir',
                        'roi_yhigh', 'threshold_high', 'binning',
                        'output_fname']:
                self.create_line(parent_widget=self._widgets['config'],
                                 fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.param_widgets['output_fname'].modify_file_selection(
            ['NPY files (*.npy *.npz)'])

        self._widgets['but_exec'] = self.create_button(
            'Generate composite', parent_widget=self._widgets['config'],
            gridPos=(_config_next_row(), 0, 1, 2), enabled=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self._widgets['progress'] = self.create_progress_bar(
            parent_widget=self._widgets['config'],
            gridPos=(_config_next_row(), 0, 1, 2), visible=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH, minimum=0, maximum=100)

        self._widgets['but_show'] = self.create_button(
            'Show composite', parent_widget=self._widgets['config'],
            gridPos=(_config_next_row(), 0, 1, 2), enabled=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self._widgets['but_save'] = self.create_button(
            'Save composite image', parent_widget=self._widgets['config'],
            gridPos=(_config_next_row(), 0, 1, 2), enabled=False,
            fixedWidth=self.CONFIG_WIDGET_WIDTH)

        self.create_spacer(parent_widget=self._widgets['config'],
                            gridPos=(_config_next_row(), 0, 1, 2),
                            policy = QtWidgets.QSizePolicy.Expanding)

        self.param_widgets['n_total'].setEnabled(False)
        for _key in ['hdf5_key', 'hdf5_first_image_num', 'hdf5_last_image_num',
                     'last_file','hdf5_stepping']:
            self.toggle_widget_visibility(_key, False)
        self.__toggle_roi_selection(False)
        self.__toggle_bg_file_selection(False)
        self.__toggle_threshold_selection(False)

    def connect_signals(self):
        """
        Connect the required signals between widgets and methods.
        """
        self._widgets['but_clear'].clicked.connect(
            partial(self.__clear_entries, 'all', True)
            )
        self._widgets['but_exec'].clicked.connect(self.__run_app)
        self._widgets['but_save'].clicked.connect(self.__save_composite)
        self._widgets['but_show'].clicked.connect(self.__show_composite)

        self.param_widgets['use_roi'].currentTextChanged.connect(
            self.__toggle_roi_selection )
        self.param_widgets['first_file'].io_edited.connect(
            self.__selected_first_file)
        self.param_widgets['last_file'].io_edited.connect(
            self.__selected_last_file)
        self.param_widgets['hdf5_key'].io_edited.connect(
            self.__selected_hdf5_key)
        self.param_widgets['use_bg_file'].io_edited.connect(
            self.__toggle_bg_file_selection)
        self.param_widgets['bg_file'].io_edited.connect(
            self.__selected_bg_file)
        self.param_widgets['bg_hdf5_key'].io_edited.connect(
            self.__selected_bg_hdf5_key)
        self.param_widgets['use_thresholds'].currentTextChanged.connect(
            self.__toggle_threshold_selection)
        self.param_widgets['file_stepping'].io_edited.connect(
            self.__update_file_stepping)
        for _key in ['hdf5_first_image_num', 'hdf5_last_image_num',
                     'hdf5_stepping']:
            self.param_widgets[_key].io_edited.connect(
                self.__update_n_image)
        # disconnect the generic param update connections and re-route to
        # composite update method
        self.param_widgets['composite_nx'].io_edited.disconnect()
        self.param_widgets['composite_nx'].io_edited.connect(
            partial(self.__update_composite_dim, 'x'))
        self.param_widgets['composite_ny'].io_edited.disconnect()
        self.param_widgets['composite_ny'].io_edited.connect(
            partial(self.__update_composite_dim, 'y'))

    def _set_app_param(self, param_key, value):
        """
        Update the Application Parameter.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.
        value : object
            The new Parameter value. This can by any datatype, depending on
            the Parameter datatype.
        """
        print('App: ', param_key, value)
        self._app.set_param_value(param_key, value)

    # def _sync_params_from_frame(self):
    #     self._app.params = self.params.get_copy
    #     _val = self.get_param_value(param_key)
    #     self._app.set_param_value(param_key, _val)

    def frame_activated(self, index):
        """
        Overload the generic frame_activated method.

        Parameters
        ----------
        index : int
            The frame index.
        """
        ...

    def __run_app(self):
        """
        Parallel implementation of the execution method.
        """
        self.set_status('Started composite image creation.')
        self._widgets['but_exec'].setEnabled(False)
        self._widgets['progress'].setVisible(True)
        self._widgets['progress'].setValue(0)
        self._app = CompositeCreatorApp(self.params.get_copy())
        self._runner = AppRunner(self._app, 8)
        self._runner.final_app_state.connect(self._set_app)
        self._runner.progress.connect(self._apprunner_update_progress)
        self._runner.finished.connect(self._apprunner_finished)
        self._runner.start()

    @QtCore.pyqtSlot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        self._widgets['but_exec'].setEnabled(True)
        self._widgets['but_show'].setEnabled(True)
        self._widgets['but_save'].setEnabled(True)
        self.set_status('Finished composite image creation.')
        del self._runner

    def __show_composite(self):
        """
        Show the composite image in the Viewwer.
        """
        self._widgets['plot_window'].setVisible(True)
        self._widgets['plot_window'].addImage(self._app.composite,
                                              replace=True)

    def __save_composite(self):
        """
        Save the composite image.
        """
        _func = QtWidgets.QFileDialog.getSaveFileName
        fname = _func(self, 'Name of file', None,
                      'TIFF (*.tif);;JPG (*.jpg);;PNG (*.png)')[0]
        self._app.export_image(fname)

    def __run_app_serial(self):
        """
        Serial implementation of the execution method.
        """
        self.set_status('Started composite image creation.')
        self._app = CompositeCreatorApp(self.params.get_copy())
        self._app.run()
        self._widgets['but_show'].setEnabled(True)
        self._widgets['but_save'].setEnabled(True)
        self.set_status('Finished composite image creation.')

    def __selected_first_file(self, fname):
        """
        Perform required actions after selecting the first image file.

        This method checks whether a hdf5 file has been selected and shows/
        hides the required fields for selecting the dataset or the last file
        in case of a file series.
        If an hdf5 image file has been selected, this method also opens a
        pop-up for dataset selection.

        Parameters
        ----------
        fname : str
            The filename of the background image file.
        """
        self.__clear_entries(['hdf5_key', 'hdf5_first_image_num',
                              'hdf5_last_image_num', 'hdf5_stepping',
                              'last_file','file_stepping', 'n_total',
                              'composite_nx', 'composite_ny'])
        hdf5_flag = os.path.splitext(fname)[1] in HDF5_EXTENSIONS
        self._config['hdf5_image_flag'] = hdf5_flag
        self._app._create_filelist()
        for _key in ['hdf5_key', 'hdf5_first_image_num',
                     'hdf5_last_image_num', 'hdf5_stepping']:
            self.toggle_widget_visibility(_key, hdf5_flag)
        self.toggle_widget_visibility('last_file', True)

        if hdf5_flag:
            dset = dialogues.Hdf5DatasetSelectionPopup(self, fname).get_dset()
            if dset is not None:
                self.update_param_value('hdf5_key', dset)
                self._app.set_param_value('hdf5_key', dset)
                self.__selected_hdf5_key()

    def __selected_last_file(self):
        """
        Perform checks after selecting the last file for a file series.
        """
        # self._sync_param_from_file('last_file')
        try:
            self._app._CompositeCreatorApp__check_files()
        except AppConfigError as _ex:
            self.__clear_entries(['last_file'], hide=False)
            QtWidgets.QMessageBox.critical(self, 'Files wrong size.', str(_ex))
            return
        self.__update_n_image()
        self.__finalize_selection()

    def __selected_bg_file(self, fname):
        """
        Perform required actions after selecting background image file.

        This method resets the fields for hdf5 image key and image number
        and opens a pop-up for dataset selection if an hdf5 file has been
        selected.

        Parameters
        ----------
        fname : str
            The filename of the background image file.
        """
        self.__clear_entries(['bg_hdf5_key', 'bg_hdf5_num'])
        hdf5_flag = os.path.splitext(fname)[1] in HDF5_EXTENSIONS
        self._config['bg_hdf5_images'] = hdf5_flag
        if hdf5_flag:
            dset = dialogues.Hdf5DatasetSelectionPopup(self, fname).get_dset()
            self.update_param_value('bg_hdf5_key', dset)
        self.toggle_widget_visibility('bg_hdf5_key', hdf5_flag)
        self.toggle_widget_visibility('bg_hdf5_num', hdf5_flag)
        self.__check_exec_enable()

    def __verify_hdf5_key(self, filename, dset, param_key):
        """
        Verify that the hdf5 file has the selected dataset.

        Parameters
        ----------
        filename : str
            The filename to the hdf5 file.
        dset : str
            The dateset.
        param_key : str
            The reference key for the hdf dataset Parameter to be reset if
            the selection is invalid.

        Returns
        -------
        bool
            The result of the hdf key check. True if the dataset exists in the
            file and False if not.
        """
        dsets = get_hdf5_populated_dataset_keys(filename)
        if dset not in dsets:
            self.__clear_entries([param_key], hide=False)
            QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Dataset key error',
                (f'The selected file\n\n"{filename}"\n\ndoes not have the '
                 f'selected dataset\n\n"{dset}"')
            ).exec_()
            return False
        return True

    def __selected_hdf5_key(self):
        """
        Perform required actions after an hdf5 key has been selected.
        """
        _fname = self.get_param_value('first_file')
        _dset = self.get_param_value('hdf5_key')
        _dset_ok = self.__verify_hdf5_key(_fname, _dset, 'hdf5_key')
        if _dset_ok:
            _shape = get_hdf5_metadata(_fname, 'shape', _dset)
            self._config['hfd5_dset_shape'] = _shape
            self._app._store_image_data_from_hdf5_file()
            _n_total = (self._config['n_image_per_file']
                        * self._config['n_files'])
            self.update_param_value('n_total', _n_total)
            self._widgets['selection_info'].setText(
                (f'Number of images in dataset: {_shape[0]}\n\nImage size: '
                 f'{_shape[1]} x {_shape[2]}'))
            self.__finalize_selection()
        else:
            self._widgets['but_exec'].setEnabled(False)

    def __selected_bg_hdf5_key(self):
        """
        Check that the background image hdf5 file actually has the required
        key.
        """
        _fname = self.get_param_value('bg_file')
        _dset = self.get_param_value('bg_hdf5_key')
        if not self.__verify_hdf5_key(_fname, _dset, 'bg_hdf5_key'):
            self._widgets['but_exec'].setEnabled(False)

    def __finalize_selection(self):
        """
        Finalize input file selection.
        """
        self._widgets['selection_info'].setVisible(True)
        for _key in ['file_stepping', 'composite_nx', 'composite_ny']:
            self.toggle_widget_visibility(_key, True)
        self._widgets['but_exec'].setEnabled(True)

    def __reset_params(self, keys='all'):
        """
        Reset parameters to their default values.

        Parameters
        ----------
        keys : Union['all', iterable], optional
            An iterable of keys which reference the Parameters. If 'all',
            all Parameters in the ParameterCollection will be reset to their
            default values. The default is 'all'.
        """
        for _but in ['but_exec', 'but_save', 'but_show']:
            self._widgets[_but].setEnabled(False)
        self._widgets['progress'].setVisible(False)
        self._widgets['plot_window'].setVisible(False)
        for _key in keys:
            param = self.params[_key]
            param.restore_default()
            self.param_widgets[_key].set_value(param.default)

    def __reset_hdf5_images_key(self, keys):
        """
        Reset the selection info key "hdf5_images" if checks fails.

        Parameters
        ----------
        keys : list
            A list with keys which have been reset.
        """
        _check_keys = ['hdf5_key', 'hdf5_first_image_num',
                       'hdf5_last_image_num', 'last_file']
        if any(_key in keys for _key in _check_keys):
            self._config['hdf5_image_flag'] = None

    def __check_exec_enable(self):
        """
        Check whether the exec button should be enabled and enable/disable it.
        """
        try:
            assert self._config['hdf5_image_flag'] is not None
            if self.get_param_value('use_bg_file'):
                assert os.path.isfile(self.get_param_value('bg_file'))
            _enable = True
        except (KeyError, AssertionError):
            _enable = False
        finally:
            self._widgets['but_exec'].setEnabled(_enable)

    def __toggle_bg_file_selection(self, flag):
        """
        Show or hide the detail for background image files.

        Parameters
        ----------
        flag : bool
            The show / hide boolean flag.
        """
        if isinstance(flag, str):
            flag = flag == 'True'
        self.set_param_value('use_bg_file', flag)
        self.toggle_widget_visibility('bg_file', flag)
        _bg_ext = os.path.splitext(self.get_param_value('bg_file'))[1]
        if not _bg_ext in HDF5_EXTENSIONS:
            flag = False
        self.toggle_widget_visibility('bg_hdf5_key', flag)
        self.toggle_widget_visibility('bg_hdf5_num', flag)
        self.__check_exec_enable()

    def __toggle_selection_infobox_visibility(self, reset_keys):
        """
        Show or hide the infobox according to keys which have been reset.

        Parameters
        ----------
        reset_keys : Union[list, tuple]
            The keys which have been reset.
        """
        _check_keys = ['hdf5_key', 'hdf5_first_image_num', 'hdf5_last_image_num',
                       'last_file']
        _should_show_box = not any(_key in reset_keys for _key in _check_keys)
        self._widgets['selection_info'].setVisible(_should_show_box)

    def __toggle_roi_selection(self, flag):
        """
        Show or hide the ROI selection.

        Parameters
        ----------
        flag : bool
            The flag with visibility information for the ROI selection.
        """
        if isinstance(flag, str):
            flag = flag == 'True'
        self.set_param_value('use_roi', flag)
        for _key in ['roi_xlow', 'roi_xhigh', 'roi_ylow', 'roi_yhigh']:
            self.toggle_widget_visibility(_key, flag)

    def __toggle_threshold_selection(self, flag):
        """
        Show or hide the threshold selection.

        Parameters
        ----------
        flag : bool
            The flaf with visibility information for the threshold selection.
        """
        if isinstance(flag, str):
            flag = flag == 'True'
        self.set_param_value('use_thresholds', flag)
        for _key in ['threshold_low', 'threshold_high']:
            self.toggle_widget_visibility(_key, flag)

    def __clear_entries(self, keys='all', hide=True):
        """
        Clear the Parameter entries and reset to default for selected keys.

        Parameters
        ----------
        keys : Union['all', list, tuple], optional
            The keys for the Parameters to be reset. The default is 'all'.
        hide : bool, optional
            Flag for hiding the reset keys. The default is True.
        """
        keys = keys if keys != 'all' else list(self.params.keys())
        self.__reset_params(keys)
        self.__toggle_selection_infobox_visibility(keys)
        for _key in ['hdf5_key', 'hdf5_first_image_num', 'hdf5_last_image_num',
                     'last_file', 'hdf5_first_image_num', 'hdf5_last_image_num',
                     'bg_hdf5_key', 'bg_hdf5_num', 'bg_file']:
            if _key in keys:
                self.toggle_widget_visibility(_key, not hide)
        self.__reset_hdf5_images_key(keys)
        self.__check_exec_enable()

    def __update_file_stepping(self):
        self._app._create_filelist()
        self.__update_n_image()

    def __update_n_image(self):
        """
        Update the number of images in the composite upon changing any
        input parameter.
        """
        if self._config['hdf5_image_flag'] is True:
            self._app._store_image_data_from_hdf5_file()
        _n_total = (self._config['n_image_per_file'] *
                    self._config['n_files'])
        if self._config['hdf5_image_flag'] is not None:
            self.update_param_value('n_total', _n_total)
            self.__update_composite_dim(self._config['composite_dim'])

    def __update_composite_dim(self, dim):
        """
        Update the composite dimension counters upon a change in one of them.

        Parameters
        ----------
        dim : Union['x', 'y']
            The dimension which has changed.
        """
        _n_total = self.get_param_value('n_total')
        num1 = self.param_widgets[f'composite_n{dim}'].get_value()
        num2 = int(np.ceil(_n_total / abs(num1)))
        dim2 = 'y' if dim == 'x' else 'x'
        self.update_param_value(f'composite_n{dim2}', num2)
        self.update_param_value(f'composite_n{dim}', abs(num1))
        self._config['composite_dim'] = dim
        if ((num1 - 1) * num2 >= _n_total
                or num1 * (num2 - 1) >= _n_total):
            self.__update_composite_dim(dim2)


if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.config.STANDARD_FONT_SIZE

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'),
                       CompositeCreatorFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()
