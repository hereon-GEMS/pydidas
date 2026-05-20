..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _hdf5_browser_window:

Hdf5 Browser Window
===================

The Hdf5 browser window allows to explore the internal structure of an HDF5 file.

.. image:: images/hdf5_browser_overview.png
    :align: center

The Hdf5 browser window essentially consists of only one element: A tree view
which displays the tree structure of the HDF5 file. Double clicking on a group
expands or collapses the tree structure for this group.

The ``+`` and ``-`` buttons in the toolbar can be used to expand or collapse all
items recursively from the currently selected item.


.. note::
    The Hdf5 browser window does not allow to plot or explore datasets but only to
    visualize the tree structure of the HDF5 file.

Acknowledgements go to the ESRF silx team. THe Hdf5 browser window is based on parts of
the ``silx.app.view.Viewer.Viewer`` class from the
`silx package <https://github.com/silx-kit/silx>`_.
