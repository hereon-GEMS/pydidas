..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

The workflow sub-package
========================

The ``workflow`` sub-packages includes classes required for organizing the workflow. These
are essentially classes for nodes which handle a single processing step and for the
workflow tree which organizes the connections between the nodes.

Further sub-packages
--------------------

The ``workflow`` package includes two additional sub-packages:

    1. ``result_io`` includes the required code to save the results of the workflow
    on the fly during processing with various formats.

    2. ``processing_tree_io`` includes the required code to import and export the
    WorkflowTree in different file formats.

Full code documentation
-----------------------

.. toctree::
    :maxdepth: 1

    workflow/workflow
    workflow/result_io
    workflow/processing_tree_io
