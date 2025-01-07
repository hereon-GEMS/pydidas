..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _workflow_test_frame:

Workflow test frame
===================

.. contents::
    :depth: 2
    :local:
    :backlinks: none
    
The Workflow test frame can be used to run the 
:py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>` locally
for a single scan point and visualize all results, including intermediate 
results.

.. image:: images/test/overview.png
    :width: 600px
    :align: center

The frame holds control and result selection widgets on the left and a plot 
canvas for data visualization on the right.

Keeping the Workflow up to date
-------------------------------

The :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`
is automatically kept up to date. If any Plugin, Plugin Parameter or ScanContext
Parameter changes, the WorkflowTree is automatically updated.
In these instances, it is not required to manually update the 
:py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`.

.. image: images/test/reset.png
    :align: right
    
However, if any global settings have changed, for example the detector mask
file, the user needs to manually reset the WorkflowTree. This can be done by
clicking the corresponding button at the top left of the frame.

Data source selection
---------------------

.. image:: images/test/image_select.png
    :align: right


A single frame must be selected to test the 
:py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`. Three 
options exist for selecting the frame which can be toggled by the "Image 
selection" Parameter (see image on the right). 

.. image:: images/test/global_index.png
    :align: left

Using the "Global index" entry, a datapoint can be selected by its absolute 
number in the acquisition sequence (i.e. chronologically starting with 0). 
This number must be given in the "Global frame index" Parameter field.


.. image:: images/test/scan_indices.png
    :align: left

Selecting the "Use scan indices" will allow the user to pick a datapoint based
on its position in the scan. Parameters for all defined scan dimensions are 
shown and must be used to select the desired datapoint.

.. image:: images/test/det_number.png
    :align: left

Selecting the "Use detector image number" will allow the user to pick a 
datapoint based on the detector image number. This accounts for offsets in 
image numbers, as defined by the "Starting index" in the Scan settings.

Processing
----------

Clicking the "Process frame" button will start the workflow processing.

.. note::

    Depending on the selected workflow, this operation might take a few seconds
    and the GUI will be unresponsive during processing. The user is also
    informed that pydidas is busy by displaying the OS's busy mouse cursor.
    
    Any pyFAI integration will require an initialization which takes several
    seconds and must be performed again if any pyFAI integration Parameters
    change.

Results
-------

.. image:: images/test/res_selection.png
    :align: left

.. image:: images/test/result_info.png
    :align: left

After running the local processing, the results for the different nodes can be
visualized by selecting the corresponding entry from the results drop-down
selection. This will open a text box with additional information about the 
plugin results (see image below). 
Information about all result axes, values and metadata will be displayed in the 
box and a plot or image will be shown in the data display, if the results are
one- or two-dimensional, respectively. For any other result dimensions, only the 
text information will be shown in the box.

|
|
|
|
|
|
|
|


Further details
---------------

Detailed results
^^^^^^^^^^^^^^^^

.. image:: images/test/details_button.png
    :align: left
    
Some plugins have defined detailed results which can be visualized in addition
to the generic plugin results. This information can be used for checking if the 
Plugin behaves as expected. Details about the opened window can be found
in the :ref:`Show Detailed Plugin Results window manual 
<show_detailed_plugin_results_window>`

.. note:
    Whether a Plugin includes detailed results and what data exactly is 
    defined individually within each Plugin.

Tweak plugin parameters
^^^^^^^^^^^^^^^^^^^^^^^

.. image:: images/test/tweak_button.png
    :align: left

The option to *tweak plugin parameters* exists for all plugins and appears below
the result info box once a plugin has been selected.

This button will open a new window which allows to test different Parameter 
options on the fly. For details, please refer to the :ref:`Tweak Plugin 
Parameter window manual <tweak_plugin_parameters_window>`

.. tip:
    Tweaking Plugin Parameters will run the WorkflowTree again for the active 
    plugin and its children. All available information is always consistent 
    when Parameter changes have been accepted.


