..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _developer_guide_to_apps:

Developers guide to pydidas applications
========================================

All pydidas applications should inherit from the :py:class:`BaseApp
<pydidas.core.BaseApp>` class.

Generic attributes and methods
------------------------------

Class attributes
^^^^^^^^^^^^^^^^

.. list-table::
    :widths: 30 70
    :header-rows: 1
    :class: tight-table

    * - class attribute
      - description
    * - :py:data:`default_params`
      - A pydidas :py:class:`ParameterCollection
        <pydidas.core.ParameterCollection>` which define the
        :py:class:`Parameters <pydidas.core.Parameter>` required to use the app.
    * - :py:data:`parse_func`
      - The function used to parse command line arguments to starting Parameter
        values.
    * - :py:data:`attributes_not_to_copy_to_app_clone`
      - A list with the names of instance attributes which must not be copied
        to an app clone. This is relevant for using the AppRunner for parallel
        processing, where it should be avoided to copy large objects because
        of the serialization of all objects during pickling.

Instance attributes
^^^^^^^^^^^^^^^^^^^

.. list-table::
    :widths: 20 80
    :header-rows: 1
    :class: tight-table

    * - instance attribute
      - description
    * - :py:data:`app_clone`
      - A boolean flag to toggle whether the current app instance is a manager
        or clone.
    * - :py:data:`_config`
      - The :py:data:`_config` dictionary should be used to store all app
        configuration which is not directly controlled by a Parameter. The
        :py:data:`_config` is saved in the app state for export / import.
    * - :py:data:`params`
      - The :py:class:`ParameterCollection <pydidas.core.ParameterCollection>`
        instance for the app. It should be accessed indirectly through the
        control methods for Parameters :py:class:`ObjectWithParameterCollection
        <pydidas.core.ObjectWithParameterCollection>`.

Generic methods
^^^^^^^^^^^^^^^

This list gives a short description for all generic methods. For details like
return values and calling parameters, please refer to the class documentation:
:py:class:`BaseApp <pydidas.core.BaseApp>`.

.. list-table::
    :widths: 20 80
    :header-rows: 1
    :class: tight-table

    * - method names
      - description
    * - :py:data:`run`
      - Run the app's task list serially in the present process. Note that this
        will freeze the process and may take a lot of time, depending on the
        number of tasks and the processing steps.
    * - :py:data:`multiprocessing_get_tasks`
      - This method must return all the tasks (as an iterable object) defined
        in the app. The app configuration should be done using Parameters and
        this method process the input from all Parameters to create the task
        list. **This method must be defined in a custom app.**
    * - :py:data:`multiprocessing_pre_run`
      - This method runs all the required initialization which needs to be
        performed once before processing tasks. By default, this method
        passes.
    * - :py:data:`multiprocessing_post_run`
      - Final processing which needs to be performed after all tasks have been
        completed. By default, this method passes.
    * - :py:data:`multiprocessing_pre_cycle`
      - This method is called once before each task is performed. By default,
        this method passes.
    * - :py:data:`multiprocessing_carryon`
      - This method allows to check whether processing can carry on or needs to
        wait (for example for new data). It is called after the pre_cycle and
        is called repeatedly until it returns a True. By default, this method
        returns True.
    * - :py:data:`multiprocessing_func`
      - This is the core processing function in which the computation for each
        task should be defined. **This method must be defined in a custom app.**
    * - :py:data:`multiprocessing_store_results`
      - This method takes the task index and the function results and stores
        them in whichever way the app defined. It is separated from the
        processing to separate it in parallel processing and only store the
        results in the main process. **This method must be defined in a
        custom app.**
    * - :py:data:`initialize_shared_memory`
      - This method is used to create shared memory objects to be shared between
        manager and app clones or it initialize it again. Details must be defined
        by the app which wishes to use it.
    * - :py:data:`export_state`
      - This method returns a dictionary with the app state in a serializable
        format, i.e. all entries are safe to process in YAML or pickle.
    * - :py:data:`import_state`
      - This method takes a state dictionary and restores the app to its
        previous state.

Creating an app instance
------------------------

An app instance can be created as any generic python object by calling its
class:

.. code-block::

    import pydidas

    class RandomImageGeneratorApp(pydidas.core.BaseApp):
    default_params = ParameterCollection(
        Parameter("num_images", int, 50),
        Parameter("image_shape", tuple, (100, 100)),
    )

    app = RandomImageGeneratorApp()

All pydidas apps can be configured at creation in one of three ways:

    1. By specifrying the :py:data:`parse_func` and using the python argparse
    package and sys.argv:

    .. code-block::

        def app_param_parser(caller=None):
            parser = argparse.ArgumentParser()
            parser.add_argument("-num_images", "-n", help="The number of images")
            parser.add_argument("-image_shape", "-i", help="The image size")
            _input, _unknown = parser.parse_known_args()
            _args = dict(vars(_input))
            if _args["num_images"] is not None:
                _args["num_images"] = int(_args["num_images"])
            if _args["image_shape"] is not None:
                _args["image_shape"] = tuple(
                    [int(entry) for entry in _args["image_shape"].strip("()").split(",")]
                )
            return _args

        class RandomImageGeneratorApp(pydidas.core.BaseApp):
            default_params = ParameterCollection(
                Parameter("num_images", int, 50),
                Parameter("image_shape", tuple, (100, 100)),
            )
            parse_func = app_param_parser

    With the default sys.argv, the app will initialize with the default values.
    When the sys.argv arguments have been set, the app will initialize with
    those:

    .. code-block::

        >>> import sys
        >>> app = RandomImageGeneratorApp()
        >>> app.get_param_values_as_dict()
        {'num_images': 50, 'image_shape': (100, 100)}
        >>> sys.argv.extend(["-num_images", "30", "-image_shape", "(25, 50)"])
        >>> app2 = RandomImageGeneratorApp()
        >>> app2.get_param_values_as_dict()
        {'num_images': 30, 'image_shape': (25, 50)}

    2. By passing the values for the Parameters as keyword arguments. Without
    any keywords, Parameters are created with their default values (see code
    block above). Giving the Parameter refkeys as keywords, it is possible to
    update the Parameter values directly at creation:

    .. code-block::

        >>> app = RandomImageGeneratorApp()
        >>> app.get_param_values_as_dict()
        {'num_images': 50, 'image_shape': (100, 100)}
        >>> app = RandomImageGeneratorApp(num_images=20, image_shape=(20, 20))
        >>> app.get_param_values_as_dict()
        {'num_images': 20, 'image_shape': (20, 20)}

    3. By sharing Parameters with other objects. One of the key advantages of
    using pydidas Parameter for handling app data is that they are objects
    which can be shared between different python objects. Any changes to the
    object will be directly available to all linked apps:

    .. code-block::

        >>> app_1 = RandomImageGeneratorApp()
        >>> num_param = app_1.get_param("num_images")
        >>> app_2 = RandomImageGeneratorApp(num_param)
        >>> id(app_1.get_param("num_images"))
        2638563877360
        >>> id(app_2.get_param("num_images"))
        2638563877360
        >>> print(
        >>>     "Num images: ",
        >>>     app_1.get_param_value("num_images"),
        >>>     app_2.get_param_value("num_images"),
        >>> )
        Num images:  50 50
        >>> app_1.set_param_value("num_images", 30)
        >>> print(
        >>>     "Num images: ",
        >>>     app_1.get_param_value("num_images"),
        >>>     app_2.get_param_value("num_images"),
        >>> )
        Num images:  30 30

.. note::

    The order of precedence (from lowest to highest) is:

        - shared Parameters
        - keyword arguments at creation
        - parsed sys.argv arguments

    This allows the user to set presets in scripts but still change the
    behaviour dynamically by changing calling arguments on the command line.


Running an app
--------------

The app can be run locally (and serially) using the :py:meth:`run` method.
The run method's definition is given below to demonstrate the exact sequence:

.. code-block::

    def run(self):
        """
        Run the app without multiprocessing.
        """
        self.multiprocessing_pre_run()
        tasks = self.multiprocessing_get_tasks()
        for task in tasks:
            self.multiprocessing_pre_cycle(task)
            _carryon = self.multiprocessing_carryon()
            if _carryon:
                _results = self.multiprocessing_func(task)
                self.multiprocessing_store_results(task, _results)
        self.multiprocessing_post_run()


To run an app with parallelization or simple in the background, please refer to
:ref:`developer_guide_to_multiprocessing`\ .


Example
-------

As example, let us extend the RandomImageGeneratorApp to a fully functional app.
The app will create a random noisy image of the given shape as its core
function.
It will utilize a shared memory array to store results to demonstrate how
manager and app clones interact in multiprocessing.
Just for demonstration purposes, it will wait for 50 ms for every 5th index
and fail every 2nd carryon check. These methods will also print some info for
demonstration:

.. code-block::

    import time
    import argparse
    import multiprocessing as mp

    import numpy as np

    import pydidas
    from pydidas.core import Parameter, ParameterCollection


    def app_param_parser(caller=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("-num_images", "-n", help="The number of images")
        parser.add_argument("-image_shape", "-i", help="The image size")
        _input, _unknown = parser.parse_known_args()
        _args = dict(vars(_input))
        if _args["num_images"] is not None:
            _args["num_images"] = int(_args["num_images"])
        if _args["image_shape"] is not None:
            _args["image_shape"] = tuple(
                [int(entry) for entry in _args["image_shape"].strip("()").split(",")]
            )
        return _args


    class RandomImageGeneratorApp(pydidas.core.BaseApp):
        default_params = ParameterCollection(
            Parameter("num_images", int, 50),
            Parameter("image_shape", tuple, (100, 100)),
        )
        attributes_not_to_copy_to_app_clone = ["shared_array", "shared_index_in_use", "_tasks"]
        parse_func = app_param_parser

        def __init__(self, *args, **kwargs):
            pydidas.core.BaseApp.__init__(self, *args, **kwargs)
            self._config["buffer_n"] = 20
            self._config["shared_memory"] = {}
            self._config["carryon_counter"] = 0
            self.shared_array = None
            self.shared_index_in_use = None
            self.results = None

        def multiprocessing_pre_run(self):
            """
            Perform operations prior to running main parallel processing function.
            """
            self._tasks = np.arange(self.get_param_value("num_images"))
            # only the manager must initialize the shared memory, the clones are passed
            # the reference:
            if not self.clone_mode:
                self.initialize_shared_memory()
            # create the shared arrays:
            self.shared_index_in_use = np.frombuffer(
                self._config["shared_memory"]["flag"].get_obj(), dtype=np.int32
            )
            self.shared_array = np.frombuffer(
                self._config["shared_memory"]["data"].get_obj(), dtype=np.float32
            ).reshape((self._config["buffer_n"],) + self.get_param_value("image_shape"))
            self.results = np.zeros(
                (self._tasks.size,) + self.get_param_value("image_shape")
            )

        def initialize_shared_memory(self):
            _n = self._config["buffer_n"]
            _num = int(
                self._config["buffer_n"] * np.prod(self.get_param_value("image_shape"))
            )
            self._config["shared_memory"]["flag"] = mp.Array("I", _n, lock=mp.Lock())
            self._config["shared_memory"]["data"] = mp.Array("f", _num, lock=mp.Lock())

        def multiprocessing_get_tasks(self):
            return self._tasks

        def multiprocessing_pre_cycle(self, index):
            """
            Sleep for 50 ms for every 5th task.
            """
            print("\nProcessing task ", index)
            if index % 5 == 0:
                print("Index divisible by 5, sleeping ...")
                time.sleep(0.05)
            return

        def multiprocessing_carryon(self):
            """
            Count up and carry on only for every second call.
            """
            self._config["carryon_counter"] += 1
            _carryon = self._config["carryon_counter"] % 2 == 0
            print("Carry on check: ", _carryon)
            return _carryon

        def multiprocessing_func(self, index):
            """
            Create a random image and store it in the buffer.
            """
            _shape = self.get_param_value("image_shape")
            # now, acquire the lock for the shared array and find the first empty
            # buffer position and write the image to it:
            _index_lock = self._config["shared_memory"]["flag"]
            while True:
                _index_lock.acquire()
                _zeros = np.where(self.shared_index_in_use == 0)[0]
                if _zeros.size > 0:
                    _buffer_pos = _zeros[0]
                    self.shared_index_in_use[_buffer_pos] = 1
                    break
                _index_lock.release()
                time.sleep(0.01)
            self.shared_array[_buffer_pos] = np.random.random(_shape).astype(np.float32)
            _index_lock.release()
            return _buffer_pos

        def multiprocessing_store_results(self, task_index, buffer_index):
            _index_lock = self._config["shared_memory"]["flag"]
            _index_lock.acquire()
            self.results[task_index] = self.shared_array[buffer_index]
            self.shared_index_in_use[buffer_index] = 0
            _index_lock.release()

This app is fully functional and can be used for testing. Running it will fill
the app's :py:data:`results` attribute with random images:

.. code-block::

    >>> app = RandomImageGeneratorApp()
    >>> app.run()
    Processing task  0
    Index divisible by 5, sleeping ...
    Carry on check:  False
    Carry on check:  True

    Processing task  1
    Carry on check:  False
    Carry on check:  True

    Processing task  2
    Carry on check:  False
    Carry on check:  True

    [...]

    >>> np.where(app.results == 0)
     (array([], dtype=int64), array([], dtype=int64), array([], dtype=int64))

Using the app's shared memory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use the app's shared memory, we only need to create a copy of the app (in the
clone mode). This will allow the two apps to use the joint shared memory:

.. code-block::

    >>> app = RandomImageGeneratorApp()
    >>> app.multiprocessing_pre_run()
    >>> app_clone = app.copy(clone_mode=True)
    >>> app_clone.multiprocessing_pre_run()
    >>> index = 10
    >>> buffer_index = app_clone.multiprocessing_func(index)
    >>> # The first buffer has now been used:
    >>> app.shared_index_in_use
    array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    >>> # now, the data from the clone is stored in the shared array and
    >>> # also accessible by the manager app:
    >>> app.shared_array[buffer_index, 0, 0:5]
    array([0.09039891, 0.7184127 , 0.46342215, 0.34047562, 0.18884952],
      dtype=float32)
    >>> app_clone.shared_array[buffer_index, 0, 0:5]
    array([0.09039891, 0.7184127 , 0.46342215, 0.34047562, 0.18884952],
      dtype=float32)
    >>> # we can now get the results from the shared buffer and store them
    >>> # in the app properly:
    >>> app.multiprocessing_store_results(index, buffer_index)
    >>> app.results[index, 0, 0:5]
    array([0.09039891, 0.7184127 , 0.46342215, 0.34047562, 0.18884952],
      dtype=float32)
