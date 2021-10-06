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

"""Package with individual QtWidgets used for the plugin parameter settings."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import parameter_collection_config_widget
from .parameter_collection_config_widget import *

from . import  parameter_config_widget
from .parameter_config_widget import *

from . import parameter_widgets_mixin
from .parameter_widgets_mixin import *

from . import plugin_param_config
from .plugin_param_config import *

__all__ += parameter_collection_config_widget.__all__
__all__ += parameter_config_widget.__all__
__all__ += parameter_widgets_mixin.__all__
__all__ += plugin_param_config.__all__

#unclutter the namespace:
del parameter_collection_config_widget
del parameter_config_widget
del parameter_widgets_mixin
del plugin_param_config
