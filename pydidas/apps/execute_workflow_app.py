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

"""Module with the ExecuteWorkflowApp class which allows to run workflows."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExecuteWorkflowApp']

import os
import time

import numpy as np
from PyQt5 import QtCore

from pydidas.apps.app_utils import FilelistManager, ImageMetadataManager
from pydidas.apps.base_app import BaseApp
from pydidas._exceptions import AppConfigError
from pydidas.core import (ParameterCollection, Dataset,
                          CompositeImage, get_generic_parameter)
from pydidas.constants import HDF5_EXTENSIONS
from pydidas.utils import (check_file_exists, check_hdf5_key_exists_in_file)
from pydidas.image_io import read_image, rebin2d
from pydidas.utils import copy_docstring
from pydidas.apps.app_parsers import parse_composite_creator_cmdline_arguments
from pydidas.workflow_tree import WorkflowTree

TREE = WorkflowTree()

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('live_processing'),
    get_generic_parameter('first_file'),
    get_generic_parameter('last_file'),
    get_generic_parameter('file_stepping'),
    get_generic_parameter('hdf5_key'),
    get_generic_parameter('hdf5_first_image_num'),
    get_generic_parameter('hdf5_last_image_num'),
    get_generic_parameter('hdf5_stepping'),
    get_generic_parameter('use_bg_file'),
    get_generic_parameter('bg_file'),
    get_generic_parameter('bg_hdf5_key'),
    get_generic_parameter('bg_hdf5_frame'),
    get_generic_parameter('composite_nx'),
    get_generic_parameter('composite_ny'),
    get_generic_parameter('composite_dir'),
    get_generic_parameter('use_roi'),
    get_generic_parameter('roi_xlow'),
    get_generic_parameter('roi_xhigh'),
    get_generic_parameter('roi_ylow'),
    get_generic_parameter('roi_yhigh'),
    get_generic_parameter('use_thresholds'),
    get_generic_parameter('threshold_low'),
    get_generic_parameter('threshold_high'),
    get_generic_parameter('binning'),
    )


class ExecuteWorkflowApp(BaseApp):
    """
    Inherits from :py:class:`pydidas.apps.BaseApp<pydidas.apps.BaseApp>`

    The ExecuteWorkflowApp is used to run workflows which can be any operation
    which can be written as Plugin.

    Parameters can be passed either through the argparse module during
    command line calls or through keyword arguments in scripts.

    The names of the parameters are similar for both cases, only the calling
    syntax changes slightly, based on the underlying structure used.
    For the command line, parameters must be passed as -<parameter name>
    <value>.
    For keyword arguments, parameters must be passed during instantiation
    using the keyword argument syntax of standard <parameter name>=<value>.

    Parameters
    ----------
    """
    default_params = DEFAULT_PARAMS
    mp_func_results = QtCore.pyqtSignal(object)
    updated_composite = QtCore.pyqtSignal()
    parse_func = parse_composite_creator_cmdline_arguments
    attributes_not_to_copy_to_slave_app = []

    def __init__(self, *args, **kwargs):
        """
        Create a CompositeCreatorApp instance.
        """
        super().__init__(*args, **kwargs)
        self._composite = None
        self._det_mask = None
        self._bg_image = None

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()

    def prepare_run(self):
        """
        Prepare running the workflow execution.
        """
        _leaves = TREE.get_all_leaves()


    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.
        """
        if 'mp_tasks' not in self._config.keys():
            raise KeyError('Key "mp_tasks" not found. Please execute'
                           'multiprocessing_pre_run() first.')
        return self._config['mp_tasks']

    def multiprocessing_pre_cycle(self, index):
        """
        Run preparatory functions in the cycle prior to the main function.

        Parameters
        ----------
        index : int
            The index of the image / frame.
        """
        self._store_args_for_read_image(index)



    def multiprocessing_carryon(self):
        """
        Get the flag value whether to carry on processing.

        By default, this Flag is always True. In the case of live processing,
        a check is done whether the current file exists.

        Returns
        -------
        bool
            Flag whether the processing can carry on or needs to wait.

        """
        if self.get_param_value('live_processing'):
            return self._image_exists_check(self._config['current_fname'],
                                            timeout=0.02)
        return True



    def multiprocessing_func(self, *index):
        """
        Perform key operation with parallel processing.

        Returns
        -------
        _image : pydidas.core.Dataset
            The (pre-processed) image.
        """
        _image = read_image(self._config['current_fname'],
                            **self._config['current_kwargs'])
        _image = self.__apply_mask(_image)
        return _image


    def multiprocessing_post_run(self):
        """
        Perform operatinos after running main parallel processing function.
        """


    @QtCore.pyqtSlot(int, object)
    def multiprocessing_store_results(self, index, image):
        """
        Store the results of the multiprocessing operation.

        Parameters
        ----------
        index : int
            The index in the composite image.
        image : np.ndarray
            The image data.
        """
