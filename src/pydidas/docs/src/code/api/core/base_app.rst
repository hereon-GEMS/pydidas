..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. |class_name| replace:: BaseApp

|class_name|
============

The BaseApp includes the structure that all applications must adhere to
for allowing them to run in the :py:class:`AppRunner <pydidas.multiprocessing.AppRunner>`.

The basic functions in Apps are used as follows:

#. Call app.multiprocessing_pre_run to perform general setup tasks
   for multiprocessing. This method should only be called once because
   it might be expensive to run.

#. Run a loop \<for index in tasks\>:

    #. Check app.multiprocessing_carryon value. If False, wait and
       repeat the check. If True, continue with processing.
    
    #. Call app.multiprocessing_func(index) to perform the main
       calculation task and put the results in a queue or transfer
       via a signal.
    
    #. Call app.multiprocessing_store_results (optionally). If the apps
       are running in parallel, they will skip this step and instead,
       they will send the results via queue to the AppRunner.

#. Call app.multiprocessing_post_run to perform cleanup steps.

* |class_name| documentation :ref:`with own methods only<own_methods_BaseApp>`
* |class_name| documentation :ref:`with inherited methods too<all_methods_BaseApp>`

.. _own_methods_BaseApp:

|class_name| with own methods only
----------------------------------

.. autoclass:: pydidas.core.BaseApp
    :members:
    :show-inheritance:

.. _all_methods_BaseApp:

|class_name| with inherited methods too
---------------------------------------

.. autoclass:: pydidas.core.BaseApp
    :members:
    :show-inheritance:
    :noindex:
    :inherited-members: QObject
    

