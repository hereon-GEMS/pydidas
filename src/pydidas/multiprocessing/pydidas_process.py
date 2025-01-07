# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The PydidasProcess ignores the interrupt signal.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasProcess"]


import signal
from multiprocessing import Process


class PydidasProcess(Process):
    """
    A subclassed multiprocessing.Process which ignores the SIGINT signal.

    The PydidasProcess can be used to ignore KeyboardInterrupts in the main process.
    However, the script takes responbisiblity to handle worker shutdown.
    """

    def __init__(self, *args, **kwargs):
        Process.__init__(self, *args, **kwargs)

    def run(self):
        """Reimplement the Process.run witih signal interruption."""
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        Process.run(self)
