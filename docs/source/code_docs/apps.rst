The apps submodule
==================

The apps are the encapsulated processing programs. They can be run from the GUI or command line.
For the graphical user interface, the framework will organize argument passing from the input fields.
For the command line, arguments can be either passed aa keywords during initialization, as command
line arguments or by updating the Parameter values of the app class in scripts.

.. toctree::
	:maxdepth: 4
	
	apps/base_app
	apps/composite_creator_app
	apps/app_utils/filelist_manager
	apps/app_utils/image_metadata_manager
