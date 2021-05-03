#!/usr/bin/env python

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

"""Module with Warning class for showing notifications."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScrollArea']

from PyQt5 import QtWidgets

class ScrollArea(QtWidgets.QScrollArea):
    """
    Convenience class to simplify the setup of a QScrollArea.
    """
    def __init__(self, parent=None, **kwargs):
        """
        Create a QScrollArea with defined widgets, width and height.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget. The default is None.
        **kwargs : keyword arguments

        Supported keywords
        ------------------
        widget : QWidget, optional
            The scroll area's own widget which is displayed.
            The default is None.
        fixedWidth : int, optional
            If the scroll area shall have a fixed width, this value can be
            defined in pixel. The default is None.
        fixedHeight : int, optional
            If the scroll area shall have a fixed height, this value can be
            defined in pixel. The default is None.

        Returns
        -------
        None.

        """
        super().__init__(parent)
        self._parent = parent
        params = dict(widget=kwargs.get('widget', None),
                      width=kwargs.get('width', None),
                      height=kwargs.get('height', None),
                      fixedHeight=kwargs.get('fixedHeight', None),
                      minHeight=kwargs.get('minHeight', None),
                      maxHeight=kwargs.get('maxHeight', None),
                      fixedWidth=kwargs.get('fixedWidth', None),
                      minWidth=kwargs.get('minWidth', None),
                      maxWidth=kwargs.get('maxWidth', None),
                      )
        if params['widget']:
            self.setWidget(params['widget'])
        self.setWidgetResizable(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setAutoFillBackground(True)
        if params['fixedWidth']:
            self.setFixedWidth(params['fixedWidth'])
        if params['minWidth']:
            self.setMinimumWidth(params['minWidth'])
        if params['maxWidth']:
            self.setMinimumWidth(params['maxWidth'])
        if params['fixedHeight']:
            self.setFixedHeight(params['fixedHeight'])
        if params['minHeight']:
            self.setMinimumHeight(params['minHeight'])
        if params['maxHeight']:
            self.setMinimumHeight(params['maxHeight'])
