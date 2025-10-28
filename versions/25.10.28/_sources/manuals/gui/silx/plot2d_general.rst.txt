..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


The :py:class:`PydidasPlot2d <pydidas.widgets.silx_plot.PydidasPlot2d>` is a
subclassed `silx Plot2d
<http://www.silx.org/doc/silx/latest/modules/gui/plot/plotwindow.html#silx.gui.plot.PlotWindow.Plot2D>`_
with additional features useful in pydidas.

.. image:: ../silx/images/standard_plot2d.png
    :width: 600px
    :align: center

- The menu
    The menu bar allows access to all generic silx and additional pydidas
    functionality. The detailed menu icons and actions are described below
    in the menu entries description.
- The image display
    This widget shows the image data. Depending on the zoom level, this is
    either the full image or a sub-region.
- The colorbar
    The colorbar shows the reference for the used colormap to map data levels to
    colors.
- The position information
    This widget displays the coordinates and data values of the data under
    the mouse cursor.

Two-dimensional plots are presented in a `silx Plot2D widget
<http://www.silx.org/doc/silx/latest/modules/gui/plot/plotwindow.html#silx.gui.plot.PlotWindow.Plot2D>`_\ .
The toolbar options will be explained in detail below. Moving the mouse over the
canvas will update the labels for x/y position and data value at the bottom of
the canvas. Note that the x and y axis positions for each pixel are defined at
the pixel center and the given values must be treated carefully with respect to
the pixel shape, especially for coarse pixels.

.. tip::

    The scaling of the results can be achieved by modifying the colormap
    settings.
