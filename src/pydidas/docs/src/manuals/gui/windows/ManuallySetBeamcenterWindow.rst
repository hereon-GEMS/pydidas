..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _manually_set_beamcenter_window:

Manually Set Beamcenter Window
==============================

The *Manually set beamcenter window* allows to select the beamcenter in
detector pixel coordinates, either by setting the pixel position directly or by
using a graphical interface. The functionality is limited in the sense that a
perfect detector orientation is assumed (i.e. all rotations are zero) and it is 
not possible to optimize rotations. If that is required, please perform a full
calibration.

.. image:: images/set_bc_overview.png
    :align: center
    :width: 600

The left side offers controls, the central panel is a list to view and edit 
points selected in an image and am image plot is shown on the right.


.. include:: ../beamcenter/bc_image_display.rst

.. include:: ../beamcenter/point_list.rst

Controls
^^^^^^^^

File input
""""""""""

.. include:: ../beamcenter/file_input.rst

Beamcenter selection
""""""""""""""""""""

.. image:: images/set_bc_controls.png
    :align: left


The beamcenter position (in detector pixel coordinates) can be set directly,
if it is known. 

The following control buttons are availabe:

 - **Set selected point as beamcenter**: This button requires to have marked
   exactly one point in the image. Clicking this button will take that point's 
   coordinates as the new beamcenter. Note that the list of points must have 
   exactly one entry, not one selected entry.
 - **Fit beamcenter with circle**: All points in the list will be used as 
   coordinates to fit a circle. The center will be taken as new beamcenter and 
   the fitted circle will be shown as overlay in the image.
 - **Fit beamcenter with ellipse**: Similar to the button above, but an ellipse
   instead of a circle is used to find the beamcenter. Fitting an ellipse 
   requires selecting at least 5 points on the circumference.
   
The last button at the bottom, "Comfirm selected beamcenter" will close the 
window and convert the selected beamcenter to pyFAI PONI coordinates and update
the DiffractionExperiment.
