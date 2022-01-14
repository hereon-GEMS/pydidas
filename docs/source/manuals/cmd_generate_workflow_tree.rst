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

To assemble a WorkflowTree, users need to know which Plugins they want to use
and they need to configure these plugins. Then, they can add these plugins to 
the tree. If the plugins are passed to the WorkflowTree without any further 
information, they will be connected in a linear manner, with every plugin 
appended to the last one.


