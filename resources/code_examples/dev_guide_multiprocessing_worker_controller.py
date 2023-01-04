import time
import pydidas
import numpy as np

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
