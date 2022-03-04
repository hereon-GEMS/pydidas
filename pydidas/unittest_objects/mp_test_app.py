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
Module with the MpTestApp class which allows to test a dummy application in
real multiprocessing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['MpTestApp']

import time

import numpy as np
from qtpy import QtCore

# because these Plugins will be loaded directly by importlib, absolute imports
# are required:
from pydidas.core import get_generic_param_collection, BaseApp
from pydidas.image_io import CompositeImage


def get_test_image(index, **kwargs):
    """
    Get a random test image.

    This function aims to mimic a real file loading and hence it has a
    dummy variable for an index.

    Parameters
    ----------
    index : object
        The index. Not used within the function but the pydidas architecture
        expects it.
    **kwargs : dict
        A dictionary with additional keyword arguments.

    Returns
    -------
    np.ndarray
        A two-dimension array with random numbers.

    """
    _shape = kwargs.get('shape', (20, 20))
    return np.random.random(_shape) + 1e-5


class MpTestApp(BaseApp):
    """
    A test Application for multiprocessing.
    """
    default_params = get_generic_param_collection(
        'hdf5_first_image_num', 'hdf5_last_image_num')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_params()
        self._composite = None
        self._config = {'n_image': None,
                        'datatype': None,
                        'mp_pre_run_called': False,
                        'mp_post_run_called': False,
                        'calls': 0,
                        'min_index': 0,
                        'max_index': 40
                        }

    def multiprocessing_pre_run(self):
        """
        The pre-run method sets up the tasks and creates a compositite image.
        """
        self._config['mp_pre_run_called'] = True
        self._config['mp_tasks'] = range(self._config['min_index'],
                                         self._config['max_index'])
        self._composite = CompositeImage(
            image_shape=(20, 20),
            composite_nx=10,
            composite_ny=int(np.ceil((self._config['max_index'])/10)),
            composite_dir='x',
            datatype=np.float64)

    def multiprocessing_get_tasks(self):
        """
        Get the tasks of the Application.

        In the case of the MpTestApp, this is a list of indices to be inserted
        into the multiprocessing queue.

        Returns
        -------
        range
            The range of tasks.
        """
        return self._config['mp_tasks']

    def multiprocessing_carryon(self):
        """
        Check for carryon calls.

        For testing, this method will alternate to yield True and False replies
        to the query.

        Returns
        -------
        bool
            The flag whether data is available or not.
        """
        self._config['calls'] += 1
        if self._config['calls'] % 2:
            time.sleep(0.001)
            return False
        return True

    def multiprocessing_func(self, index):
        """
        Perform the multiprocessing computation.

        The MpTestApp will only return a random image.

        Parameters
        ----------
        index : int
            The input index of the image.

        Returns
        -------
        image : np.ndarray
            The image data.
        """
        _fname, _kwargs = 'dummy', {'shape': (20, 20)}
        _image = get_test_image(_fname, **_kwargs)
        return _image

    @QtCore.Slot(int, object)
    def multiprocessing_store_results(self, index, image):
        """
        Store the result of the multiprocessing function call.

        The MpTestApp will insert the random image into the composite.

        Parameters
        ----------
        index : int
            The image index. This determines the position in the composite
            image.
        image : np.ndarray
            The image data.
        """
        self._composite.insert_image(image, index - self._config['min_index'])

    def multiprocessing_post_run(self):
        """
        Call post-run operations.

        The MpTestApp will only store an internal variable to document that
        this method has been called.
        """
        self._config['mp_post_run_called'] = True
