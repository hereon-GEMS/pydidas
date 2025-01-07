..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Pydidas 1D plot
^^^^^^^^^^^^^^^ 

The :py:class:`PydidasPlot1d <pydidas.widgets.silx_plot.PydidasPlot1d>` is a 
subclassed `silx Plot1d 
<http://www.silx.org/doc/silx/latest/modules/gui/plot/plotwindow.html#silx.gui.plot.PlotWindow.Plot1D>`_
with additional features useful in pydidas.

.. image:: ../silx/images/standard_plot1d.png
    :width: 600px
    :align: center

- The menu
    The menu bar allows access to all generic silx and additional pydidas 
    functionality. The detailed menu icons and actions are described below
    in the menu entries description.
- The plot display
    This plot shows the data. Depending on the zoom level, this is either
    the full image or a sub-region.
- The position information
    This widget displays the coordinates and data values of the data under
    the mouse cursor. 

menu entries description
"""""""""""""""""""""""" 

.. list-table::
    :widths: 20 80
    :class: tight-table
    :header-rows: 1

    * - menu icon
      - description
    * -  .. image:: ../silx/images/menu_zoom.png
            :align: center
      - Zoom mode: clicking with the mouse and dragging spans a new selection
        of the data to be visualized.
    * -  .. image:: ../silx/images/menu_pan.png
            :align: center
      - Panning mode: clicking with the mouse and dragging moves the data on the
        canvas.
    * -  .. image:: ../silx/images/menu_unzoom.png
            :align: center
      - Unzoom: Reset the display region to the full data.
    * -  .. image:: ../silx/images/menu_x_autoscale.png
            :align: center
      - Activate autoscaling of the x-axis. If enabled, the x-axis will be 
        matched to the data range upon activation or upon using the "Unzoom"
        button.
    * -  .. image:: ../silx/images/menu_y_autoscale.png
            :align: center
      - Activate autoscaling of the y-axis. If enabled, the y-axis will be 
        matched to the data range upon activation or upon using the "Unzoom"
        button.
    * -  .. image:: ../silx/images/menu_x_log.png
            :align: center
      - Switch between a linear and a logarithmic x-axis.
    * -  .. image:: ../silx/images/menu_y_log.png
            :align: center
      - Switch between a linear and a logarithmic y-axis.
    * -  .. image:: ../silx/images/menu_grid.png
            :align: center
      - Toggle a grid in the main plotting canvas.
    * -  .. image:: ../silx/images/menu_style.png
            :align: center
      - Change the drawing style. Repeatedly using this button will cycle 
        through lines, dots, and lines & dots styles for the curve.
    * -  .. image:: ../silx/images/menu_plot_type_generic.png
            :align: center
      - Change the plotted data to the generic y vs. x plot without any special
        operations.
    * -  .. image:: ../silx/images/menu_plot_type_kratky.png
            :align: center
      - Plot data in a Kratky-type plot using y * x^2 vs. x for the y and 
        x-axis, respectively. This plot allows, for example, to correct for the 
        q-dependence of the scattering intensity in small angle scattering.
    * -  .. image:: ../silx/images/menu_copy_to_clipboard.png
            :align: center
      - Copy the currently visible figure to the clipboard.            
    * -  .. image:: ../silx/images/menu_save_to_file.png
            :align: center      
      - Save the currently loaded full data to file, ignoring any zooming. This 
        function will open a dialogue to select the file type and filename. 
        Depending on the selected file type, the colormap and scaling will be 
        retained (e.g. for png export) or ignored (e.g. tiff export).
    * -  .. image:: ../silx/images/menu_print.png
            :align: center
      - Print the currently visible figure. This will print the current canvas 
        (and therefore only the data visible on the canvas).

