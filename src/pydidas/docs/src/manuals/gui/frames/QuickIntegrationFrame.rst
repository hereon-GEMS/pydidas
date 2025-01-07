..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Quick Integration frame
=======================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

The *Quick integration* frame allows to perform a quick integration without 
needing to set up the full :py:class:`DiffractionExperiment
<pydidas.contexts.diff_exp.DiffractionExperiment>` and 
:py:class:`ScanContext<pydidas.contexts.scan.Scan>`.

The frame does, however, have some limitations: Processing is limited to data
loading and integrating (azimuthal, radial or 2-dimensional) and the detector is
assumed to be perfectly aligned, i.e. all rotations are set to zero.


.. image:: images/quick_int/overview.png
    :width: 600px
    :align: center

The left side shows the configuration and most configuration options will become
available once an image has been imported. The right side holds two plots for
input image and integration results in tabs.

The configuration on the left holds the following functions which will be 
described in more detail below:

  - Input selection
  - Experiment description
  - Beamcenter
  - Integration region of interest
  - Run the integration

Input selection
---------------

.. include:: ../beamcenter/file_input.rst

Experiment description
----------------------

.. image:: images/quick_int/experiment.png
    :align: left

The detailed experiment description is hidden upon startup. Default values for 
the detector pixel size, detector distance and X-ray energy allow to run any 
integration right away without needing to modify any values. The only Parameter
displayed directly is the detector model. If the shape of the input image 
corresponds to a known detector, the choices are updated correspondingly.
Choosing the correct detector model allows pyFAI to use the generic mask for 
this detector make, for example to mask module gaps.

.. note::
    The integration can be run directly with the defaults but as a result, the 
    scaling of the integration results (i.e. 2theta / Q / r values) are wrong.
    Nonetheless, the integration profile can be inspected and assessed.

.. image:: images/quick_int/exp_full.png
    :align: right
    
The expanded experiment description section offers the options of importing a 
full calibration or by manually setting X-ray energy, sample-detector distance
and the detector pixel size. Note that square pixels are assumed. 

A custom detector mask can be used as well. This will take precedence over the
generic detector mask.

|
|

Beamcenter
----------

.. image:: images/quick_int/beamcenter.png
    :align: left

The beamcenter position (in detector pixel coordinates) can be set directly,
if it is known. The position is also updated if the experimental description 
has been imported. 

The "Start graphical beamcenter selection" button will toggle the graphical 
selection mode. This will show additional control buttons, a panel with a list
of selected points and disable other settings. In addition, clicking in the 
image will select the clicked pixel positions and store them in the list.

.. image:: images/quick_int/bc_selection.png
    :width: 600px
    :align: center

The image above shows the initial view after enabling the graphical beamcenter 
selection. The additional control buttons and center panel with the point list 
are described in detail below.

.. include:: ../beamcenter/bc_image_display.rst

.. include:: ../beamcenter/point_list.rst

Control buttons
^^^^^^^^^^^^^^^

.. image:: images/quick_int/bc_control.png
    :align: left

|
|
|
|

The control buttons allow give two choices for setting the beamcenter:

1. A single selected point can be set as beamcenter. This requires that exactly 
   one point was selected in the image. The beamcenter marker will be updated 
   and the coordinates will be copied as the new beamcenter.
   
2. A circle can be fitted through all selected points. The circle center is 
   taken as the beamcenter position. The circle fit will be shown with a dotted
   line to allow verification of the quality.
   
The last button, "confirm beamcenter" will disable the graphical beamcenter
selection and enable the other configurations again.


Integration region of interest
------------------------------

.. image:: images/quick_int/roi_options.png
    :align: left
    
The integration region of interest can be selected either by entering values 
for the radial and azimuthal range or graphically after clicking the 
"Select radial / azimuthal integration range in image" button.

.. include:: ../integration_roi/select_roi.rst

Run the integration
-------------------

.. image:: images/quick_int/run.png
    :align: left

To run, the integration, select the corresponding direction and number of points
from the list and click the button to run. The results will be displayed in the 
second plot tab, labeled *Integration results*.

Data visualization
------------------

Two separate plots for input and integration results are organized as tabs on 
the right side of the frame. 

The modified silx Plot1D and Plot2D widgets are used for displaying the data
and the are described in detail below.

.. include:: ../silx/plot1d.rst

.. include:: ../silx/plot2d.rst
