.. _generate_workflow_tree:

Generate a WorkflowTree
=======================

Introduction to the WorkflowTree
--------------------------------

The tree consists of py:class:`WorkflowNodes <pydidas.workflow.WorkflowNode>`
which store information about their position in the tree and their parents and
children as well as their associated processing plugin but the nodes are
agnostic to any meta-information.

The :py:class:`WorkflowTree <pydidas.workflow.workflow_tree._WorkflowTree>`
is a pydidas object with only a single running instance. It manages the 
interactions between the user and the individual nodes.

Its instance can be obtained by calling the following code:

.. code-block::

	>>> import pydidas
	>>> TREE = pydidas.workflow.WorkflowTree()
	
Processing with the WorkflowTree is separated in two steps. First, any 
operations which need to be performed only once (i.e. initializations) are 
executed. Second, processing is performed for each data frame at a time. This 
allows to easily run the WorkflowTree in serial or parallel processing. 

Assembling a WorkflowTree
-------------------------

To assemble a ``WorkflowTree``, users need to know which Plugins they want to 
use and they need to configure these plugins. Then, they can add these plugins 
to the tree. If the plugins are passed to the WorkflowTree without any further 
information, they will be connected in a linear manner, with every plugin 
appended to the last one.

Plugins can be configured either in the ``WorkflowTree`` or before adding them 
to the tree. Access to the individual plugins in the tree is somewhat hidded,
though, and it is recommended to configure each ``Plugin`` before adding it to 
the ``WorkflowTree``.

The following example will create a WorkflowTree which loads data from a single
Hdf5 file and performs two separate integrations in different angular ranges:

.. code-block::

	>>> import pydidas
	>>> TREE = pydidas.workflow.WorkflowTree()
	>>> COLLECTION = pydidas.plugins.PluginCollection()
	
	# Create a loader plugin and set the file path
	>>> loader = COLLECTION.get_plugin_by_name('Hdf5singleFileLoader')()
	>>> loader.set_param_value('filename', '/home/someuser/test/file.h5')
	
	# Create an integrator plugin for a specific radial range
	>>> integrator1 = COLLECTION.get_plugin_by_name('PyFAIazimuthalIntegration')()
	>>> integrator1.set_param_value('rad_use_range', True)
	>>> integrator1.set_param_value('rad_npoints', 200)
	>>> integrator1.set_param_value('rad_range_lower', 5.5)
	>>> integrator1.set_param_value('rad_range_upper', 7.5)

	# Create an integrator plugin for a second radial range
	>>> integrator2 = COLLECTION.get_plugin_by_name('PyFAIazimuthalIntegration')()
	>>> integrator2.set_param_value('rad_use_range', True)
	>>> integrator2.set_param_value('rad_npoints', 400)
	>>> integrator2.set_param_value('rad_range_lower', 12.1)
	>>> integrator2.set_param_value('rad_range_upper', 16.1)
	
	# Add the plugins to the WorkflowTree. The return value of the node ID of 
	# the newly added plugin.
	>>> TREE.create_and_add_node(loader)
	0
	>>> TREE.create_and_add_node(integrator1)
	1
	# because plugins will always be attached to the last node, the first 
	# integrator plugin did not need to specify a parent, but the second one 
	# will have to do just that:
	>>> TREE.create_and_add_node(integrator2, parent=0)
	2
