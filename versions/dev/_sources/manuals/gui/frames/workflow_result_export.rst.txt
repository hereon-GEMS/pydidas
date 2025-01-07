..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. image:: images/results_export.png
    :align: left

The data export section allows users to export results either for the current
node or for all nodes. The current node is the selected node for visualization.

.. note::

    The export will always export the full node dataset, not just the subset 
    which has been selected for display.
    
The first Parameter allows to select the export format(s). The second Parameter
controls overwriting of results. If True, existing data files will be 
overwritten without any additional warning. If False and an existing file is
detected, an Exception will be raised.

Clicking either the "Export current node results" or the "Export all results"
button will open a dialogue to select the folder.

.. note::

    To achieve naming consistency, it is not possible for the user to change
    the filenames of exported data, only the directory.