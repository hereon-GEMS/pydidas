.. _user_config_window:

The User config window
======================

The *User config window* allows the user to customize the bahaviour of their
pydidas copy. The individual Parameters are described below.

.. image:: images/user_config_overview.png
    :align: center

Using the :py:data:`Restore defaults` button will change all settings back to 
their default values.

Settings
--------

.. list-table::
    :widths: 25 75
    :header-rows: 1
    :class: tight-table
    
    * - Parameter 
      - Description
    * - Detector mask file
      - The path to the *global* detector mask file used in pydidas. Whenever a
        *global detector mask* is referred to in pydidas, it refers to this 
        file.
    * - Detector mask display value
      - The value to display for masked pixels. **This value is used for 
        visualization only, not for processing.**
    * - Mosaic tiling border width
      - The width (in pixels) of the border between adjacent images in 
        composites.
    * - Mosaic border value
      - The value to be assigned to the pixels on the border between adjacent
        images.
    * - Histogram outlier fraction
      - [This setting is for 2D image displays only]. This Parameter defines
        which portion of the histogram should be ignored when defining the 
        upper limit for the colormap. The default value of 0.07 means that the
        top 7% of the histogram will be ignored for setting the colormap. The 
        default value was selected to cover all pixels in module gaps for an
        Eiger 9M detector.
    * - Default colormap
      - The default colormap to be used for displaying 2D datasets. The 
        colormap can still be changed in each individual data window but those
        changes are not persistent.
    * - Plugin paths
      - The paths where pydidas is searching for its plugins. The default
        directory will have all generic pydidas plugins. To add individual 
        paths with custom plugins, just add them to the list. 
        
        **Entries must be separated by a double semicolor ";;".**
        
        Changes to the plugin path will only take effect after using the 
        :py:data:`Update plugin collection` button.
