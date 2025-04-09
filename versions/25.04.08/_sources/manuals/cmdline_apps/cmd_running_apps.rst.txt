..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _running_pydidas_applications: 

Running pydidas applications
============================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Pydidas applications are designed to be runnable both in serial and parallel
modes. This requires a different syntax from the user which will be presented 
below. 

.. note::
    For a detailed description of the internal workings of applications
    please refer to the :ref:`developer_guide_to_apps` section.

Configuring an application
--------------------------

pydidas applications are standard pydidas objects and their configuration is 
handled using pydidas :py:class:`Parameters <pydidas.core.Parameter>`. A 
short usage guide has already been given in :ref:`accessing_parameters`.

Some applications might have additional properties or methods to further 
interact with the user, but these will be covered in the specific manuals.

As an example, let us use a :py:class:`DummyApp` which creates a list with 
random strings and takes two parameters for the length of each string and the 
total number of strings.

.. warning::

    The DummyApp is not a real object in pydidas. This example cannot be 
    run in a real python console.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.DummyApp()
    >>> app.get_param_keys()
    ['number_of_strings', 'length_of_string']
    >>> app.set_param_value('number_of_strings', 10)
    >>> app.set_param_value('length_of_string', 10)

Running an application serially
-------------------------------

To run an app serially, simply call the :py:meth:`run 
<pydidas.core.BaseApp.run>` method of the app. Note that this will be a 
blocking call until the application is finished with its processing. 

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.DummyApp()
    >>> app.set_param_value('number_of_strings', 10)
    >>> app.set_param_value('length_of_string', 10)
    >>> app.run()
    >>> app.get_results()
    ['yeOhsEodCq',
     'gnqZKRxHcK',
     'SbEbVlyjgx',
     'gcrNYzGUQY',
     'NnfLeTcXbS',
     'xoweEcFgqs',
     'ujHXTPsWyh',
     'XoOkaRqvIv',
     'ewrMXWBpdG',
     'TurPkkywwJ']

Running an application using parallelization
--------------------------------------------

.. note::

    For a detailed description of how the pydidas multiprocessing works,
    please refer to the :ref:`multiprocessing_package` or to the 
    :ref:`developer_guide_to_multiprocessing`.

To run an application using parallel processing, an additional object is needed
to control the parallelization. This is the 
:py:class:`AppRunner <pydidas.multiprocessing.AppRunner>`. Usage is 
straightforward and happens through only a few commands. The AppRunner starts
in a separate thread and is non-blocking. It launches multiple independent
processes and can run in the background.

To run an application, first configure the application as usually. Then,
create an :py:class:`AppRunner <pydidas.multiprocessing.AppRunner>` instance
with the configured application as calling argument. The app instance in the 
:py:class:`AppRunner <pydidas.multiprocessing.AppRunner>` is not directly 
accessible but the user can use the runner's
:py:meth:`call_app_method <pydidas.multiprocessing.AppRunner.call_app_method>`
method to call a method of the app or the 
:py:meth:`set_app_param <pydidas.multiprocessing.AppRunner.set_app_param>`
method to modify one of the application's parameters.

.. warning::
    
    Starting the :py:class:`AppRunner <pydidas.multiprocessing.AppRunner>` will
    create a new instance of the application and any changes made to the local
    instance will not be mirrored in the 
    :py:class:`AppRunner <pydidas.multiprocessing.AppRunner>`'s app instance.

Running an application with the 
:py:class`AppRunner <pydidas.multiprocessing.AppRunner>` requires to call the 
:py:data:`start` method. This will start the thread and create the worker
processes.

.. warning::

    Running apps which rely on Qt's Signals and Slots (like the 
    :py:class:`ExecuteWorkflowApp <pydidas.apps.ExecuteWorkflowApp>`) will 
    require a running QApplication event loop.
    Also do not forget to stop the event loop when finished.

An example with a custom application is given below:

.. code-block::

    import random
    import string

    import numpy as np
    from qtpy import QtWidgets

    import pydidas


    #define CHARS to create random strings
    CHARS = string.ascii_letters + string.digits


    class DummyApp(pydidas.core.BaseApp):
        default_params = pydidas.core.ParameterCollection(
            pydidas.core.Parameter('number_of_strings', int, 10),
            pydidas.core.Parameter('length_of_strings', int, 10),
        )

        def multiprocessing_pre_run(self):
            self.results = {}
            pydidas.core.BaseApp.multiprocessing_pre_run(self)

        def multiprocessing_get_tasks(self):
            """Get the dummy tasks."""
            return np.arange(self.get_param_value('number_of_strings'))

        def multiprocessing_func(self, index):
            """Create a random string."""
            length = self.get_param_value('length_of_strings', 10)
            return ''.join(random.choice(CHARS) for _ in range(length))

        def multiprocessing_store_results(self, index, result):
            self.results[index] = result


    def main():
        qtapp = QtWidgets.QApplication.instance()
        app = DummyApp()
        runner = pydidas.multiprocessing.AppRunner(app)

        # Now connect the AppRunner's emitted results to our local app:
        runner.sig_results.connect(app.multiprocessing_store_results)

        # Also make sure to terminate the QApplication event loop after
        # finishing the calculations:
        runner.finished.connect(qtapp.quit)

        # Start the runner and the QApplication event loop:
        runner.start()
        qtapp.exec_()

        print('Resulting random strings:')
        for _key, _val in app.results.items():
            print(f'  {_key:02d}: {_val}')


    if __name__ == '__main__':
        main()

Running this script will create an output like:

.. code-block::

    Resulting random strings:
      00: EgLDoQCBto
      01: tbE07t910T
      02: JpmZZJ6QjL
      03: YTgKKtLWqP
      04: vvFAuJ8W9d
      05: HFLVkWt1Gm
      06: kPjP2pWA6Z
      07: AHiPGRADWa
      08: 1vFmmMM2mZ
      09: BSrpoTxzOg

For status updates, one could use the :py:data:`AppRunner.sig_process` 
Signal. An example with a new printing slot and an updated :py:data:`main`
function is given below:

.. code-block:: 

    def print_progress(progress):
        """Print the current progress repeatedly in the same line."""
        _n_chars = int(60 * progress)
        _txt = (
            "\u2588" * _n_chars
            + "-" * (60 - _n_chars)
            + "|"
            + f" {100*progress:05.2f}%: "
        )
        print(_txt, end='\r', flush=True)

    def main():
        qtapp = QtWidgets.QApplication.instance()
        app = DummyApp()
        runner = pydidas.multiprocessing.AppRunner(app)

        # Now connect the AppRunner's emitted results to our local app:
        runner.sig_results.connect(app.multiprocessing_store_results)

        # Also make sure to terminate the QApplication event loop after
        # finishing the calculations:
        runner.finished.connect(qtapp.quit)
    
        # Connect also the AppRunner.sig_progress to the print_progress
        # function:
        runner.sig_progress.connect(print_progress)

        # Start the runner and the QApplication event loop:
        runner.start()
        qtapp.exec_()

        print('\nResulting random strings:')
        for _key, _val in app.results.items():
            print(f'  {_key:02d}: {_val}')

