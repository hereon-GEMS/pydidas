# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import time

import numpy as np
import pydidas
from qtpy import QtTest


def test_func(task, slope, offset):
    return task * slope + offset


def run_worker_controller():
    worker_controller = pydidas.multiprocessing.WorkerController()
    worker_controller.change_function(test_func, 2, 5)
    result_spy = QtTest.QSignalSpy(worker_controller.sig_results)

    worker_controller.add_tasks(np.arange(10))
    worker_controller.finalize_tasks()
    worker_controller.start()

    while True:
        print("Progress at ", worker_controller.progress)
        if worker_controller.progress >= 1:
            break
        time.sleep(0.5)

    results = sorted(result_spy)

    print("Results: ", results)
    print("WorkerController is alive: ", worker_controller.isRunning())


def run_worker_controller_with_restart():
    worker_controller = pydidas.multiprocessing.WorkerController()
    worker_controller.change_function(test_func, 2, 5)
    result_spy = QtTest.QSignalSpy(worker_controller.sig_results)

    worker_controller.add_tasks(np.arange(10))
    # worker_controller.finalize_tasks()
    worker_controller.start()

    print("\nWaiting for results ...")
    with pydidas.core.utils.TimerSaveRuntime() as runtime:
        while True:
            if worker_controller.progress >= 1:
                break
            time.sleep(0.005)
    print("Runtime was ", runtime())

    results = sorted(result_spy)
    print("Results: ", results)
    print("WorkerController is alive: ", worker_controller.isRunning())

    worker_controller.add_tasks(np.arange(10, 20))

    print("\nWaiting for results ...")
    with pydidas.core.utils.TimerSaveRuntime() as runtime:
        while True:
            if worker_controller.progress >= 1:
                break
            time.sleep(0.005)
    print("Runtime was ", runtime())

    results = sorted(result_spy)
    print("Results: ", results)

    # now, if we suspend it, to change the function, and to add more items to
    # its tasks but they will not be processed:
    worker_controller.suspend()

    worker_controller.change_function(test_func, -1, 0)
    worker_controller.add_tasks(np.arange(20, 30))

    time.sleep(0.2)

    # restarting will spawn new Processes to carry out the calculations:
    worker_controller.restart()

    print("\nWaiting for results ...")
    with pydidas.core.utils.TimerSaveRuntime() as runtime:
        while True:
            if worker_controller.progress >= 1:
                break
            time.sleep(0.005)
    print("Runtime was ", runtime())

    results = sorted(result_spy)
    print("Results: ", results)
    print("WorkerController is alive: ", worker_controller.isRunning())


if __name__ == "__main__":
    # run_worker_controller()
    run_worker_controller_with_restart()
