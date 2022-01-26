Running pydidas applications
============================

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

As an example, let us use a ``DummyApp`` which creates a list with random 
strings and takes two parameters for the length of each string and the total
number of strings.

.. note::

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

To run an app serially, simply call the ``run`` method of the app. Note that 
this will be a blocking call until the application is finished with its 
processing. 

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

To run an application using parallel processing, an additional object is needed
to control the parallelization. This is the 
:py:class:`AppRunner <pydidas.multiprocessing.AppRunner>`. Usage is 
straightforward and happens through only a few commands. The AppRunner starts
in a separate thread and is non-blocking. It launches multiple independent
processes and can run in the background.

.. note::

    For a detailed description of how the pydidas multiprocessing works,
    please refer to the :ref:`multiprocessing_package` or to the 
	:ref:`developer_guide_to_multiprocessing`.

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

.. code-block::
	
	# Set up the app:
	>>> import pydidas
	>>> app = pydidas.apps.DummyApp()
	>>> app
	<pydidas.apps.dummy_app.DummyApp at 0x1c23aed0ee0>
	>>> app.set_param_value('number_of_strings', 10)
	>>> app.set_param_value('length_of_string', 10)
	
	# Define the AppRunner
	>>> runner = pydidas.multiprocessing.AppRunner(app)
	
	# Checking the progress now will yield a -1 because the AppRunner has not 
	# yet queried the app for the tasks
	>>> runner.progress
	-1
	
	# If we change an app parameter in the runner, the local instance will not
	# be modified:
	>>> runner.set_app_param('length_of_string', 20)
	>>> app.get_param('length_of_string')
	Parameter <length_of_string (type: Integral): 10 (default: 5)>
	
	# If we start the runner and query the progress immediately, it will yield
	# zero:
	>>> runner.start()
	>>> runner.progress
	0
	
	# To check, whether the runner is finished, check that progress is equal
	# to one:
	>>> runner.progress
	1
	
	# Now, we need to get the runner's update app back into the local namespace
	# to access it directly. 
	>>> app = runner.get_app()
	>>> app
	<pydidas.apps.dummy_app.DummyApp at 0x1c246465e50>
	app.get_param_values_as_dict()
	{'number_of_strings': 10,
	 'length_of_string': 20}
	>>> app.get_results()
	['HynGtTMzELIGpxKUjsmv',
	 'vHpcpwnqbVbpbnDKIOnf',
	 'RFQvZvqotYCMpityIHGk',
	 'MIXWNdsbLbFDxNDRQnjA',
	 'sKbWVcxyRbTrEAvSNyfp',
	 'PUaRVxJiCEjfeiCozoHN',
	 'zByPTNALcybfXkDTyXPL',
	 'LaBUIxLkWBTBdcSkDrct',
	 'nWUnyMWHxHEXJxalOjcX',
	 'tpAYNIMIUhymdzyDOmLJ']
	
.. note::
	
	This is a very basic example and multiprocessing can be performed more
	elegantly by using Qt's signal and slot system which is used by pydidas.
	For a full description of the signals, please refer to the 
	:ref:`developer_guide_to_signals`.

