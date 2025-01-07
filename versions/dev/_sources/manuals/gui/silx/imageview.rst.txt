..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Pydidas ImageView
^^^^^^^^^^^^^^^^^

The :py:class:`PydidasImageView <pydidas.widgets.silx_plot.PydidasImageView>` is a
subclassed `silx ImageView
<http://www.silx.org/doc/silx/latest/modules/gui/plot/imageview.html#silx.gui.plot.ImageView.ImageView>`_
with additional features useful in pydidas.

Its layout is shown below:

.. image:: ../silx/images/standard_imageview.png
    :width: 600px
    :align: center

- The menu
    The menu bar allows access to all generic silx and additional pydidas
    functionality. The detailed menu icons and actions are described below
    in the menu entries description.
- The image display
    This plot shows the image data. Depending on the zoom level, this is either
    the full image or a sub-region.
- The overview & pan area
    This widget shows the current zoom region with respect to the full image,
    if the user zoomed in on a subregion. In addition, it allows to pan the
    image region by dragging the zoom region.
- The histograms
    The vertical and horizontal histograms display the histograms for the
    selected image region.
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
    * -  .. image:: ../silx/images/menu_palette.png
            :align: center
      - Open the colormap editor. This button opens a window with selections
        for the colormap and scaling of the displayed minimum and maximum
        values.
    * - .. image:: ../silx/images/menu_crop_histogram_outliers.png
            :align: center
      - Crop histogram outliers: Calculate the histogram of the image and set
        the colormap to ignore the low *x% and the top *y%* of the image
        histogram. The levels of *x* and *y* can be adjusted in the pydidas
        user settings.
    * - .. image:: ../silx/images/menu_cmap_autoscale.png
            :align: center
      - Autoscale the colormap to the image mean value +/- 3 standard
        deviations.
    * -  .. image:: ../silx/images/menu_aspect.png
            :align: center
      - This action allows to control the aspect of the displayed data and
        allows to stretch the data to fill the available canvas or keep its
        original aspect ratio.
    * -  .. image:: ../silx/images/menu_orientation.png
            :align: center
      - Control the position of the origin in the image: Select between the top
        left and bottom left corner.
    * -  .. image:: ../silx/images/menu_mask.png
            :align: center
      - Mask tools: This button opens an additional widget at the bottom of the
        canvas with tools for importing or setting a mask to mask certain
        data regions.
    * -  .. image:: ../silx/images/menu_histogram.png
            :align: center
      - Show/hide the histograms at the side. This will also hide the
        *overview & pan* widget.
    * -  .. image:: ../silx/images/menu_filter.png
            :align: center
      - Filter tools: This button allows the user to select simple filters to
        apply to the image data.
    * -  .. image:: ../silx/images/menu_coordinate_system.png
            :align: center
      - Set coordinate system: This button will open a submenu which allows to
        select the coordinate system (cartesian or cylindrical). Note that the
        cylindrical coordinate system use the global :py:class:`DiffractionExperimentContext
        <pydidas.contexts.diff_exp.DiffractionExperiment>`
        calibration to determine the beam center. Therefore, looking at data
        with a different calibration will display a wrong center and therefore
        also wrong coordinates.
    * -  .. image:: ../silx/images/menu_copy_to_clipboard.png
            :align: center
      - Copy the currently visible figure to the clipboard. This will only copy
        the main figure and not the histograms.
    * -  .. image:: ../silx/images/menu_save_to_file.png
            :align: center
      - Save the currently loaded full data to file, ignoring any zooming. This
        function will open a dialogue to select the file type and filename.
        Depending on the selected file type, the colormap and scaling will be
        retained (e.g. for png export) or ignored (e.g. tiff export).
    * -  .. image:: ../silx/images/menu_print.png
            :align: center
      - Print the currently visible figure. This will print only the data
        visible on the canvas and it will retain colormap and scaling settings.
    * -  .. image:: ../silx/images/menu_profile.png
            :align: center
      - Create and delete line profiles. This function allows the selection and
        editing of line profiles. The line profiles are shown in the histograms
        plots for the vertical and horizontal, respectively.
