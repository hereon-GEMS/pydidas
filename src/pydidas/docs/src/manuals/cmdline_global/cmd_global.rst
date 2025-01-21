..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

pydidas general command line tutorial
=====================================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

.. _accessing_parameters:

Accessing Parameters
--------------------

All pydidas objects handle user variables in the form of
:py:class:`Parameters <pydidas.core.Parameter>` which enforces type checks where
required. These objects are organized in
:py:class:`ParameterCollections <pydidas.core.ParameterCollection>` which allow
direct access to the Parameter values. Usually, users do not need to create or
manage Parameters but only modify their values.

Useful methods of ParameterCollection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the full :py:class:`ParameterCollections <pydidas.core.ParameterCollection>`
method documentation, please refer to the class documentation. However, users
will probably manage with a handful of methods:

    **get_param_keys**\ ()
        Get all the reference keys to access the respective parameters.
    **get_param_value**\ (*key*)
        Get the value of the Parameter referenced by *key*.
    **get_param_values_as_dict**\ ()
        Get the value of all stored Parameters in form of a dictionary with the
        Parameter reference keys as dict keys and the Parameter values as dict
        values.
    **set_param_value**\ (*key*, *value*)
        Set the value of the Parameter referenced by *key* to the given *value*.

.. tip::
    The described methods are universal and apply to all pydidas objects with
    Parameters.

Examples
^^^^^^^^

All examples will use the DiffractionExperimentContext object (please see below for a
description of the object) and the examples will only cover the code bases, not
the use case.

First, let us create the object called :py:data:`exp`

.. code-block::

    >>> import pydidas
    >>> exp = pydidas.contexts.DiffractionExperimentContext()

The object :py:data:`exp` will be used in all examples below.

    1. Get all Parameter keys contained in :py:data:`exp`:

        .. code-block::

            >>> exp.get_param_keys()
            ['xray_wavelength',
             'xray_energy',
             'detector_name',
             'detector_npixx',
             'detector_npixy',
             'detector_pxsizex',
             'detector_pxsizey',
             'detector_mask_file',
             'detector_dist',
             'detector_poni1',
             'detector_poni2',
             'detector_rot1',
             'detector_rot2',
             'detector_rot3']
             
    2. Get the value of the :py:class:`Parameter <pydidas.core.Parameter>`
    *xray_energy*

        .. code-block::

            >>> exp.get_param_value('xray_energy')
            15.0

    3. Get the values of all :py:class:`Parameters <pydidas.core.Parameter>` as
    a dictionary to process further:

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
             'detector_mask_file': Path('.'),
             'detector_dist': 0.23561364873702045,
             'detector_poni1': 0.11575233539615679,
             'detector_poni2': 0.12393982882406686,
             'detector_rot1': -0.007522050071166131,
             'detector_rot2': -0.004845626736941386,
             'detector_rot3': 5.799041608456517e-08}

        .. tip::

            You can also use the :py:data:`param_values` property to retrieve
            all parameter values in a dictionary.

    4. Set the value of the *xray_energy*
    :py:class:`Parameter <pydidas.core.Parameter>`. This is a float value,
    however, the :py:class:`Parameter <pydidas.core.Parameter>` will attempt
    to convert other types to float. If successful,
    for demonstration purposes, let us set it with a string first. This will
    raise a :py:data:ValueError` and the Parameter will not be updated.

        .. code-block::

            >>> exp.get_param_value('xray_energy')
            15.0
            >>> exp.set_param_value('xray_energy', '12.0')
            >>> exp.get_param_value('xray_energy')
            12.0
            >>> exp.set_param_value('xray_energy', 13)
            >>> exp.get_param_value('xray_energy')
            13.0
            >>> exp.set_param_value('xray_energy', "twelve")
            ValueError: Cannot set Parameter (object ID:2129071369296, refkey:
            'xray_energy', name: 'X-ray energy') because it is of the wrong data type.
            (expected: <class 'numbers.Real'>, input type: <class 'str'>
            >>> exp.get_param_value('xray_energy')
            13.0


Global pydidas objects
----------------------

Global objects for processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All apps use the same global persistent objects (implemented as singletons), if
required. Information is separated according to the reasons to change. The three
main objects are:

    :py:class:`ScanContext <pydidas.contexts.scan.Scan>`
        The details about the scan. This includes generic information like scan
        title, data directory and scan names and specific information like the
        number of scan dimensions and the number of points in each dimension
        (but also metadata like dimension names, units, offsets and step width).
        The latter information can be used to create the correct axis labels in
        plots. For the full documentation please visit the
        :ref:`ScanSetup manual <scan_context>`.
    :py:class:`DiffractionExperimentContext <pydidas.contexts.diff_exp.DiffractionExperiment>`
        This object includes information about the global experimental setup
        like X-ray energy, detector type, position and geometry. For the full
        documentation please visit the
        :ref:`DiffractionExperimentContext manual <diffraction_exp_context>`.
    :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`
        The WorkflowTree holds information about which plugins are used and
        about the order of plugins to be processed. For the full documentation
        please visit the :ref:`WorkflowTree manual <workflow_tree>`.

These objects can be accesses by calling their respective factories:

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.contexts.ScanContext()
    >>> EXPERIMENT = pydidas.contexts.DiffractionExperimentContext()
    >>> TREE = pydidas.workflow.WorkflowTree()

Note that the factories return a link to the unique instance and multiple calls
yield the same object:

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.contexts.ScanContext()
    >>> SCAN
    <pydidas.contexts.scan.Scan at 0x1d4a257b820>
    >>> SCAN2 = pydidas.contexts.ScanContext()
    >>> SCAN2
    <pydidas.contexts.scan.Scan at 0x1d4a257b820>
    >>> SCAN == SCAN2
    True

.. _global_plugincollection:

PluginCollection
^^^^^^^^^^^^^^^^

pydidas uses a global
:py:class:`PluginCollection <pydidas.plugins.plugin_collection.PluginRegistry>`
to manage all known plugins. Plugins will be discovered based on known plugin
paths which are managed persistently in the PluginCollection using Qt's
QSettings which use the systems registry and are platform-independent. A
reference to the persistent :py:class:`PluginCollection
<pydidas.plugins.plugin_collection.PluginRegistry>` object can be obtained
using:

.. code-block::

    >>> import pydidas
    >>> COLLECTION = pydidas.plugins.PluginCollection()

.. note::
    For the full documentation of all available methods, please refer to the
    class documentation:
    :py:class:`PluginCollection <pydidas.plugins.plugin_collection.PluginRegistry>`
    This section handles only the most common use cases.

Management of stored paths
""""""""""""""""""""""""""

Paths can be managed by various methods. New paths can be added using the
:py:meth:`find_and_register_plugins
<pydidas.plugins.plugin_collection.PluginRegistry.find_and_register_plugins>`
method and a list of all currently registered paths can be obtained by the
:py:meth:`get_all_registered_paths
<pydidas.plugins.plugin_collection.PluginRegistry.get_all_registered_paths>`
method. To permanently remove a stored paths, a user can use the
:py:meth:`unregister_plugin_path
<pydidas.plugins.plugin_collection.PluginRegistry.unregister_plugin_path>`
method. To remove all stored paths and plugin, use
the :py:meth:`unregister_all_paths
<pydidas.plugins.plugin_collection.PluginRegistry.unregister_all_paths>` method.
This method must be called with a :py:data:`True` flag to take effect and is
ignored otherwise.


.. note::
    Note that the generic plugin path is always included and cannot be removed from
    the collection by the user.

.. Warning::
    Using the :py:meth:`unregister_all_paths
    <pydidas.plugins.plugin_collection.PluginRegistry.unregister_all_paths>`
    method will remove all custom paths which have ever been registered and the
    user is responsible to add all required paths again.

    This method will not keep any references to the original stored paths and they
    are truly lost.

An example of the use of stored paths is given below.

.. code-block::

    >>> import pydidas
    >>> COLLECTION = pydidas.plugins.PluginCollection()
    >>> COLLECTION.registered_paths
    [Path(''/home/someuser/path/to/plugins')]
    >>> COLLECTION.find_and_register_plugins(
        '/home/someuser/another/path',
        'home/someuser/yet/another/path')
    >>> COLLECTION.registered_paths
    [Path('/home/someuser/path/to/plugins'), 
     Path('/home/someuser/another/path'),
     Path('/home/someuser/yet/another/path')]

    # Now, if we exit and restart python, all paths will be included in the
    # new instance:
    >>> exit()
    $ python
    >>> import pydidas
    >>> COLLECTION = pydidas.plugins.PluginCollection()
    >>> COLLECTION.registered_paths
    [Path('/home/someuser/path/to/plugins'), 
     Path('/home/someuser/another/path'),
     Path(''/home/someuser/yet/another/path')]
    # Using the ``unregister_plugin_path`` method allows to remove a single path:
    >>> COLLECTION.unregister_plugin_path(Path('/home/someuser/another/path'))
    >>> COLLECTION.registered_paths
    [Path('/home/someuser/path/to/plugins'),
     Path(''/home/someuser/yet/another/path')]
    # Using the ``unregister_all_paths`` method without the confirmation flag
    # will be ignored:
    >>> COLLECTION.unregister_all_paths()
    'Confirmation for unregistering all paths was not given. Aborting...'
    >>> COLLECTION.registered_paths
    [Path('/home/someuser/path/to/plugins'), 
     Path('/home/someuser/yet/another/path')]
    >>> COLLECTION.unregister_all_paths(True)
    >>> COLLECTION.registered_paths
    []


Plugin references
"""""""""""""""""

Internally, plugins are referenced by their class name and there can only be one
plugin registered with the same class name. This behaviour is deliberate to
allow overwriting generic plugins with modified private versions. By default,
plugin references are overridden with a new class if such a class is
encountered. In addition to the class name, each plugin has a
:py:data:`plugin_name` attribute which allows to set a more readable reference
name for the Plugin.

.. tip::
    The loading of Plugins occurs in the order of the stored paths. Therefore,
    a path further down in the list will take precedence over an earlier path.
    The loading of Plugins can be controlled by organizing the sequence
    of paths.

    The generic plugins are always loaded first.

.. warning::
    Trying to register a second class with a different class name but the same
    plugin name will fail and raise an exception. Both the class name and the
    plugin name must be unique and a plugin can only replace a plugin with both
    matching class and plugin names or with a similar class name and a different
    plugin name.

Finding and getting a plugin
""""""""""""""""""""""""""""

Plugins can either be found by their class name using the
:py:meth:`get_plugin_by_name
<pydidas.plugins.plugin_collection.PluginRegistry.get_plugin_by_name>`
method or by their plugin name using the
:py:meth:`get_plugin_by_plugin_name
<pydidas.plugins.plugin_collection.PluginRegistry.get_plugin_by_plugin_name>`
method. A list of all available plugin class names can be obtained with the
:py:meth:`get_all_plugin_names
<pydidas.plugins.plugin_collection.PluginRegistry.get_all_plugin_names>`
method.

.. code-block::

    >>> import pydidas
    >>> COLLECTION = pydidas.plugins.PluginCollection()
    >>> COLLECTION.get_all_plugin_names()
    ['Hdf5fileSeriesLoader',
     'FrameLoader',
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

Once the plugins have been created, their Parameters can be modified as
described in the `Accessing Parameters`_ section. The organization of plugins
into a WorkflowTree are covered in the section :ref:`WorkflowTree manual
<workflow_tree>`.

.. _pydidas_qsettings:

pydidas QSettings
-----------------

pydidas uses Qt's QSettings to store persistent information in the system's
registry. The :py:class:`pydidas.core.PydidasQsettings` class can be used to
display and modify global parameters.
The most useful methods for general users are
:py:meth:`show_all_stored_q_settings
<pydidas.core.PydidasQsettings.show_all_stored_q_settings>`
to print the names and values of all stored settings and
:py:meth:`set_value <pydidas.core.PydidasQsettings.set_value>` to modify a key.

.. code-block::

    >>> import pydidas
    >>> config = pydidas.core.PydidasQsettings()
    >>> config.show_all_stored_q_settings()
    global/mp_n_workers: 4
    global/plot_update_time: 1
    global/shared_buffer_max_n: 20
    global/shared_buffer_size: 100
    >>> config.set_value('global/shared_buffer_size', 50)
    >>> config.show_all_stored_q_settings()
    global/mp_n_workers: 4
    global/plot_update_time: 1
    global/shared_buffer_max_n: 20
    global/shared_buffer_size: 50

Note that the full list of global keys is longer and only a subset is presented
here for demonstration purposes.

.. note::

    The Qsettings are persistent (for a specific pydidas version) on the system
    for every individual user account, i.e. any changes you make will persist
    if you start a new pydidas instance or process. Likewise, any changes made
    as a different user will not be applied to your settings.

Description of pydidas's Qsettings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: ../global/pydidas_qsettings.rst
