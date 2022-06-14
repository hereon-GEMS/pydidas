The Execute workflow frame
==========================

The "Run full processing" frame is split in two main parts. On the left are the 
controls for configuring the automatic saving and for running the Workflow as 
well as for manual data export. The right part of the frame is taken by a 
visualization widget for 1d plots or 2d images, depending on the result 
selection.

.. image:: ../../images/frames/execute_workflow_01_overview.png
    :width:  457px
    :align: center

The configuration on the left holds four different functions which will be 
described in more detail below:

  - Configuration of the automatic result saving
  - Running the processing
  - Selecting the results to be plotted
  - Manually exporting results

Detailed description of frame items
-----------------------------------

Configuring the automatic saving
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../../images/frames/execute_workflow_02_autosave_inactive.png
    :align: left
    
The configuration of the automatic saving is the topmost item on the left of the
frame. By default, autosaving the results is disabled and only the toggle 
Parameter to enable it is visible. Enabling the autosave will show two 
additional Parameter configuration widgets to select the saving directory and 
the type of files. 

.. image:: ../../images/frames/execute_workflow_03_autosave_active.png
    :align: left

Files will be automatically created based on different autosave formats selected
in the Parameter.

.. note::

    The autosave directory must be an empty directory at the start of the 
    processing, even though this condition is not enforced at the time of 
    selection.
    
Running the processing
^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../../images/frames/execute_workflow_04_processing_to_start.png
    :align: left

The processing can be started with a click on the corresponding button. This 
will show a progress bar and an "Abort" button. 

.. image:: ../../images/frames/execute_workflow_05_processing_active.png
    :align: left
    
The "Abort" button will let the user send termination signals to the worker 
processes and - depending on the type of calculations - may take a while to take 
effect because the current process might not accept the termination signal 
until it starts a new job.

.. include:: ./workflow_result_selection.rst

.. include:: ./workflow_result_export.rst

.. include:: ../silx/plot1d.rst

.. include:: ../silx/plot2d.rst

