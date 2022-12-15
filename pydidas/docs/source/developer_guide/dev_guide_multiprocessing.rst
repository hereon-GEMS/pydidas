.. _developer_guide_to_multiprocessing:

Developers guide to pydidas multiprocessing
===========================================


.. contents::
    :depth: 2
    :local:
    :backlinks: none
    
    
Pydidas offers multiprocessing using the python multiprocessing package with
a controller process in a separate thread to prevent the caller from blocking.

The :py:class:`WorkerController <pydidas.multiprocessing.WorkerController>` is 
the generic pydidas implementation and the :py:class:`AppRunner 
<pydidas.multiprocessing.AppRunner>` is the subclassed version to run pydidas 
apps.

WorkerController
----------------

Pydidas uses the :py:class:`WorkerController 
<pydidas.multiprocessing.WorkerController>` class to run generic (function) 
tasks. 

Communication with workers
^^^^^^^^^^^^^^^^^^^^^^^^^^

Communication with the workers is handles by four queues:

- **send** queue to send tasks to the workers.
- **reveiver** queue to receive results from the workers.
- **stop** queue to send stop signals to the workers.
- **finished** queue for the workers to signal they have completed all tasks.

The user does not have to interact with the queues itself, this is handled by 
the :py:class:`WorkerController <pydidas.multiprocessing.WorkerController>`.

If the user wants to stop the workers, they can use the 
:py:meth:`send_stop_signal 
<pydidas.multiprocessing.WorkerController.send_stop_signal>` method:

.. automethod:: pydidas.multiprocessing.WorkerController.send_stop_signal
    :noindex:

Communication with the user
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :py:class:`WorkerController <pydidas.multiprocessing.WorkerController>` 
uses **Qt's** slots and signals for communicating results to the user.

Three signals are provided:

- **sig_progress(float):** This signal is emitted after a result has been 
  received and gives the current progress, normalized to the range [0, 1).
- **sig_results(object, object):** This signal is emitted for each result and
  returns the tuple (task argument, task result) to allow identification of
  the result.
- **sig_finshed:** The finished signal is emitted once all tasks have been 
  performed and all workers have finished.

.. note:: 

    It is the responsibility of the user to connect to the signals prior to 
    starting a process to receive the results.
    Because of the Qt framework's behaviour, an eventloop must be running for
    the signals to be processed.
    

Key methods
^^^^^^^^^^^

The following methods are key to using the :py:class:`WorkerController 
<pydidas.multiprocessing.WorkerController>` :

.. list-table::
    :widths: 30 70
    :header-rows: 1
    :class: tight-table
    
    * - method name
      - description
    * - change_function(func, \*args, \*\*kwargs)
      - Change the function to be called by the workers. \*args and \*\*kwargs
        can be any additional calling arguments to the function. The first
        calling argument will always be the task.
    * - add_task(task)
      - Add the given task to the list of tasks to be processed.
    * - add_tasks(tasks)
      - Add all individual tasks from the iterable argument to the list of tasks
        to be processed.
    * - finalize_tasks()
      - This method will add *stop tasks* to the queue to inform the workers 
        that all tasks have been successfully finished. 
        Calling this method will also flag the workers to finish and the 
        processes will terminate after finishing all calculations.
    * - start()
      - The run method will start the thread event loop, start the worker 
        processes and submit all tasks to the queue.
    * - suspend()
      - Suspend will temporarily suspend the event loop. **Note** that all
        submitted tasks will still be processed by the workers but no new
        tasks will be submitted and no results will be processed.
    * - restart()
      - This method will restart processing of the event loop.

Examples
^^^^^^^^

Minimal working example
```````````````````````

The following minimal working example can be run from an interactive console
or saved as file.

.. code-block::

    import time
    import pydidas
    import numpy as np

    from qtpy import QtTest


    def test_func(task, slope, offset):
        return task* slope + offset


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
        print(results)
    
        print("WorkerController is alive: ", worker_controller.is_alive())


    if __name__ == "__main__":
        run_worker_controller()


Working example with restart of the Thread
``````````````````````````````````````````

In the following example, not calling the :py:meth:`finalize_tasks 
<pydidas.multiprocessing.WorkerController.finalize_tasks>` will keep the 
thread alive and allow the submission of new tasks.

.. code-block::

    import time
    import pydidas
    import numpy as np

    from qtpy import QtTest


    def test_func(task, slope, offset):
        return task* slope + offset


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


AppRunner
---------

The :py:class:`AppRunner <pydidas.multiprocessing.AppRunner>` is the specialized
subclass to work with pydidas :py:class:`Apps <pydidas.core.BaseApp>`.

A sequence diagram of the communicatino with the :py:class:`AppRunner 
<pydidas.multiprocessing.AppRunner>` is given below.

.. image:: images/AppRunner_sequence.png
    :width: 400px
    :align: center

The app_processor
^^^^^^^^^^^^^^^^^

The :py:func:`app_processor <pydidas.multiprocessing.app_processor>` 
functionality is summarized in the flowchart below:

.. image:: images/app_processor_logic_flow_chart.png
    :width: 400px
    :align: center
