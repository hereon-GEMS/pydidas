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

"""Module with the PluginCollection Singleton class."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['get_generic_plugin_path', 'trim_filename',
           'plugin_type_check', 'plugin_consistency_check']


import os

from .plugin_constants import INPUT_PLUGIN, PROC_PLUGIN, OUTPUT_PLUGIN


def get_generic_plugin_path():
    """
    Get the generic plugin path.

    By default, plugins will be put in the pydidas/plugins folder whereas
    the code is located in the pydidas/pydidas folder.

    Returns
    -------
    str
        The path to the generic plugin folder.
    """
    return os.path.join(
        os.path.dirname(
        os.path.dirname(
        os.path.dirname(__file__))), 'plugins')


def trim_filename(path):
    """
    Trim a filename from a path if present.

    Parameters
    ----------
    path : str
        The file system path, including eventual filenames.

    Returns
    -------
    path : str
        The path without filename
    """
    path = os.path.dirname(path) if os.path.isfile(path) else path
    if os.sep == '/':
        path.replace('\\', os.sep)
    else:
        path.replace('/', os.sep)
    return path


def plugin_type_check(cls_item):
    """
    TO DO
    """
    if cls_item.basic_plugin:
        return 'base'
    if cls_item.plugin_type == INPUT_PLUGIN:
        return 'input'
    if cls_item.plugin_type == PROC_PLUGIN:
        return 'proc'
    if cls_item.plugin_type == OUTPUT_PLUGIN:
        return 'output'
    raise ValueError('Could not determine the plugin type for'
                     'class "{cls_item.__name__}"')


def plugin_consistency_check(cls_item):
    """
    Verify that plugins pass a rudimentary sanity check.

    Parameters
    ----------
    cls_item : plugin object
        A plugin class.

    Returns
    -------
    bool.
        Returns True if consistency check succeeded and False otherwise.
    """
    return (getattr(cls_item, '_is_pydidas_plugin', False)
            and not getattr(cls_item, 'basic_plugin', True))
