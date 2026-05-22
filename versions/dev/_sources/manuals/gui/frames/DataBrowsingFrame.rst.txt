..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _data_browsing_frame:

Data browsing frame
===================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

The data browsing frame allows the visualization of one-dimensional and
two-dimensional data. The frame is divided in two main parts: On the left, a
directory explorer allows to browse the full file system and select files. On
the right side, a data display allows to visualize data.

**Files are selected by double-clicking on the respective file in the directory.**
For raw images, an additional selection widget to specify the data settings will
be shown. Similarly, for hdf5 files, an additional selection widget to select
the dataset in the file will be shown.

.. image::  images/data_browse/overview.png
    :width: 580px
    :align: center

In the screenshot above, the data display is empty as no data has been selected.
An example will be shown in the following sections.

The width of the directory explorer widget can be adjusted by using the dark
grey handle between the two main widgets, to reduce or to enlarge the directory
explorer, respectively. The draggable handle is highlighted with the green frame
in the screenshot above.

.. warning::

    The two main widgets have a defined minimum size. If the user drags the
    splitter further, the respective widget will be hidden. It can be enlarged
    again by capturing and dragging the dark slider from the edge towards the
    center.

Controls
^^^^^^^^

The controls are located on the left, above the directory explorer.

Browsing options header
"""""""""""""""""""""""

.. image:: images/data_browse/options.png
    :width: 297 px
    :align: right

At the very top of the left panel, a bold **Data browsing options** header is
shown next to a toggle button labelled *Hide browsing options* /
*Show browsing options*. Clicking this button collapses or expands the entire
browsing-options section, leaving only the *Current directory* field and the
filter row visible. This is useful to maximise the vertical space for the
directory tree when the options do not need to be changed.


Browsing options
""""""""""""""""

The collapsible options section contains the following controls. Selecting or
deselecting an option will directly update the directory explorer.

  - **Show network drives**

    This option allows to show or hide linked network drives in the explorer
    view.

  - **Sorting is case sensitive**

    This option toggles case sensitive sorting. If enabled, lowercase and
    uppercase names will be sorted and displayed separately.

  - **Use custom data browsing root**

    When this checkbox is enabled, the directory explorer is restricted to a
    user-defined root directory. Only paths at or below the chosen root will
    be visible and accessible. This is convenient when working in an
    environment with a well-known data location and a cluttered file system.

    Enabling this option reveals three additional controls (see below).

    .. image:: images/data_browse/custom_root.png
        :width: 400px
        :align: left

    .. note::

        Attempting to navigate to a directory outside the custom root will
        raise a warning and the request will be ignored.

  - **Data browsing root** *(visible only when the custom root is enabled)*

    An input field that accepts the path of the desired root directory. Bare
    drive letters such as ``C:`` are automatically expanded to ``C:\``. The
    entry is not applied immediately; use the *Apply new root* button to
    confirm it.

  - **Apply new root** button *(visible only when the custom root is enabled)*

    Applies the path currently entered in the *Data browsing root* field as
    the new root for the explorer. If the path does not exist, the entry is
    rejected and the explorer reverts to showing the full file system.

  - **Reset root** button *(visible only when the custom root is enabled)*

    Clears the custom root and restores the explorer to the full file system.

Current directory and filter row
"""""""""""""""""""""""""""""""""

These controls are always visible regardless of whether the browsing options
section is collapsed.

  - **Current directory**

    This widget both shows the current directory and allows to change the
    current directory by entering a new path. If the new path does not exist,
    the entry will be ignored. It is also possible to drag and drop directories
    or files from the file system into the entry field. This will automatically
    set the current directory to the directory of the dragged item. In the case
    of files, the file will also be opened, if it is a supported data format.

  - **Filename filter**

    This field allows to filter the displayed files in the directory explorer.
    The asterisk ``*`` can be used as a wildcard. For example, entering ``*.h5``
    will display only files with the ``.h5`` extension. The filter is applied to
    files only and will not affect the display of directories, i.e. all
    directories will always be shown, regardless of the filter. The filter can
    be reset by deleting the entry in the field.

  - **Reset filter**

    This button resets the filename filter. It is equivalent to deleting the
    entry in the filter field.

  - **Collapse all**

    This button collapses all directories in the directory explorer.


Directory explorer
^^^^^^^^^^^^^^^^^^

The directory explorer is used to select the data to be displayed. The exact
look and feel will depend on the used operating system and might be different
from the screenshots shown here.

A single click on an item will just highlight the item but will otherwise be
ignored.

Double-clicking on a folder (or clicking the arrow next to a folder) will
**expand** the folder if it is currently collapsed, or **collapse** it if it is
already expanded. Double-clicking on a file will instruct pydidas to open the
selected file. If the data format is readable and the file contains
two-dimensional data, the content will be displayed in the ImageView widget.
In case of hdf5 files, an additional selection field will be shown to select
the data frame.

When a custom browsing root is active, the tree is anchored at that root
directory and parent directories above it are not shown.

Data display
^^^^^^^^^^^^

The data display widget is shown on the right with the default 2D image view for
multi-dimensional data.

Key elements are:

  - The filename display at the top:  This widget shows the full path of the
    opened file.
  - Selection widgets for raw images and hdf5 files: These widgets allow to
    select the data settings for raw images and the dataset for hdf5 files.
  - The visualization widget: The selected data is displayed here.
  - The slice selection widget: Select the slicing in multi-dimensional datasets
    to select a two-dimensional slice for visualization.
  - The display modality selection: Select how to display the data.


.. image:: images/data_browse/display.png
    :align: right
    :width: 300px

Details for all elements are given below.

.. note::

    The data display cannot process any metadata like axis labels or ranges.
    Only the raw data is displayed and only indices can be used to select.

|
|
|

The hdf5 data selection widget
""""""""""""""""""""""""""""""

The hdf5 data selection widget is shown below.

.. image:: images/data_browse/hdf5_small.png
    :align: center

In the minimized view, it allows to open a window to display the hdf5 file
structure (:ref:`hdf5_browser_window`), and a combo box to select the dataset to
display. An additional button allows to show more dataset filter options. The
full widget with all filter options is shown below:

.. image:: images/data_browse/hdf5_all.png
    :align: center

The first row allows the user to select dataset filters for specific names. For
example, the Eiger detector master file has a number of datasets for detector
specific settings like offsets and calibrations for the different modules. If
the respective box is ticked, these datasets will not be shown in the drop-down
list. Additional filters for datasets can be set on their and minimum data
dimension. Any changes to the filters will update the list of filtered datasets
immediately.

To select a dataset, simply select the corresponding hdf5 dataset key from the
drop-down list of the combo box. This will update the selection of the data
frame.

Browsing multi-dimensional datasets uses the slice selection widget, which will
be explained below.

The raw data selection widget
"""""""""""""""""""""""""""""

Importing raw data files requires an additional selection of data type, image
shape and header length (the header length is given in bytes). Setting all these
values allows to correctly decode raw images. The respective widget is shown
below:

.. image:: images/data_browse/raw.png
    :align: center

Trying to decode raw data with wrong settings raises a warning message if the
data cannot be imported.

A checkbox with *Automatically load files with these settings* allows to
automatically apply these settings to a series of files with the same settings.

The :py:data:`Hide detailed dataset selection options` button allows to minimize
the widget to a minimal size to increase the available space for the data
display.

Display modality and slice selection
""""""""""""""""""""""""""""""""""""

At the bottom of the data display widget, the display modality and slice
selection widgets allow to define how the data is displayed and which slice is
shown.

An exemplary view is shown below:

.. image:: images/data_browse/selection.png
    :align: center

Depending on the data dimensionality, the modality selection will show different
options:

 - Curve: Display a one-dimensional slice of the data as a line plot.
 - Image: Display a two-dimensional slice of the data as an image.
 - Raw: Display the raw data as a table.

The axis selection is required to specify which information to plot. For a curve
view, one data dimension can be specified as *curve y*. The other axes will show
a *use slice* option and a slider to select the slice to be plotted. For an
image view, two axes can be selected to *use as image y-axis* and *use as image
x-axis*, respectively. The other axes will show a *use slice* option and a
slider. Similarly, for the raw view, two axes can be selected to *use as row*
and *use as column*, respectively.

2D image view
"""""""""""""

.. include:: ../silx/plot2d_general.rst

Menu icon descriptions
~~~~~~~~~~~~~~~~~~~~~~

The following functionality is available through the toolbar icons:

.. include:: ../silx/plot2d_icons.rst
