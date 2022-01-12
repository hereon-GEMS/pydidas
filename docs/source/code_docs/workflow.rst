The workflow sub-package
========================

The ``workflow`` sub-packages includes classes required for organizing the workflow. These
are essentially classes for nodes which handle a single processing step and for the 
workflow tree which organizes the connections between the nodes. 

Further sub-packages
--------------------

The ``workflow`` package includes two additional sub-packages:

	1. ``result_savers`` includes the required code to save the results of the workflow
	on the fly during processing with various formats.
	
	2. ``workflow_tree_io`` includes the required code to import and export the 
	WorkflowTree in different file formats.

Full code documentation
-----------------------

.. toctree::
	:maxdepth: 1
	
	workflow/workflow
	workflow/result_savers
	workflow/workflow_tree_io

