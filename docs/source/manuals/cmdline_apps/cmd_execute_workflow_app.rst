.. _execute_workflow_app:

Tutorial for the ExecuteWorkflowApp
===================================

Motivation
----------

The :py:class:`ExecuteWorkflowApp <pydidas.apps.ExecuteWorkflowApp>` is one of 
the most important objects in pydidas as it allows to process workflows. Note 
that most of the configuration is not performed by the ExecuteWorkflowApp itself
but by the global objects for 
:py:class:`ScanSetup <pydidas.experiment.scan_setup.scan_setup._ScanSetup>`,
:py:class:`ExperimentalSetup <pydidas.experiment.scan_setup.scan_setup._ExperimentalSetup>`,
and :py:class:`WorkflowTree <pydidas.workflow.workflow_tree._WorkflowTree>`.

Documentation on the use of these objects is given in :ref:`scan_setup`,
:ref:`experimental_setup` and :ref:`workflow_tree`, respectively.

Globally controlled settings
----------------------------

Some settings used by the ExecuteWorkflowApp are controlled globally by pydidas. 
These are:

- The file path for the global mask file (`global/det_mask`)

and for parallel processing additionally:

- The number of parallel worker processes (`global/mp_n_workers`)
- The size of the data exchange buffer (in MB) (`global/shared_buffer_size`)
- The number of datasets which can be held in the buffer (`global/shared_buffer_max_n`)



