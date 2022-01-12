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
(:py:class:`ParameterCollections <pydidas.core.ParameterCollection>`).

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

These objects can be accesses