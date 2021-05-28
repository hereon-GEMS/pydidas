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

"""
Module with the ImageReaderFactory which returns always the same instance
of the ImageReader.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ImageReaderFactory']

import os


class ReaderBuilder:
    """
    Builder class to prevent multiple instances of any ImageReader subclass
    to be created.
    """
    def __init__(self, obj):
        """
        Initialization

        Parameters
        ----------
        obt : ImageReader
            The concrete implementation of the ImageReader class for this
            particular reader and file format.
        """
        self._instance = None
        self._object = obj


    def __call__(self, **kwargs):
        """
        Get the ImageReaer (subclass) instance.

        If an instance exists, it is returned. If no instance exists yet,
        one is created.

        Returns
        -------
        instance : object
            The instance of the ImageReader
        """
        if not self._instance:
            self._instance = self._object()
        return self._instance


class _ImageReaderFactory:
    """
    Factory to manage readers for different file types.
    """

    def __init__(self):
        self._readers = {}
        self._extensions = {}

    def register_format(self, filetype, ext, reader):
        """
        Register a new file type.

        This method registers new file types to the image reader and also
        maps the specified extensions to the file type and image reader.

        Note that file extensions will not be handled case-sensitive.

        Parameters
        ----------
        filetype : str
            The reference name of the filetype to register
        ext : list
            A list of string entries for the different extensions associated
            with this specific file type.
        reader : object
            The reader implementation class (not its instance! - The instance
            will be managed by the Builder).
        """
        self._readers[filetype] = ReaderBuilder(reader)
        for ex in ext:
            self._extensions[ex] = filetype

    def get_reader(self, filename, **kwargs):
        """
        Get the reader associated with the filetype of filename.

        This method finds the ImageReader registered to the file extension
        of the input filename and returns the instance for reading the image.

        Parameters
        ----------
        filename : str
            The filename including the extension and the full path.

        Returns
        -------
        reader : ImageReader
            The instance of the ImageReader implementation.
        """
        fhead, ext = os.path.splitext(filename)
        ext = ext.lower()
        if not ext in self._extensions.keys():
            raise ValueError(f'Extension "{ext}" not supported.')
        reader = self._readers.get(self._extensions[ext])
        if not reader:
            raise ValueError(f'Extension "{ext}" not supported.')
        return reader(**kwargs)


class ImageReaderFactoryBuilder:
    """
    Builder class to prevent multiple instances of the _ImageReaderFactory to
    be created.
    """
    def __init__(self):
        """
        Initialization
        """
        self._instance = None

    def __call__(self, **kwargs):
        """
        Get the _ImageReaderFactory instance.

        If an instance of ImageReaderFactory exists, it is returned.
        If no instance exists yet, one is created and returned.

        Returns
        -------
        _ImageReaderFactory
            The class instance.
        """
        if not self._instance:
            self._instance = _ImageReaderFactory()
        return self._instance


ImageReaderFactory = ImageReaderFactoryBuilder()
