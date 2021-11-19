# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

from . import button_factory
from .button_factory import *

from . import progress_bar_factory
from .progress_bar_factory import *

from . import spin_box_factory
from .spin_box_factory import *

from . import check_box_factory
from .check_box_factory import *

from . import label_factory
from .label_factory import *

from . import line_factory
from .line_factory import *

from . import spacer_factory
from .spacer_factory import *

from . import combobox_factory
from .combobox_factory import *

from . import param_widget_factory
from .param_widget_factory import *

from . import radio_button_group_factory
from .radio_button_group_factory import *

__all__ = []
__all__ += button_factory.__all__
__all__ += spin_box_factory.__all__
__all__ += label_factory.__all__
__all__ += line_factory.__all__
__all__ += spacer_factory.__all__
__all__ += progress_bar_factory.__all__
__all__ += check_box_factory.__all__
__all__ += combobox_factory.__all__
__all__ += param_widget_factory.__all__
__all__ += radio_button_group_factory.__all__

# unclutter namespace and remove modules:
del spin_box_factory
del progress_bar_factory
del check_box_factory
del button_factory
del label_factory
del line_factory
del spacer_factory
del combobox_factory
del param_widget_factory
del radio_button_group_factory
