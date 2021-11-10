
from . import base_plugin
from .base_plugin import *

from . import base_input_plugin
from .base_input_plugin import *

from . import base_proc_plugin
from .base_proc_plugin import *

from . import base_output_plugin
from .base_output_plugin import *

from . import plugin_constants
from .plugin_constants import *

from . import plugin_collection
from .plugin_collection import *

from . import pyfai_integration_base
from .pyfai_integration_base import *

from . import plugin_getter_
from .plugin_getter_ import *

__all__ = []
__all__ += base_plugin.__all__
__all__ += base_input_plugin.__all__
__all__ += base_proc_plugin.__all__
__all__ += base_output_plugin.__all__
__all__ += plugin_collection.__all__
__all__ += pyfai_integration_base.__all__
__all__ += plugin_getter_.__all__

# unclutter namespace and delete imported modules
del base_plugin
del base_input_plugin
del base_proc_plugin
del base_output_plugin
del plugin_constants
del plugin_collection
del pyfai_integration_base
del plugin_getter_
