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
Module with the ViewResultsFrame which allows to visualize results from
running the pydidas WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ViewResultsFrame']

from ..core import get_generic_param_collection
from ..workflow import WorkflowResults
from .builders.view_results_frame_builder import (
    ViewResultsFrameBuilder)
from .mixins import ViewResultsMixin

RESULTS = WorkflowResults()


class ViewResultsFrame(ViewResultsFrameBuilder, ViewResultsMixin):
    """
    The ViewResultsFrame is used to visualize the results from running the
    WorkflowTree.
    """
    default_params = get_generic_param_collection(
        'selected_results', 'saving_format', 'enable_overwrite')

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        ViewResultsFrameBuilder.__init__(self, parent)
        self.set_default_params()
        self.build_frame()
        ViewResultsMixin.__init__(self)
