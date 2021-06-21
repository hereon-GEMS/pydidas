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

"""Subpackage with GUI elements."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import workflow_tree_edit_manager
from .workflow_tree_edit_manager import *

from . import data_browsing_frame
from .data_browsing_frame import *

from . import workflow_edit_frame
from .workflow_edit_frame import *

from . import base_frame
from .base_frame import *

from . import experiment_settings_frame
from .experiment_settings_frame import *

from . import scan_settings_frame
from .scan_settings_frame import *

from . import processing_single_plugin_frame
from .processing_single_plugin_frame import *

from . import processing_full_workflow
from .processing_full_workflow import *

from . import composite_creator_frame
from .composite_creator_frame import *

__all__ += workflow_tree_edit_manager.__all__
__all__ += data_browsing_frame.__all__
__all__ += workflow_edit_frame.__all__
__all__ += base_frame.__all__
__all__ += experiment_settings_frame.__all__
__all__ += scan_settings_frame.__all__
__all__ += processing_single_plugin_frame.__all__
__all__ += processing_full_workflow.__all__
__all__ += composite_creator_frame.__all__

# Unclutter namespace: remove modules from namespace
del workflow_tree_edit_manager
del data_browsing_frame
del workflow_edit_frame
del base_frame
del experiment_settings_frame
del scan_settings_frame
del processing_single_plugin_frame
del processing_full_workflow
del composite_creator_frame
