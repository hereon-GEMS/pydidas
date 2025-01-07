..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Command line applications
=========================

This section includes a generic manual for running apps from the command line
as well as specific application manuals for generic pydidas apps.

These apps are available in pydidas:

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

    cmd_running_apps
    cmd_composite_creator_app
    cmd_execute_workflow_app
    cmd_directory_spy_app
