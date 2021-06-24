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

"""Module with a factory function to create formatted QSpinBoxes."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_progress_bar']

from PyQt5.QtWidgets import QProgressBar

from ..utilities import apply_widget_properties

def create_progress_bar(**kwargs):
    """
    Create a QSpinBox widget and set properties.

    Parameters
    ----------
    **kwargs : dict
        Any supported keyword arguments.

    Supported keyword arguments
    ---------------------------
    *Qt settings : any
        Any supported Qt settings for a QProgressBar (for example minimum,
        maximum, fixedWidth, visible, enabled)

    Returns
    -------
    bar : QtWidgets.QProgressBar
        The instantiated progress bar widget.
    """
    _bar = QProgressBar()
    apply_widget_properties(_bar, **kwargs)
    return _bar
