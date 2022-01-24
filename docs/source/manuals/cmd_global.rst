pydidas general command line tutorial
=====================================

Accessing Parameters
--------------------

All pydidas objects handle user variables in the form of 
:py:class:`Parameters <pydidas.core.Parameter>` which enforces type checks where
required. These objects are organized in 
:py:class:`ParameterCollections <pydidas.core.ParameterCollection>` which allow
direct access to the Parameter values. Usually, users do not need to create or 
manage Parameters but only modify their values.

Useful methods
^^^^^^^^^^^^^^

Users will probably manage with a handful of methods. For the full method documentation,
please refer to the class documentation: 
:py:class:`ParameterCollections <pydidas.core.ParameterCollection>`.

	**get_param_keys**()
		Get all the reference keys to access the respective parameters.
	**get_param_value**(*key*)
		Get the value of the Parameter referenced by *key*.
	**get_param_values_as_dict**()
		Get the value of all stored Parameters in form of a dictionary with the 
		Parameter reference keys as dict keys and the Parameter values as dict values.
	**set_param_value**(*key*, *value*)
		Set the value of the Parameter referenced by *key* to the given *value*.

.. tip:: 
	The described methods are universal and apply to all pydidas objects with Parameters.

Examples
^^^^^^^^

All examples will use the ExperimentalSetup object (please see below for a description
of the object) and the examples will only cover the code bases, not the use case. 

First, let us create the object called ``exp``

.. code-block::

	>>> import pydidas
	>>> exp = pydidas.core.ExperimentalSetup()

The object ``exp`` will be used in all examples below.

	1. Get all Parameter keys contained in ``exp``:

		.. code-block::

			>>> exp.get_param_keys()
			['xray_wavelength',
			 'xray_energy',
			 'detector_name',
			 'detector_npixx',
			 'detector_npixy',
			 'detector_sizex',
			 'detector_sizey',
			 'detector_dist',
			 'detector_poni1',
			 'detector_poni2',
			 'detector_rot1',
			 'detector_rot2',
			 'detector_rot3']

	2. Get the value of the Parameter *xray_energy* 

		.. code-block::
		
			>>> exp.get_param_value('xray_energy')
			15.0
			
	3. Get the values of all Parameters as dictionary to process further:

		.. code-block::
		
			>>> params = exp.get_param_values_as_dict()
			>>> params
			{'xray_wavelength': 0.8265613228880018,
			 'xray_energy': 15.0,
			 'detector_name': 'Eiger 9M',
			 'detector_npixx': 3110,
			 'detector_npixy': 3269,
			 'detector_sizex': 7.5e-05,
			 'detector_sizey': 7.5e-05,
			 'detector_dist': 0.23561364873702045,
			 'detector_poni1': 0.11575233539615679,
			 'detector_poni2': 0.12393982882406686,
			 'detector_rot1': -0.007522050071166131,
			 'detector_rot2': -0.004845626736941386,
			 'detector_rot3': 5.799041608456517e-08}
			
	4. Set the value of the *xray_energy* Parameter. This is a float value,
	for demonstration purposes, let us set it with a string first. This will raise
	a ValueError and the Parameter will not be updated.

		.. code-block::

			>>> exp.get_param_value('xray_energy')
			15.0		
			>>> exp.set_param_value('xray_energy', '12.0')
			ValueError: Cannot set Parameter (object ID:2506714567632, 
			refkey: "xray_energy", name: "X-ray energy") because it is of the 
			wrong data type.
			>>> exp.get_param_value('xray_energy')
			15.0		
			>>> exp.set_param_value('xray_energy', 12.0)
			>>> exp.get_param_value('xray_energy')
			12.0		


Global pydidas objects
----------------------

Global objects for processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All apps use the same global persistent objects (implemented as singletons), if
required. Information is separated according to the reasons to change. The three
main objects are:

	ScanSetup
		The details about the scan. This includes crucial information like the
		number of scan dimensions and the number of points in each dimension but
		also metadata like dimension names, units, offsets and step width. The latter
		information can be used to create the correct axis labels in plots.
	ExperimentalSetup
		This object includes information about the global experimental setup like
		X-ray energy, detector type, position and geometry.
	WorkflowTree
		The WorkflowTree holds information about which plugins are used and about
		the order of plugins to be processed. 

These objects can be accesses by calling their respective factories:

.. code-block::

	>>> import pydidas
	>>> SCAN = pydidas.experiment.ScanSetup()
	>>> EXPERIMENT = pydidas.experiment.ExperimentalSetup()
	>>> TREE= pydidas.workflow.WorkflowTree()

Note that the factories return a link to the unique instance and multiple calls yield 
the same object:

.. code-block::

	>>> import pydidas
	>>> SCAN = pydidas.experiment.ScanSetup()
	>>> SCAN
	<pydidas.experiment.scan_setup.scan_setup._ScanSetup at 0x1d4a257b820>
	>>> SCAN2  = pydidas.experiment.ScanSetup()
	>>> SCAN2
	<pydidas.experiment.scan_setup.scan_setup._ScanSetup at 0x1d4a257b820>
	>>> SCAN == SCAN2
	True
	

PluginCollection
^^^^^^^^^^^^^^^^

pydidas uses a global 
:py:class:`PluginCollection <pydidas.plugins.plugin_collection._PluginCollection>` 
to manage all known plugins. Plugins will be discovered based on known plugin paths 
which are managed persistently in the PluginCollection using Qt's QSettings which use 
the systems registry and are platform-independant. A reference to the persistent 
PluginCollection object can be obtained using:

.. code-block::

	>>> import pydidas
	>>> COLLECTION = pydidas.plugins.PluginCollection()

.. note::
	For the full documentation of all available methods, please refer to the class
	documentation:
	:py:class:`PluginCollection <pydidas.plugins.plugin_collection._PluginCollection>` 
	This section handles only the most common use cases.

Management of stores paths
""""""""""""""""""""""""""

Paths can be managed by three methods. New paths can be added using the 
``find_and_register_plugins`` method and a list of all currently registered
paths can be obtained by the ``get_all_registered_paths`` method.
To permanently remove all stored paths, a user can use the ``clear_qsettings`` 
method. To remove all stored paths and plugins from the current instance, use
the ``clear_collection`` method. This method must be called with a ``True`` flag
to take effect and is ignored otherwise.

.. Warning::
	Using the ``clear_qsettings`` method will remove all paths which have ever
	been registered and the user is responsible to add all new paths again.
	
	Also, calling this method will **not** remove known plugins from the current
	instance. If desired, this must be done using the ``clear_collection`` method.

An example of the use of stored paths is given below.

.. code-block::

	>>> import pydidas
	>>> COLLECTION = pydidas.plugins.PluginCollection()
	>>> COLLECTION.get_all_registered_paths()
	['/home/someuser/path/to/plugins']
	>>> COLLECTION.find_and_register_plugins('/home/someuser/another/path', 
	...                                      'home/someuser/yet/another/path')
	>>> COLLECTION.get_all_registered_paths()
	['/home/someuser/path/to/plugins', '/home/someuser/another/path',
	 '/home/someuser/yet/another/path']
	
	# Now, if we exit and restart python, all paths will be included in the 
	# new instance:
	>>> exit()
	$ python
	>>> import pydidas
	>>> COLLECTION = pydidas.plugins.PluginCollection()
	>>> COLLECTION.get_all_registered_paths()
	['/home/someuser/path/to/plugins', '/home/someuser/another/path',
	 '/home/someuser/yet/another/path']
	
	# If we use the ``clear_qsettings`` method, the paths will still exist
	# in the current instance, but will be gone once we restart the kernel:
	>>> COLLECTION.clear_qsettings()
	>>> COLLECTION.get_all_registered_paths()
	['/home/someuser/path/to/plugins', '/home/someuser/another/path',
	 '/home/someuser/yet/another/path']
	>>> exit()
	$ python
	>>> import pydidas
	>>> COLLECTION = pydidas.plugins.PluginCollection()
	>>> COLLECTION.get_all_registered_paths()
	[]
	>>> COLLECTION.find_and_register_plugins('/home/someuser/path/to/plugins', 
	...                                      '/home/someuser/another/path', 
	...                                      '/home/someuser/yet/another/path')
	>>> COLLECTION.get_all_registered_paths()
	['/home/someuser/path/to/plugins', '/home/someuser/another/path',
	 '/home/someuser/yet/another/path']
	
	# Using the ``clear_collection`` method without the confirmation flag 
	# will be ignored:
	>>> COLLECTION.clear_collection()
	'The confirmation flag was not given. The PluginCollection has not been reset.'
	>>> COLLECTION.get_all_registered_paths()
	['/home/someuser/path/to/plugins', '/home/someuser/another/path',
	 '/home/someuser/yet/another/path']
	>>> COLLECTION.clear_collection(True)
	>>> COLLECTION.get_all_registered_paths()
	[]

	# Starting a new instance will restore the paths because the qsettings have
	# not been reset:
	>>> exit()
	$ python
	>>> import pydidas
	>>> COLLECTION = pydidas.plugins.PluginCollection()
	>>> COLLECTION.get_all_registered_paths()
	['/home/someuser/path/to/plugins', '/home/someuser/another/path',
	 '/home/someuser/yet/another/path']
	

Plugin references
"""""""""""""""""

Iternally, plugins are referenced by their class name and there can only be one
plugin registered with the same class name. This behaviour is deliberate to allow
overwriting generic plugins with modified private versions. By default, plugin
references are overridden with a new class if such a class is encountered.
In addition to the class name, each plugin has a ``plugin_name`` attribute which
allows to set a more readable reference name for the Plugin.

.. tip::
	The loading of Plugins occurs in the order of the stored paths. Therefore,
	a path further down in the list will take precedence over an earlier path. 
	The loading of Plugins can be controlled by organizing the sequence of paths.

.. warning::
	Trying to register a second class with a different class name but the same
	plugin name will fail and raise an exception. Both the class name and the 
	plugin name must be unique and a plugin can only replace a plugin with both
	matching class and plugin names or with a similar class name and a different
	plugin name.

Finding and getting a plugin
""""""""""""""""""""""""""""

Plugins can either be found by their class name using the ``get_plugin_by_name``
method or by their plugin name using the ``get_plugin_by_plugin_name`` method.
A list of all available plugin class names can be obtained with the 
``get_all_plugin_names`` method.

.. code-block::
	
	>>> import pydidas
	>>> COLLECTION = pydidas.plugins.PluginCollection()
	>>> COLLECTION.get_all_plugin_names()
	['Hdf5fileSeriesLoader',
	 'Hdf5singleFileLoader',
	 'TiffLoader',
	 'MaskImage',
	 'PyFAI2dIntegration',
	 'PyFAIazimuthalIntegration',
	 'PyFAIradialIntegration',
	 'pyFAIintegrationBase',
	 'BasePlugin',
	 'InputPlugin',
	 'OutputPlugin',
	 'ProcPlugin']
	 
	# Get the plugin class from the collection:
	>>> _plugin = COLLECTION.get_plugin_by_name('PyFAI2dIntegration')
	>>> _plugin
	proc_plugins.pyfai_2d_integration.PyFAI2dIntegration
	
	# Create a new instance:
	>>> _integrate2d = _plugin()
	>>> _integrate2d
	<proc_plugins.pyfai_2d_integration.PyFAI2dIntegration at 0x2132e91a670>
	
	# Get an azimuthal integration plugin by its plugin name and create a 
	# new instance directly (note the additional "()" at the end)
	>>> _azi_int = COLLECTION.get_plugin_by_plugin_name('pyFAI azimuthal Integration')()
	>>> _azi_int
	<proc_plugins.pyfai_azimuthal_integration.PyFAIazimuthalIntegration at 0x2132e9b6ee0>
	
Once the plugins have been created, their Parameters can be modified as described
in the `Accessing Parameters`_ section. The organization of plugins into a WorkflowTree
are covered in the section :ref:`workflow_tree`.