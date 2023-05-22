.. 
    Copyright 2023, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


Point list and controls
^^^^^^^^^^^^^^^^^^^^^^^

At the very top of the list is a configuration widget to change the color of all
the plot overlay items like the points to increase the contrast. 

The point list displays the positions of all clicked points. Left-clicking on
a point in the list will select this point and also highlight it in the image
by changing the marker. Multiple points can be selected by holding 
:py:data:`Shift` when selecting the second point to select all points inbetween
or by holding :py:data:`Ctrl` while selecting points to add only single points 
to the selection. All selected points will be highlighted in the image. 

The two buttons at the bottom of the point list allow to delete the current
selection of points or all points. The current selection of points can also be
deleted by pressing :py:data:`Del` while the plot list has the focus.
