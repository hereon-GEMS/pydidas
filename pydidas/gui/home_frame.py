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
Module with the HomeFrame which acts as a starting and reference point when
opening pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['HomeFrame']

import os
from qtpy import QtGui, QtCore

from ..core.utils import get_doc_home_address
from ..widgets import BaseFrame


_toolbar_use_text = (
    'Use the menu toolbar on the left to switch between different Frame. '
    'Some menu toolbars will open an additional submenu on  the left. The '
    'active frame is highlighted.')

_doc_address = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'docs', 'build', 'html', 'index.html').replace('\\', '/')
_help_text = (
    'Documentation is available in the html format. You can open the '
    'documentation from any frame using the "Help" menu entry to either open '
    'it in the system\'s web browser or a window.\nOr follow this link to '
    f'<a href="{get_doc_home_address()}">open the documentation in a browser'
    '</a>.')

_proc_setup_text = (
    'Setting up a processing job requires three different object to be set: '
    '\n  1. The experimental setup. This includes values such as the beamline '
    'energy, detector and detector geometry.'
    '\n  2. The scan setup. This includes the number of scan dimensions and '
    'number of scan points per dimension.'
    '\n  3. The processing workflow. The workflow must includes all the '
    'plugins which should be executed.'
    '\n\nEach object has its own dedicated setup frame with importers and '
    'exporters for the various supported formats.')

_proc_text = (
    'The processing can be started and visualized in the '
    '"Run Full Processing" frame.\n'
    'Once the processing has been started, it will run in a separate'
    ' process and the GUI will stay responsive. \n'
    'Results can be visualized on the fly while the processing is '
    'running by selecting the desired node and axes.\n'
    'For a full tutorial, please visit the corresponding help page: '
    f'<a href="{get_doc_home_address()}">open the processing documentation'
    ' in a browser</a>.')


class HomeFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)

        self.create_label('label_welcome', 'Welcome to pydidas',
                          fontsize=14, bold=True, fixedWidth=400)
        self.create_label('label_full_name',
                          '- the python Diffraction Data Analysis Suite.',
                          fontsize=13, bold=True, fixedWidth=400)
        self.create_spacer(None)
        self.create_label('label_quickstart', 'Quickstart hints:',
                          fontsize=12, bold=True, fixedWidth=400)
        self.create_spacer(None)
        self.create_label('label_toolbar', 'Menu toolbar:', fontsize=11,
                          underline=True, bold=True, fixedWidth=400)
        self.create_label('label_toolbar_use', _toolbar_use_text,
                          fixedWidth=600)
        self.create_spacer(None)

        self.create_label('label_help_header', 'Online help:', fontsize=11,
                          underline=True, bold=True, fixedWidth=400)
        self.create_label(
            'label_help', _help_text, fixedWidth=600, openExternalLinks=True,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            textFormat=QtCore.Qt.RichText)
        self._widgets['label_help'].linkActivated.connect(self.open_link)
        self.create_spacer(None)

        self.create_label('label_proc_setup', 'Processing setup:', fontsize=11,
                          underline=True, bold=True, fixedWidth=400)
        self.create_label('label_processing_setup', _proc_setup_text,
                          fixedWidth=600)

        self.create_label('label_proc', 'Processing:', fontsize=11,
                          underline=True, bold=True, fixedWidth=400)
        self.create_label(
            'label_processing', _proc_text, fixedWidth=600,
            openExternalLinks=True, textFormat=QtCore.Qt.RichText,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse)

    @QtCore.Slot(str)
    def open_link(self, link_str):
        """
        Open a link in the system's default browser.

        Parameters
        ----------
        link_str : str
            The link address.
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(link_str))
