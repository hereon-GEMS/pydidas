..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


Point list and controls
^^^^^^^^^^^^^^^^^^^^^^^

Located at the top are controls for how to select points and for the overlay 
color.

The *Use 2 click point selection* toggles how points are selected in the image:

  - Disabled 2-click point selection:

    If disabled, points will be selected directly with a single click in the 
    image. This requires the user to manually zoom in to select points with 
    high accuracy.
    
  - Enabled 2-click point selection:

    When enabled, clicking on a point in the image will zoom in on the selected
    point to allow a higher degree of precision for the point selection. 
    The second click will select the point and reset the zoom to the previous
    settings.
    
The second item is a configuration widget to change the color of all the plot 
overlay items like the points to increase the contrast, depending on the chosen
colormap for the image. Changing the color in the drop-down selection will 
automatically update the color in all overlay items. 

The point list displays the positions of all clicked points. Left-clicking on
a point in the list will select this point and also highlight it in the image
by changing the marker. Multiple points can be selected by holding 
:py:data:`Shift` when selecting the second point to select all points inbetween
or by holding :py:data:`Ctrl` while selecting points to add only single points 
to the selection. All selected points will be highlighted in the image. 

The two buttons at the bottom of the point list allow to delete the current
selection of points or all points. The current selection of points can also be
deleted by pressing :py:data:`Del` while the plot list has the focus.
