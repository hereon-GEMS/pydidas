Command line manuals
====================

pydidas can be started from any python console (iPython, jupyter, console in 
a development environment) and is dependant on a number of other modules which
should have been installed automatically by anaconda.

These apps are available from the command line:

	CompositeCreatorApp
		An application that allows to create a composite image by stitching
		diffraction images (or parts of them) into a new composite image.
		Images can be rebinned or cropped and thresholds can be applied 
		prior to merging them.
	
	ExecuteWorkflowApp
		An application which allows to run workflows (which have to have been 
		defined by the user). Workflows can be reused and only the data source
		needs to be updated (i.e. the filenames and/or directories).
		Workflows themselves are organized as plugins 
		

The following manuals are available:

.. toctree::
	:maxdepth: 1
	
	cmd_global
	cmd_workflow_tree
	cmd_composite_creator_app
	cmd_execute_workflow_app
	


