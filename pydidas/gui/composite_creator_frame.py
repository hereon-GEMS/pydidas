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
import matplotlib.image as mplimg
from PyQt5 import QtWidgets, QtCore

from silx.gui.plot import PlotWindow
# from silx.gui.plot.ImageView import ImageView

from pydidas.apps import CompositeCreatorApp
from pydidas.core import ParameterCollectionMixIn
from pydidas.config import HDF5_EXTENSIONS
from pydidas.widgets import (
    ReadOnlyTextWidget, ScrollArea, CreateWidgetsMixIn,
    create_default_grid_layout, BaseFrame)
from pydidas.widgets.dialogues import Hdf5DatasetSelectionPopup
from pydidas.widgets.param_config import ParameterConfigMixIn, ParamConfig
from pydidas.utils import (get_hdf5_populated_dataset_keys,
                           get_hdf5_metadata)
from pydidas.multiprocessing import AppRunner


class CompositeCreatorFrame(BaseFrame, ParameterConfigMixIn,
                            ParameterCollectionMixIn, CreateWidgetsMixIn):
    """
    Frame with Parameter setup for the CompositeCreatorApp and result
    visualization.
    """
    CONFIG_WIDGET_WIDTH = 300

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        ParameterConfigMixIn.__init__(self)
        self.params = CompositeCreatorApp.get_default_params_copy()
        self.__select_info = {'hdf_images': None,
                              'composite_dim': 'x'}
        self._app = None
        self._widgets = {}
        self.init_widgets()
        self.connect_signals()

    def init_widgets(self):
        """
        Create all widgets and initialize their state.
        """
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.w_buttons = {}

        self._widgets['config'] = ParamConfig(self, initLayout=False,
                                              lineWidth=0, frameStyle=0,
                                              midLineWidth=5)
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

        for _key in self.params:
            # special formatting for some parameters:
            if _key in ['first_file', 'last_file', 'hdf_key', 'bg_file',
                        'bg_hdf_key', 'output_fname']:
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

            # add selection info box after hdf_key widgets:
            if _key == 'hdf_key':
                self._widgets['config'].layout().addWidget(
                    self._widgets['selection_info'], _config_next_row(),
                    0, 1, 2)

            # add spacers between groups:
            if _key in ['hdf_last_image_num', 'bg_hdf_num', 'composite_dir',
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

        self.param_widgets['n_image'].setEnabled(False)
        for _key in ['hdf_key', 'hdf_first_image_num', 'hdf_last_image_num',
                     'last_file', 'hdf_first_image_num', 'hdf_last_image_num',
                     'stepping']:
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
        self.param_widgets['hdf_key'].io_edited.connect(
            self.__selected_hdf_key)
        self.param_widgets['use_thresholds'].currentTextChanged.connect(
            self.__toggle_threshold_selection)
        for _key in ['hdf_first_image_num', 'hdf_last_image_num', 'stepping']:
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
        self.param_widgets['use_bg_file'].io_edited.connect(
            self.__toggle_bg_file_selection)
        self.param_widgets['bg_file'].io_edited.connect(
            self.__selected_bg_file)
        self.param_widgets['bg_hdf_key'].io_edited.connect(
            self.__selected_bg_hdf_key)

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
        self._runner = AppRunner(self._app)
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
        self._widgets['plot_window'].addImage(self._app.composite,
                                              replace=True)

    def __save_composite(self):
        """
        Save the composite image.
        """
        _func = QtWidgets.QFileDialog.getSaveFileName
        fname = _func(self, 'Name of file', None,
                      'TIFF (*.tif);;JPG (*.jpg);;PNG (*.png)')[0]
        mplimg.imsave(fname, self._app.composite)

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
        self.__clear_entries(['hdf_key', 'hdf_first_image_num',
                              'hdf_last_image_num', 'last_file', 'stepping',
                              'n_image', 'composite_nx', 'composite_ny'])
        hdf_flag = os.path.splitext(fname)[1] in HDF5_EXTENSIONS
        for _key in ['hdf_key', 'hdf_first_image_num', 'hdf_last_image_num']:
            self.toggle_widget_visibility(_key, hdf_flag)
        self.toggle_widget_visibility('last_file', not hdf_flag)
        self.__select_info['hdf_images'] = hdf_flag
        if hdf_flag:
            dset = Hdf5DatasetSelectionPopup(self, fname).get_dset()
            self.update_param_value('hdf_key', dset)
            self.__selected_hdf_key()

    def __selected_last_file(self):
        """
        Perform checks after selecting the last file for a file series.
        """
        _path1, _fname1 = os.path.split(self.params['first_file'].value)
        _path2, _fname2 = os.path.split(self.params['last_file'].value)
        # verify both files are in the same path:
        if _path1 != _path2:
            QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Files not in same directory',
                (f'The selected files\n\t{_fname1}\n\nand\n\t{_fname2}'
                 f'\n\nAre not in the same path:\n\n\tpath I:  {_path1}'
                 f'\n\n\tpath II: {_path2}')
            ).exec_()
            self.__clear_entries(['last_file'], hide=False)
            return
        # get the list of all the files included in the selection:
        _flist = sorted(os.listdir(_path1))
        index1 = _flist.index(_fname1)
        index2 = _flist.index(_fname2)
        _flist = _flist[index1 : index2 + 1]
        # check that all selected files are of the same size:
        _fsizes = np.r_[[os.stat(f'{_path1}/{f}').st_size for f in _flist]]
        if _fsizes.std() > 0.:
            QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Files not of same size',
                (f'The selected files\n\n\t{_fname1}\n\nto\n\t{_fname2}'
                 f'\n\nare not all of the same size. Please verify the'
                 ' selection.')
            ).exec_()
            self.__clear_entries(['last_file'], hide=False)
            return
        # finally, give information about number of selected files
        self._widgets['selection_info'].setText(
            (f'Selected directory:\n  [...]/{os.path.basename(_path1)}\n'
             f'Total number of selected files: {index2 - index1 + 1}'))
        self.update_param_value('n_image', index2 - index1 + 1)
        self.__select_info['file_n_image'] = index2 - index1 + 1
        self.__select_info['file_list'] = _flist
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
        self.__clear_entries(['bg_hdf_key', 'bg_hdf_num'])
        hdf_flag = os.path.splitext(fname)[1] in HDF5_EXTENSIONS
        self.__select_info['bg_hdf_images'] = hdf_flag
        if hdf_flag:
            dset = Hdf5DatasetSelectionPopup(self, fname).get_dset()
            self.update_param_value('bg_hdf_key', dset)

    def __verify_hdf_key(self, filename, dset, param_key):
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

    def __selected_hdf_key(self):
        """
        Perform required actions after an hdf5 key has been selected.
        """
        _fname = self.get_param_value('first_file')
        _dset = self.get_param_value('hdf_key')
        if self.__verify_hdf_key(_fname, _dset, 'hdf_key'):
            _shape = get_hdf5_metadata(_fname, 'shape', _dset)
            self._widgets['selection_info'].setText(
                (f'Number of images in dataset: {_shape[0]}\n\nImage size: '
                 f'{_shape[1]} x {_shape[2]}'))
            self.update_param_value('n_image', _shape[0])
            self.__select_info['hdf_n_image'] = _shape[0]
            self.__finalize_selection()
        else:
            self._widgets['but_exec'].setEnabled(False)

    def __selected_bg_hdf_key(self):
        """
        Check that the background image hdf5 file actually has the required
        key.
        """
        _fname = self.get_param_value('bg_file')
        _dset = self.get_param_value('bg_hdf_key')
        if not self.__verify_hdf_key(_fname, _dset, 'bg_hdf_key'):
            self._widgets['but_exec'].setEnabled(False)

    def __finalize_selection(self):
        """
        Finalize input file selection.
        """
        self._widgets['selection_info'].setVisible(True)
        for _key in ['stepping', 'composite_nx', 'composite_ny']:
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
        for _key in keys:
            param = self.params[_key]
            param.restore_default()
            self.param_widgets[_key].set_value(param.default)

    def __reset_hdf_images_key(self, keys):
        """
        Reset the selection info key "hdf_images" if checks fails.

        Parameters
        ----------
        keys : list
            A list with keys which have been reset.
        """
        _check_keys = ['hdf_key', 'hdf_first_image_num', 'hdf_last_image_num',
                       'last_file']
        if any(_key in keys for _key in _check_keys):
            self.__select_info['hdf_images'] = None

    def __check_exec_enable(self):
        """
        Check whether the exec button should be enabled and enable/disable it.
        """
        try:
            assert self.__select_info['hdffile'] is not None
            if self.get_param_value('use_bg_file'):
                assert os.path.exists(self.get_param_value('bg_file'))
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
        self.toggle_widget_visibility('bg_hdf_key', flag)
        self.toggle_widget_visibility('bg_hdf_num', flag)
        self.__check_exec_enable()

    def __toggle_selection_infobox_visibility(self, reset_keys):
        """
        Show or hide the infobox according to keys which have been reset.

        Parameters
        ----------
        reset_keys : Union[list, tuple]
            The keys which have been reset.
        """
        _check_keys = ['hdf_key', 'hdf_first_image_num', 'hdf_last_image_num',
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
        for _key in ['hdf_key', 'hdf_first_image_num', 'hdf_last_image_num',
                     'last_file', 'hdf_first_image_num', 'hdf_last_image_num',
                     'bg_hdf_key', 'bg_hdf_num', 'bg_file']:
            if _key in keys:
                self.toggle_widget_visibility(_key, not hide)
        self.__reset_hdf_images_key(keys)
        self.__check_exec_enable()

    def __update_n_image(self):
        """
        Update the number of images in the composite upon changing any
        input parameter.
        """
        step = self.get_param_value('stepping')
        if self.__select_info['hdf_images'] is True:
            img1 = self.get_param_value('hdf_first_image_num')
            img2 = self.get_param_value('hdf_last_image_num')
            if img2 == -1:
                img2 = self.__select_info['hdf_n_image']
            _n = len(range(img1, img2, step))
        elif self.__select_info['hdf_images'] is False:
            _n = len(range(0, self.__select_info['file_n_image'], step))
        if self.__select_info['hdf_images'] is not None:
            self.update_param_value('n_image', _n)
            self.__update_composite_dim(self.__select_info['composite_dim'])

    def __update_composite_dim(self, dim):
        """
        Update the composite dimension counters upon a change in one of them.

        Parameters
        ----------
        dim : Union['x', 'y']
            The dimension which has changed.
        """
        _n_total = self.get_param_value('n_image')
        num1 = self.param_widgets[f'composite_n{dim}'].get_value()
        num2 = int(np.ceil(_n_total / abs(num1)))
        dim2 = 'y' if dim == 'x' else 'x'
        self.update_param_value(f'composite_n{dim2}', num2)
        self.update_param_value(f'composite_n{dim}', abs(num1))
        self.__select_info['composite_dim'] = dim
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
