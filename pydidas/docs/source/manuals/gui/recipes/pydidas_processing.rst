Using the pydidas processing pipeline
=====================================

.. contents::
    :depth: 2
    :local:
    :backlinks: none
    
.. note::

    While setting up and using the pydidas processing pipeline is also available
    from the command line, creating and editing the 
    :py:class:`WorkflowTree <pydidas.workflow.workflow_tree._WorkflowTree>`, 
    :py:class:`DiffractionExperimentContext <pydidas.contexts.diffraction_exp_context.diffraction_exp_context._DiffractionExperimentContext>`, and
    :py:class:`ScanContext <pydidas.contexts.scan_context.scan_context._ScanContext>` are more easily
    done in the graphical user interface and therefore, this guide covers
    the GUI.
    
To process data from scratch, the following steps need to be performed:

    1. Perform the detector calibration (in pyFAI geometry)
    2. Define the experimental setup (X-ray energy, detector, geometry) using 
       the calibration.
    3. Define the scan (paths, filenames and scanpoints).
    4. Define the workflow which defines which operations to perform on the 
       data.
    5. Test the workflow and tweak processing parameters (optional).
    6. Run workflow and save results.
    
Each of the steps will be explained in detail below. Also, an example will be
used for demonstration of each step.

1. Detector calibration
-----------------------

The detector calibration can best be performed using the *pyFAI-calib2* tool.
A version of this tool is implemented in pydidas and can be accessed directly
through the toolbar menu on the left (circled in orange):

.. image:: images/processing_01_calibration.png
    :align: center
    :width: 400px

For a tutorial on how to use the *pyFAI-calib2* tool, please refer directly 
to the `pyFAI calibration tutorial 
<https://pyfai.readthedocs.io/en/master/usage/cookbook/calib-gui/index.html#cookbook-calibration-gui>`_\ .

2. Define the experimental setup
--------------------------------

.. image:: images/processing_02_experimental_setup.png
    :align: left
    :width: 300px
    
The pydidas frame to edit the experimental setup can be accessed through the
*Workflow processing* -> *Define experimental setup* toolbar entries (marked
in orange on the left). 

If you just performed the detector calibration, use the 2nd button from the top
*Copy all experimental parameters from calibration* to automatically update
all Parameter values, with the exception of the detector mask.

If you want to re-use a previous detector calibration, use the topmost button
*import experimerimental parameters from file* to open a file selection 
dialogue. After confirming the selected file, the parameters are updated.
Note that the *detector mask file* parameter is not included in pyFAI's 
.poni file format and is not updated when importing a poni file. 

The *detector mask file* must be set independently of the pyFAI calibration
parameter import, if it has not been set in the pyFAI calibration.

For more details, please refer to the :ref:`define_diffraction_exp_frame` 
manual.

Example
^^^^^^^

The example has been performed at an X-ray energy of 13 keV using an Eiger 9M
detector. This information was available from the beamline. The mask file for
the detector was saved at *E:\test\eiger_mask.npy* (in numpy binary format).
All the information was copied from the detector calibration.

3. Define the scan
------------------

.. image:: images/processing_03_scan_setup.png
    :align: center
    :width: 400px

Scan parameters and metadata can be edited on the *define scan* frame which can
be accessed through the *Workflow processing* -> *Define scan* toolbar entries 
(marked in orange in the image above). 

All of the *global scan parameters* (except for the scan title) found in the 
left column are mandatory, whereas on the number of scan points is mandatory 
for each scan dimension.

The parameters for the scan base directory and naming pattern allow pydidas to 
find the data and read the correct files. The number of scan points in each scan
dimension allows pydidas to re-arrange the input data in the correct shape.
The additional parameters for the individual scan dimensions are used for 
annotating the results and for giving meaningful values to the dimensions but 
they are not strictly necessary.

For more information, please refer to the :ref:`define_scan_frame` manual.

Example
^^^^^^^

In the example used in the image above, the individual image files are located
in the E:\test\raw directory and the data files are named test_00010_data.h5, 
test_00011_data.h5, etc. (therefore, the starting index is set to 10).

One image was acquired at each scan point in a mesh of 25 x 25 points. 

4. Creating the workflow
------------------------

To create the workflow, select the *Workflow processing* - > *Workflow editing* 
toolbar entry (marked in orange in the image above). 
The workflow is comprised of individual plugins which each perform a single 
task, like frame loading, azimuthal integration, background correction, 
peak fitting. The workflow can branch downward in an unlimited number of nodes
(subject to processing resources).

