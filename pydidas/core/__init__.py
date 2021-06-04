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

from . import parameter
from .parameter import *

from . import dataset
from .dataset import *

from . import parameter_collection
from .parameter_collection import *

from . import object_with_parameter_collection
from .object_with_parameter_collection import *

from . import composites
from .composites import *

from . import composite_image
from .composite_image import *

from . import generic_parameters
from .generic_parameters import *

from . import global_settings
from .global_settings import *

from . import experimental_settings
from .experimental_settings import *

from . import scan_settings
from .scan_settings import *

from . import hdf_key
from .hdf_key import *

__all__ += composites.__all__
__all__ += parameter_collection.__all__
__all__ += parameter.__all__
__all__ += object_with_parameter_collection.__all__
__all__ += dataset.__all__
__all__ += global_settings.__all__
__all__ += experimental_settings.__all__
__all__ += scan_settings.__all__
__all__ += hdf_key.__all__
__all__ += composite_image.__all__
__all__ += generic_parameters.__all__

# Unclutter namespace: remove modules from namespace
del composites
del parameter
del dataset
del global_settings
del experimental_settings
del scan_settings
del hdf_key
del parameter_collection
del object_with_parameter_collection
del composite_image
del generic_parameters
