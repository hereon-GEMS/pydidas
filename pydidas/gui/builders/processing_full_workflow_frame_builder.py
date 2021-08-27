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

"""
Module with the create_processing_full_workflow_frame_widgets_and_layout
function which is used to populate the ProcessingFullWorkflowFrame with
widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_processing_full_workflow_frame_widgets_and_layout']

import qtawesome as qta


def create_processing_full_workflow_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.ProcessingFullWorkflowFrame
        The ProcessingFullWorkflowFrame instance.
    """
    frame._widgets = {}
    _layout = frame.layout()
    _layout.setHorizontalSpacing(10)
    _layout.setVerticalSpacing(5)

    frame.create_label('title', 'Full processing workflow', fontsize=14,
                       gridPos=(0, 0, 1, 5))

    frame.create_spacer('title_spacer', height=20, gridPos=(-1, 0, 1, 2))
    frame.create_button('but_verify_config', 'Verify all settings',
                        gridPos=(-1, 0, 1, 2),
                        icon=qta.icon('mdi.text-search'))

    frame.create_spacer(None, height=20, gridPos=(-1, 0, 1, 2))
    frame.create_param_widget(frame.params['run_type'])

    frame.create_spacer(None, height=20, gridPos=(-1, 0, 1, 2))
    frame.create_button('but_run', 'Run', gridPos=(-1, 0, 1, 2),
                        icon=qta.icon('fa5s.play'), fixedHeight=50,
                        fixedWidth=600)

    frame.create_spacer(None, height=50, gridPos=(-1, 0, 1, 2))
    frame.create_button('but_feedback', 'Processing feedback',
                        gridPos=(-1, 0, 1, 2))
