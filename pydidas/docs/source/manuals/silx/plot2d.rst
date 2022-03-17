Presentation of 2D plots
^^^^^^^^^^^^^^^^^^^^^^^^ 

.. image:: ../../images/frames/execute_workflow_12_2dplot_overview.png
    :width:  506px
    :align: left
    
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

Toolbar menu entries
""""""""""""""""""""

.. list-table::
    :widths: 20 80
    :class: tight-table
    :header-rows: 1

    * - menu icon
      - description
    * -  .. image:: ../../images/plot2d/plot2d_01_menu_zoom.png
            :align: center
      - Zoom mode: clicking with the mouse and dragging spans a new selection
        of the data to be visualized.
    * -  .. image:: ../../images/plot2d/plot2d_02_menu_pan.png
            :align: center
      - Panning mode: clicking with the mouse and dragging moves the data on the
        canvas.
    * -  .. image:: ../../images/plot2d/plot2d_03_menu_unzoom.png
            :align: center
      - Unzoom: Reset the display region to the full data.
    * -  .. image:: ../../images/plot2d/plot2d_04_menu_palette.png
            :align: center
      - Open the colormap editor. This button opens a window with selections
        for the colormap and scaling of the displayed minimum and maximum 
        values.
    * -  .. image:: ../../images/plot2d/plot2d_05_menu_aspect.png
            :align: center
      - This action allows to control the aspect of the displayed data and 
        allows to stretch the data to fill the available canvas or keep its
        original aspect ratio.
    * -  .. image:: ../../images/plot2d/plot2d_06_menu_orientation.png
            :align: center
      - Control the position of the origin in the image: Select between the top
        left and bottom left corner.
    * -  .. image:: ../../images/plot2d/plot2d_07_menu_colorbar.png
            :align: center
      - Display or hide the colorbar on the drawing canvas.
    * -  .. image:: ../../images/plot2d/plot2d_08_menu_mask.png
            :align: center
      - Mask tools: This button opens an additional widget at the bottom of the
        canvas with tools for importing or setting a mask to mask certain 
        data regions. 
    * -  .. image:: ../../images/plot2d/plot2d_09_menu_copy_to_clipboard.png
            :align: center
      - Copy the currently visible figure to the clipboard. This will only copy
        the main figure and not the histograms.
    * -  .. image:: ../../images/plot2d/plot2d_10_menu_save_to_file.png
            :align: center
      - Save the currently loaded full data to file, ignoring any zooming. This 
        function will open a dialogue to select the file type and filename. 
        Depending on the selected file type, the colormap and scaling will be 
        retained (e.g. for png export) or ignored (e.g. tiff export).
    * -  .. image:: ../../images/plot2d/plot2d_11_menu_print.png
            :align: center
      - Print the currently visible figure. This will print only the data 
        visible on the canvas and it will retain colormap and scaling settings.
    * -  .. image:: ../../images/plot2d/plot2d_12_menu_profile.png
            :align: center
      - Create and delete line profiles. This function allows the selection and
        editing of line profiles. The line profiles are shown in the histograms
        plots for the vertical and horizontal, respectively.

