..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _composite_creator_frame:

Composite image creator frame
=============================

.. contents::
    :depth: 2
    :local:
    :backlinks: none
    
The Composite image creator frame is a graphical interface to configure the 
:py:class:`CompositeCreatorApp <pydidas.apps.CompositeCreatorApp>` and to
visualize the results.

After starting the frame, only the menu for editing the Parameters is enabled
(orange frame in the image below).
For the tutorial about editing Parameters, please visit 
:ref:`gui_editing_parameters`. The full list of Parameters and their description
is given at the end in :ref:`composite_image_creator_params`. 

After setting the required Parameters, the app control panel (yellow frame in 
the image below) will become enabled and the user can start processing.

The processed composite image will be shown on the right side of the frame 
(blue area in the image below).

.. image:: images/comp_crt/initial.png
    :width: 600px
    :align: center

Control buttons
----------------

Clear all entries
^^^^^^^^^^^^^^^^^

.. image:: images/comp_crt/clear.png
    :align: left

The "Clear all entries" button at the top will reset all inputs to their default
values. Note that no confirmation will be asked of the user.

Generate composite
^^^^^^^^^^^^^^^^^^

.. image:: images/comp_crt/generate.png
    :align: left

Once the bare minimum Parameters have been selected (this is the first file name
and in case of an Hdf5 file the dataset), the "Generate composite" button will 
be enabled. Clicking the button starts an :py:class:`AppRunner <pydidas.multiprocessing.AppRunner>`
process which loads and processes the images in parallel processes.

Once clicked, the "Generate composite" button will be disabled and a 
progress bar as well as an "Abort" button will appear:

.. image:: images/comp_crt/abort.png
    :align: left

The progress bar will update with each received image and it shows the global
processing progress. The "Abort" button will stop the AppRunner. Any data 
received by the Frame up to this point will be kept but the rest of the 
composite image will only consist of zeros. The progress bar and "Abort" button 
will be hidden again after the Composite creation has finished.

.. note:: 
    After starting the AppRunner, it is normal that the first results need
    a few seconds to arrive because the new processes need to be started and
    load all required python packages.

Show composite
^^^^^^^^^^^^^^

.. image:: images/comp_crt/show.png
    :align: left

During processing, the composite image is automatically updated. If the uses
requires an additional manual update, the "Show composite" button can be used
to perform this update.

Save composite image
^^^^^^^^^^^^^^^^^^^^ 

.. image:: images/comp_crt/save.png
    :align: left

The "Save composite image" button opens a dialogue to select a file name. The 
image type is determined automatically based on the selected file extension.
A filter for all supported data types can be selected at the bottom of the 
dialogue.

Result visualization
--------------------

.. image:: images/comp_crt/results.png
    :width: 600px
    :align: center

Results are visualized in a :py:class:`PydidasPlot2d <pydidas.widgets.silx_plot.PydidasPlot2d>`,
described below:

.. include:: ../silx/plot2d.rst

.. _composite_image_creator_params:

Full list of Composite image creator Parameters
-----------------------------------------------

.. include:: ../../global/composite_creator_app_params.rst
