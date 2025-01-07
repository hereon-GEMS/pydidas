..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


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
    * -  .. image:: ../silx/images/menu_match_canvas.png
            :align: center
      - Match canvas: Set the aspect ratio to 1 and match the canvas size to
        the data to allow a tight fit.
    * -  .. image:: ../silx/images/menu_expand_canvas.png
            :align: center
      - Expand canvas: Reset the canvas size to take up all available space.
        This option does also change the data aspect to make use of the full
        canvas.
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
    * -  .. image:: ../silx/images/menu_colorbar.png
            :align: center
      - Display or hide the colorbar on the drawing canvas.
    * -  .. image:: ../silx/images/menu_mask.png
            :align: center
      - Mask tools: This button opens an additional widget at the bottom of the
        canvas with tools for importing or setting a mask to mask certain
        data regions.
    * -  .. image:: ../silx/images/menu_coordinate_system.png
            :align: center
      - Set coordinate system: This button will open a submenu which allows to
        select the coordinate system (cartesian or cylindrical). Note that the
        cylindrical coordinate system use the global :py:class:`DiffractionExperimentContext
        <pydidas.contexts.diff_exp.DiffractionExperiment>`
        calibration to determine the beam center. Therefore, looking at data
        with a different calibration will display a wrong center and therefore
        also wrong coordinates.
    * -  .. image:: ../silx/images/menu_get_data_info.png
            :align: center
      - Get information for selected datapoint: This button will allow the user
        to click on a point in the image and show a window with additional
        information about this point (specifically: all indices / data values).
    * -  .. image:: ../silx/images/menu_copy_to_clipboard.png
            :align: center
      - Copy the currently visible figure to the clipboard. This will only copy
        the main figure and not the colorbar.
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
