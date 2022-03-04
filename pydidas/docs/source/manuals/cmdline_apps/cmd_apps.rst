Command line applications
=========================

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
        
    DirectorySpyApp
        An application which allows to scan a directory for new files - either
        all new files or files which match a filename pattern. This app keeps
        the latest filename and image data available for the user to process
        further.

The following manuals are available:

.. toctree::
    :maxdepth: 1
    
    running_apps
    cmd_composite_creator_app
    cmd_execute_workflow_app
    cmd_directory_spy_app
