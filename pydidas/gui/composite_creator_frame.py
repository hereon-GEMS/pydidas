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
from pathlib import Path
from functools import partial

import qtawesome as qta
import numpy as np
from PyQt5 import QtWidgets, QtCore

# from silx.gui.plot.ImageView import ImageView

from pydidas.gui.toplevel_frame import ToplevelFrame
from pydidas.core import Parameter, HdfKey
from pydidas.config import HDF5_EXTENSIONS
from pydidas.widgets import ReadOnlyTextWidget
from pydidas.widgets.dialogues import Hdf5DatasetSelection
from pydidas.widgets.param_config import ParamConfigMixIn
from pydidas.utils import (get_hdf5_populated_dataset_keys,
                           get_hdf5_dataset_shape)


_params = {
    'first_file': Parameter('First file name', Path, default=Path(), refkey='first_file'),
    'last_file': Parameter('Last file name', Path, default=Path(), refkey='last_file'),
    'hdf_key': Parameter('Hdf image key (dataset)', HdfKey, default=HdfKey(''), refkey='hdf_key'),
    'hdf_first_no': Parameter('First image number', int, default=0, refkey='hdf_first_no'),
    'hdf_last_no': Parameter('Last image number', int, default=-1, refkey='hdf_last_no'),
    'stepping': Parameter('Stepping', int, default=1, refkey='stepping'),
    'n_image': Parameter('Total number of images', int, default=-1, refkey='n_image'),
    'composite_nx': Parameter('Number of images in x', int, default=1, refkey='composite_nx'),
    'composite_ny': Parameter('Number of images in y', int, default=-1, refkey='composite_ny'),
    #'flag_roi': Parameter('Use ROI', str, default='False', refkey='flag_roi', choices=['True', 'False']),
    'flag_roi': Parameter('Use ROI', int, default=False, refkey='flag_roi', choices=[True, False]),
    'roi_xlow': Parameter('ROI lower x limit', int, default=0, refkey='roi_xlow'),
    'roi_xhigh': Parameter('ROI upper x limit', int, default=-1, refkey='roi_xhigh'),
    'roi_ylow': Parameter('ROI lower y limit', int, default=0, refkey='roi_ylow'),
    'roi_yhigh': Parameter('ROI upper y limit', int, default=-1, refkey='roi_yhigh'),
    'rebin': Parameter('Rebinning factor', int, default=1, refkey='rebin'),
    }


class CompositeCreatorFrame(ToplevelFrame, ParamConfigMixIn):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)
        self.params = _params
        self.__select_info = {'hdf_images': None}

        self.init_widgets()
        self.connect_signals()

    def init_widgets(self):
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(5)

        self.add_label('Composite image creator', fontsize=14,
                       gridPos=(0, 0, 1, 5))
        self.add_spacer(height=20, gridPos=(self.next_row(), 0, 1, 2))
        self.b_clear = self.add_button('Clear all entries',
                                       gridPos=(self.next_row(), 0, 1, 2))

        # special formatting for first_file, last_file and hdf_key:
        for _key in ['first_file', 'last_file', 'hdf_key']:
            self.add_param(self.params[_key], linebreak=True,
                           halign_text=QtCore.Qt.AlignLeft, n_columns_text=2,
                           n_columns=2, width= 250, width_text=200)

        self.w_selection_info = ReadOnlyTextWidget(
            fixedWidth=250, fixedHeight=90, visible=False)
        _layout.addWidget(self.w_selection_info, self.next_row(), 0, 1, 2)

        for _key in [key for key in self.params
                     if key not in self.param_widgets.keys()]:
            self.add_param(self.params[_key], width=100, width_text=140)
        self.param_widgets['n_image'].setEnabled(False)

        for _key in ['hdf_key', 'hdf_first_no', 'hdf_last_no', 'last_file',
                     'hdf_first_no', 'hdf_last_no', 'stepping']:
            self.toggle_widget_visibility(_key, False)

        self.b_exec = self.add_button('Generate composite',
                                      gridPos=(self.next_row(), 0, 1, 2),
                                      enabled=False)
        self.b_save = self.add_button('Save composite image as tif',
                                      gridPos=(self.next_row(), 0, 1, 2),
                                      enabled=False)
        self.toggle_roi_selection(False)
        self.add_spacer(height=20, gridPos=(self.next_row(), 0, 1, 2),
                        policy = QtWidgets.QSizePolicy.Expanding)

    def connect_signals(self):
        self.b_clear.clicked.connect(partial(self.__clear_entries, 'all'))

        self.param_widgets['flag_roi'].currentTextChanged.connect(
            self.toggle_roi_selection )
        self.param_widgets['first_file'].io_edited.connect(
            self.__selected_fist_file)
        self.param_widgets['last_file'].io_edited.connect(
            self.__selected_last_file)
        self.param_widgets['hdf_key'].io_edited.connect(
            self.__selected_hdf_key)
        for _key in ['hdf_first_no', 'hdf_last_no', 'stepping']:
            self.param_widgets[_key].io_edited.connect(
                self.update_n_image)

        # disconnect the generic param update connections and re-route to
        # composite update method
        self.param_widgets['composite_nx'].io_edited.disconnect()
        self.param_widgets['composite_nx'].io_edited.connect(
            partial(self.update_composite_dim, 'x'))
        self.param_widgets['composite_ny'].io_edited.disconnect()
        self.param_widgets['composite_ny'].io_edited.connect(
            partial(self.update_composite_dim, 'y'))

    def __selected_fist_file(self, fname):
        # reset all follow-up settings upon selecting a new
        self.__clear_entries(['hdf_key', 'hdf_first_no', 'hdf_last_no',
                            'last_file', 'stepping', 'n_image',
                            'composite_nx', 'composite_ny'])
        # depending on whether a hdf5 file has been selected, show and hide
        # different widgets:
        hdf_flag = (True if os.path.splitext(fname)[1] in HDF5_EXTENSIONS
                    else False)
        for _key in ['hdf_key', 'hdf_first_no', 'hdf_last_no']:
            self.toggle_widget_visibility(_key, hdf_flag)
            self.toggle_widget_visibility('last_file', not hdf_flag)
        self.param_widgets['last_file'].setVisible(not hdf_flag)
        self.__select_info['hdf_images'] = hdf_flag
        # open a pop-up to select the dataset from the hdf5 file
        if hdf_flag:
            dset = Hdf5DatasetSelection(self, fname).get_dset()
            self.update_param_value('hdf_key', dset)
            self.__selected_hdf_key()

    def __selected_hdf_key(self):
        _fname = self.params['first_file'].value
        _dset = self.params['hdf_key'].value
        dsets = get_hdf5_populated_dataset_keys(_fname)
        if _dset not in dsets:
            QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Dataset key error',
                (f'The selected file\n\n\t{_fname}\n\ndoes not have the '
                 f'selected dataset\n\n{_dset}')
            ).exec_()
            self.__clear_entries(['hdf_key'])
            self.toggle_widget_visibility('hdf_key', True)
            return
        _shape = get_hdf5_dataset_shape(_fname, _dset)
        self.w_selection_info.setText(
            (f'Number of images in dataset:\n  {_shape[0]}\n\nImage size:\n  '
             f'{_shape[1]} x {_shape[2]}'))
        self.update_param_value('n_image', _shape[0])
        self.__select_info['hdf_n_image'] = _shape[0]
        self.__show_selection_choices()

    def __selected_last_file(self):
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
            self.__clear_entries(['last_file'])
            return
        # get the list of all the files included in the selection:
        _flist = os.listdir(_path1)
        _flist.sort()
        i1 = _flist.index(_fname1)
        i2 = _flist.index(_fname2)
        _flist = _flist[i1:i2 + 1]
        # check that all selected files are of the same size:
        _fsizes = np.r_[[os.stat(f'{_path1}/{f}').st_size for f in _flist]]
        if _fsizes.std() > 0.:
            QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Files not of same size',
                (f'The selected files\n\n\t{_fname1}\n\nto\n\t{_fname2}'
                 f'\n\nare not all of the same size. Please verify the'
                 ' selection.')
            ).exec_()
            self.__clear_entries(['last_file'])
            return
        # finally, give information about number of selected files
        self.w_selection_info.setText(
            (f'Selected directory:\n  [...]/{os.path.basename(_path1)}\n'
             f'\nTotal number of selected files:\n  {i2 - i1 + 1}'))
        self.update_param_value('n_image', i2 - i1 + 1)
        self.__select_info['file_n_image'] = i2 - i1 + 1
        self.__select_info['file_list'] = _flist
        self.__show_selection_choices()

    def __show_selection_choices(self):
        self.w_selection_info.setVisible(True)
        for _key in ['stepping', 'composite_nx', 'composite_ny']:
            self.toggle_widget_visibility(_key, True)
        self.b_exec.setEnabled(True)

    def __clear_entries(self, keys='all'):
        if keys == 'all':
            keys = list(self.params.keys())
        for _key in keys:
            param = self.params[_key]
            param.restore_default()
            self.param_widgets[_key].set_value(param.default)
        self.w_selection_info.setVisible(False)
        for _key in ['hdf_key', 'hdf_first_no', 'hdf_last_no', 'last_file',
                     'hdf_first_no', 'hdf_last_no']:
            self.toggle_widget_visibility(_key, False)
        self.__select_info['hdf_images'] = None
        self.b_exec.setEnabled(False)

    def update_n_image(self):
        step = self.get_param_value('stepping')
        if self.__select_info['hdf_images']:
            i1 = self.get_param_value('hdf_first_no')
            i2 = self.get_param_value('hdf_last_no')
            if i2 == -1:
                i2 = self.__select_info['hdf_n_image']
            _n = (i2 - i1) // step
        elif self.__select_info['hdf_images'] == False:
            _n = self.__select_info['file_n_image'] // step
        if self.__select_info['hdf_images'] is not None:
            self.update_param_value('n_image', _n)


    def toggle_roi_selection(self, toggle):
        if isinstance(toggle, str):
            toggle = True if toggle == 'True' else False
        for _key in ['roi_xlow', 'roi_xhigh', 'roi_ylow', 'roi_yhigh']:
            self.param_widgets[_key].setEnabled(toggle)

    def frame_activated(self, index):
        ...

    def update_composite_dim(self, dim):
        n1 = self.param_widgets[f'composite_n{dim}'].get_value()
        n2 = int(np.ceil(self.get_param_value('n_image') / n1))
        dim2 = 'y' if dim == 'x' else 'x'
        self.params[f'composite_n{dim}'].value = n1
        self.update_param_value(f'composite_n{dim2}', n2)


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

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'), CompositeCreatorFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()