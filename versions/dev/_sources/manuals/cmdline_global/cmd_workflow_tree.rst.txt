..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _workflow_tree:

The WorkflowTree class
======================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Introduction to the WorkflowTree
--------------------------------

The :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`
consists of multipke :py:class:`WorkflowNodes <pydidas.workflow.WorkflowNode>`
which store information about their position in the tree and their parents and
children as well as their associated processing plugin but the nodes are
agnostic to any meta-information.

The :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`
is a pydidas singleton object with only a single instance at runtime. It manages
the interactions between the user and the individual nodes.

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

To assemble a
:py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`, users
need to know which Plugins they want to use and they need to configure these
plugins. Then, they can add these plugins to the tree. If the plugins are
passed to the WorkflowTree without any further information, they will be
connected in a linear manner, with every plugin appended to the last one.

:py:class:`Plugins <pydidas.plugins.BasePlugin>` can be configured either in the
:py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>` or
before adding them to the tree. Access to the individual plugins in the tree
is somewhat hidded, though, and it is recommended to configure each
:py:class:`Plugins <pydidas.plugins.BasePlugin>` before adding it to
the :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`.

To create a new node with a plugin and add it to the
:py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`, use the
:py:meth:`create_and_add_node
<pydidas.workflow.ProcessingTree.create_and_add_node>` method:

.. automethod:: pydidas.workflow.processing_tree.ProcessingTree.create_and_add_node
    :noindex:

The following example will create a WorkflowTree which loads data from a single
Hdf5 file and performs two separate integrations in different angular ranges:

.. code-block::

    >>> import pydidas
    >>> TREE = pydidas.workflow.WorkflowTree()
    >>> COLLECTION = pydidas.plugins.PluginCollection()

    # Create a loader plugin and set the file path
    >>> loader = COLLECTION.get_plugin_by_name('Hdf5FileSeriesLoader')()
    # The configuration of the loader is not detailed here.

    # Create an integrator plugin for a specific radial range
    >>> integrator1 = COLLECTION.get_plugin_by_name('PyFAIazimuthalIntegration')()
    >>> integrator1.set_param_value('rad_use_range', True)
    >>> integrator1.set_param_value('rad_npoint', 200)
    >>> integrator1.set_param_value('rad_range_lower', 5.5)
    >>> integrator1.set_param_value('rad_range_upper', 7.5)

    # Create an integrator plugin for a second radial range
    >>> integrator2 = COLLECTION.get_plugin_by_name('PyFAIazimuthalIntegration')()
    >>> integrator2.set_param_value('rad_use_range', True)
    >>> integrator2.set_param_value('rad_npoint', 400)
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


Running workflows
-----------------

The :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`
includes several methods to run either the full Workflow or just individual
plugins for testing.

Test individual plugins
"""""""""""""""""""""""

To test individual plugins, users can use the :py:meth:`execute_single_plugin
<<pydidas.workflow.ProcessingTree.execute_single_plugin>` method.

.. automethod:: pydidas.workflow.processing_tree.ProcessingTree.execute_single_plugin
    :noindex:

This method will execute a single plugin only. This method can be used to check
intermediate results and make sure that a workflow works as intended.

The following example shows how to use this method to read a frame from an hdf5
file and store it for further processing. (This example assumes that the objects
from the previous example are still existing).

.. code-block::

    >>> res, kws = TREE.execute_single_plugin(0, 0)
    >>> kws
    {}
    >>> res
    Dataset(
    axis_labels: {
        0: "detector y",
        1: "detector x"},
    axis_ranges: {
        0: None
        1: None},
    axis_units: {
        0: "pixel",
        1: "pixel"},
    metadata: {'slicing_axes': [0], 'frame': [0], 'dataset':
       '/entry/data/data'},
    array([[0, 1, 0, ..., 1, 0, 1],
           [0, 0, 1, ..., 2, 0, 0],
           [0, 0, 0, ..., 0, 3, 0],
           ...,
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 1, 1]], dtype=uint32)
    )


Run the full WorkflowTree
"""""""""""""""""""""""""

Two different methods are available to run the full
:py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`. First,
there is the :py:meth:`execute_process
<pydidas.workflow.ProcessingTree.execute_process>` method which
will run the full workflow for a single frame but will not gather any results
from the nodes nor return any values. This method is used by the automatic
processing where pydidas organizes results. Secondly, the
:py:meth:`execute_process_and_get_results
<pydidas.workflow.ProcessingTree.execute_process_and_get_results>`
method will do the same calculations but also gathers the results from the
individual plugins and returns them to the user. The documentation for the
:py:meth:`execute_process_and_get_results
<pydidas.workflow.ProcessingTree.execute_process_and_get_results>`
method is given below.

.. automethod:: pydidas.workflow.ProcessingTree.execute_process_and_get_results
    :noindex:

Using the :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`
from the example above, the following example demonstrates the usage.

.. code-block::

    # This method will not return any results:
    >>> res = TREE.execute_process(0)
    >>> res is None
    True

    # This method will return results:
    >>> res = TREE.execute_process_and_get_results(0)
    >>> res
    {1: Dataset(
     axis_labels: {
         0: '2theta'},
     axis_ranges: {
         0: array([5.505     , 5.51500001, 5.52500001, ...,
                   7.47500088, 7.48500089, 7.49500089])},
     axis_units: {
         0: 'deg'},
     metadata: {},
     array([2.357937 , 2.29853  , 2.3073444, ..., 2.0363004, 2.039918 ,
            2.0199535], dtype=float32)
     ),
     2: Dataset(
     axis_labels: {
         0: '2theta'},
     axis_ranges: {
         0: array([12.105     , 12.11500001, 12.12500001, ...,
                   16.07500191, 16.08500191, 16.09500192])},
     axis_units: {
         0: 'deg'},
     metadata: {},
     array([ 1.4057364,  1.4105228,  1.4086472, ...,  8.046747 , 17.791353 ,
            22.341616 ], dtype=float32)
     )}

To run the workflow for multiple data frames, it is recommended to use the
:py:class:`ExecuteWorkflowApp <pydidas.apps.ExecuteWorkflowApp>`. Please refer
to the :ref:`execute_workflow_app`.
