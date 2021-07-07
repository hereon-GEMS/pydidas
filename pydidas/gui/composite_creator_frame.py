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

"""Module with the CompositeCreatorFrame which allows to combine images to
mosaics."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CompositeCreatorFrame']

import os
from functools import partial

import numpy as np

from PyQt5 import QtWidgets, QtCore


from pydidas.gui.builders import CompositeCreatorFrameBuilder
from pydidas._exceptions import AppConfigError
from pydidas.apps import CompositeCreatorApp
from pydidas.core import (ParameterCollectionMixIn, ParameterCollection,
                          get_generic_parameter)
from pydidas.config import HDF5_EXTENSIONS
from pydidas.image_reader import read_image
from pydidas.widgets import (BaseFrameWithApp, dialogues, parameter_config)
from pydidas.utils import (get_hdf5_populated_dataset_keys,
                           get_hdf5_metadata, check_file_exists)
from pydidas.multiprocessing import AppRunner


class CompositeCreatorFrame(BaseFrameWithApp,
                            parameter_config.ParameterConfigWidgetsMixIn,
                            ParameterCollectionMixIn):
    """
    Frame with Parameter setup for the CompositeCreatorApp and result
    visualization.
    """
    CONFIG_WIDGET_WIDTH = 300

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrameWithApp.__init__(self, parent)
        parameter_config.ParameterConfigWidgetsMixIn.__init__(self)

        self._app = CompositeCreatorApp()
        self._filelist = self._app._filelist
        self._config = self._app._config
        self._app_attributes_to_update.append('_composite')
        self._runner = None
        self._create_param_collection()

        CompositeCreatorFrameBuilder(self)
        self.connect_signals()
        self.setup_initial_state()

    def _create_param_collection(self):
        """
        Create the local ParameterCollection which is an updated
        CompositeCreatorApp collection.
        """
        for param in self._app.params.values():
            self.add_param(param)
            if param.refkey == 'hdf5_key':
                self.add_param(get_generic_parameter('hdf5_dataset_shape'))
            if param.refkey == 'last_file':
                self.add_param(get_generic_parameter('raw_image_shape'))
            if param.refkey == 'file_stepping':
                self.add_param(get_generic_parameter('n_files'))

    def connect_signals(self):
        """
        Connect the required signals between widgets and methods.
        """
        self._widgets['but_clear'].clicked.connect(
            partial(self.__clear_entries, 'all', True)
            )
        self._widgets['but_exec'].clicked.connect(self._run_app)
        self._widgets['but_save'].clicked.connect(self.__save_composite)
        self._widgets['but_show'].clicked.connect(self.__show_composite)
        self._widgets['but_abort'].clicked.connect(self.__abort_comp_creation)

        for _key in ['last_file', 'file_stepping']:
            self.param_widgets[_key].io_edited.connect(
                self.__update_file_selection)
        for _key in ['hdf5_first_image_num', 'hdf5_last_image_num',
                     'hdf5_stepping']:
            self.param_widgets[_key].io_edited.connect(
                self.__update_n_image)

        self.param_widgets['use_roi'].currentTextChanged.connect(
            self.__toggle_roi_selection )
        self.param_widgets['first_file'].io_edited.connect(
            self.__selected_first_file)
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
        # disconnect the generic param update connections and re-route to
        # composite update method
        self.param_widgets['composite_nx'].io_edited.disconnect()
        self.param_widgets['composite_nx'].io_edited.connect(
            partial(self.__update_composite_dim, 'x'))
        self.param_widgets['composite_ny'].io_edited.disconnect()
        self.param_widgets['composite_ny'].io_edited.connect(
            partial(self.__update_composite_dim, 'y'))

    def setup_initial_state(self):
        """
        Setup the initial state for the widgets.
        """
        self.__toggle_roi_selection(False)
        self.__toggle_bg_file_selection(False)
        self.__toggle_threshold_selection(False)

    def frame_activated(self, index):
        """
        Overload the generic frame_activated method.

        Parameters
        ----------
        index : int
            The frame index.
        """
        ...

    def _run_app(self):
        """
        Parallel implementation of the execution method.
        """
        self.set_status('Started composite image creation.')
        self._widgets['but_exec'].setEnabled(False)
        self._widgets['but_abort'].setVisible(True)
        self._widgets['progress'].setVisible(True)
        self._widgets['progress'].setValue(0)
        self._runner = AppRunner(self._app, 8)
        self._runner.final_app_state.connect(self._set_app)
        self._runner.progress.connect(self._apprunner_update_progress)
        self._runner.finished.connect(self._apprunner_finished)
        print(self._runner._AppRunner__app._filelist._config['file_list'])
        self._runner.start()

    @QtCore.pyqtSlot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        self._widgets['but_exec'].setEnabled(True)
        self._widgets['but_show'].setEnabled(True)
        self._widgets['but_save'].setEnabled(True)
        self._widgets['but_abort'].setVisible(False)
        self._widgets['progress'].setVisible(False)
        self.set_status('Finished composite image creation.')
        self._runner = None

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
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Name of file', None,
            'TIFF (*.tif);;JPG (*.jpg);;PNG (*.png)')[0]
        self._app.export_image(fname)

    def _run_app_serial(self):
        """
        Serial implementation of the execution method.
        """
        self.set_status('Started composite image creation.')
        self._app.run()
        self._widgets['but_show'].setEnabled(True)
        self._widgets['but_save'].setEnabled(True)
        self.set_status('Finished composite image creation.')

    @QtCore.pyqtSlot(str)
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
            The filename of the first image file.
        """
        if not self.__check_file(fname):
            return
        self.__clear_entries(['hdf5_key', 'hdf5_first_image_num',
                              'hdf5_last_image_num', 'hdf5_stepping',
                              'last_file','file_stepping', 'n_total',
                              'composite_nx', 'composite_ny'])
        hdf5_flag = os.path.splitext(fname)[1] in HDF5_EXTENSIONS
        self._config['hdf5_file_flag'] = hdf5_flag
        self.__update_widgets_after_selecting_first_file()
        self.__update_file_selection()
        if hdf5_flag:
            self.__popup_select_hdf5_key(fname)
        else:
            _shape = read_image(fname).shape
            self.update_param_value('raw_image_shape', _shape)
            self.update_param_value('images_per_file', 1)
        self.__update_n_total()

    def __check_file(self, fname):
        if self.get_param_value('live_processing') or os.path.isfile(fname):
            return True
        if fname not in ['', '.']:
            dialogues.CriticalWarning(
                'File does not exist',
                f'The selected file\n\n"{fname}"\n\ndoes not exist.')
            self.__clear_entries(['first_file'], hide=False)
            self.__clear_entries(
                ['hdf5_key', 'hdf5_first_image_num',
                 'hdf5_last_image_num', 'hdf5_stepping',
                 'last_file','file_stepping', 'n_total',
                 'composite_nx', 'composite_ny'])
        return False

    def __update_widgets_after_selecting_first_file(self):
        """
        Update widget visibilty after selecting the first file based on the
        file format (hdf5 or not).
        """
        hdf5_flag = self._config['hdf5_file_flag']
        for _key in ['hdf5_key', 'hdf5_first_image_num',
                     'hdf5_last_image_num', 'hdf5_stepping',
                     'hdf5_dataset_shape']:
            self.toggle_widget_visibility(_key, hdf5_flag)
        self.toggle_widget_visibility('last_file', True)
        self.toggle_widget_visibility('raw_image_shape', not hdf5_flag)

    def __popup_select_hdf5_key(self, fname):
        """
        Create a popup window which asks the user to select a dataset.

        Parameters
        ----------
        fname : str
            The filename to the hdf5 data file.
        """
        dset = dialogues.Hdf5DatasetSelectionPopup(self, fname).get_dset()
        if dset is not None:
            self.update_param_value('hdf5_key', dset)
            self._app.set_param_value('hdf5_key', dset)
            self.__selected_hdf5_key()
        else:
            self.__clear_entries(['images_per_file', 'n_total',
                                  'hdf5_dataset_shape', 'hdf5_key',
                                  'hdf5_first_image_num',
                                  'hdf5_last_image_num', 'hdf5_stepping',],
                                 False)


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
            dialogues.CriticalWarning(
                'Dataset key error',
                (f'The selected file\n\n"{filename}"\n\ndoes not have the '
                 f'selected dataset\n\n"{dset}"'))
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
            self._app._store_image_data_from_hdf5_file()
            _n_total = (self.get_param_value('images_per_file')
                        * self._filelist.n_files)
            self.update_param_value('n_total', _n_total)
            self.update_param_value('hdf5_dataset_shape', _shape)
            self.__update_n_image()
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
            self._config['hdf5_file_flag'] = None

    def __check_exec_enable(self):
        """
        Check whether the exec button should be enabled and enable/disable it.
        """
        try:
            assert self._config['hdf5_file_flag'] is not None
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


    def __abort_comp_creation(self):
        """
        Abort the creation of the composite image.
        """
        self._runner.stop()
        self._apprunner_finished()


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
        for _key in ['hdf5_key', 'hdf5_first_image_num', 'hdf5_last_image_num',
                     'first_file', 'last_file', 'hdf5_first_image_num',
                     'hdf5_last_image_num','bg_hdf5_key', 'bg_hdf5_num',
                     'bg_file']:
            if _key in keys:
                self.toggle_widget_visibility(_key, not hide)
        self.__reset_hdf5_images_key(keys)
        self.__check_exec_enable()


    def __update_n_image(self):
        """
        Update the number of images in the composite upon changing any
        input parameter.
        """
        if self._config['hdf5_file_flag'] is True:
            self._app._store_image_data_from_hdf5_file()
        if self._config['hdf5_file_flag'] is not None:
            _n_per_file = self.get_param_value('images_per_file')
            self.param_widgets['images_per_file'].set_value(_n_per_file)
            _n_total = (_n_per_file * self._filelist.n_files)
            self.update_param_value('n_total', _n_total)
            self.__update_composite_dim(self.get_param_value('composite_dir'))

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
        if ((num1 - 1) * num2 >= _n_total
                or num1 * (num2 - 1) >= _n_total):
            self.__update_composite_dim(dim2)

    def __update_file_selection(self):
        """
        Update the filelist based on the current selection.
        """
        print('update file selection')
        try:
            self._filelist.update()
        except AppConfigError as _ex:
            self.__clear_entries(['last_file'], hide=False)
            QtWidgets.QMessageBox.critical(self, 'Could not create filelist.',
                                           str(_ex))
            return
        if not self._filelist.n_files > 0:
            QtWidgets.QMessageBox.critical(self, 'Filelist is empty.',
                                           'The list of fils is empty. Please'
                                           ' verify the selection.')
            return
        self.update_param_value('n_files', self._filelist.n_files)
        self.__update_n_total()
        self.__finalize_selection()

    def __update_n_total(self):
        """
        Update the total number of selected images.
        """
        _n_total = (self.get_param_value('images_per_file') *
                    self._filelist.n_files)
        self.update_param_value('n_total', _n_total)
        self.__update_composite_dim(self.get_param_value('composite_dir'))

    def __finalize_selection(self):
        """
        Finalize input file selection.
        """
        for _key in ['file_stepping', 'composite_nx', 'composite_ny']:
            self.toggle_widget_visibility(_key, True)
        self._widgets['but_exec'].setEnabled(True)


if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
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
