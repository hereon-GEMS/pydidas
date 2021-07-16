Code documentation
==================

This sections lays out the API of the code and is intended as reference for developers.

A fundamental consideration is the separation of GUI and functionality. All computational 
functionality is designed to be accessible from the command line / scripts. (Although the 
GUI does provide some convenience editing methods.)
Some funcionality like file browsing and result visualization requires a GUI and is not
available from the command line.


Module structure
----------------

The module structure is the following (listed in alphabetical order):

* **apps** - The apps are the encapsulated processing programs.

  * *app_utils* - Classes which have been re-factored out of the apps but are used by these.

* **config** - This submodule includes presets (e.g. GUI config) and definitions (e.g. file 
  extension associations)  

* **core** - The core classes which are used throughout the package. These include data structure,
  generic items, and factories.

  * *experimental settings* - Classes for the global experimental settings

* **gui** - The equivalent to *apps* for the graphical user interface. *Frames* encapsulate
  specific functionalities.

  * *builders* - Builder classes for the GUI frames.

* **image_reader** - The factory implementation of the image reader to open image files.

  * *implementations* - Specific implementations for various file formats.

  * *low_level_readers* - Low-level implementations of file readers used by *implementations* (e.g.  
    reading slices out of hdf5 files).

* **multiprocessing** - Tools used for running apps and functions parallely on several
  processes. 

* **plugins** - The plugin library for creating dynamic processing workflows.

* **utils** - Independant utility functions used throughout the module.

* **widgets** - The widgets used in the frames in the GUI. Special *collections* are organized
  as submodules.

  * *dialogues* - User I/O dialogues.

  * *factory* - Widget factory methods

  * *parameter_config* - I/O widgets for Parameter (values).

  * *windows* - Additional stand-alone windows which can be invoked by the main window.

  * *workflow_edit* - Widgets used for creating a dynamic canvas and build workflow trees.

* **workflow_tree** - Classes used for organizing plugin workflows.
  


Key concepts
------------

* **Parameter** - The key data structure used in pydidas is the Parameter. The class documentation
  can be found here: :doc:`Parameter<./code_docs/core/parameter>`.
* **ParameterCollection** - An extended dictionary with Parameter values only. This class is used
  for managing most of the internal data in the pydidas module. Reference:
  :doc:`ParameterCollection<./code_docs/core/parameter_collection>`
  
  
Module documentation
--------------------

.. toctree::
	:maxdepth: 2
	
	code_docs/apps
	code_docs/core
	code_docs/gui