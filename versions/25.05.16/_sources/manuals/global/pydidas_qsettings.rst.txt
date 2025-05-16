..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Pydidas QSettings are grouped into two main categories: 'global' settings and
'user' settings. Global settings define the system behaviour and performance
whereas the user settings handle convenience user configurations.

**Global** settings
""""""""""""""""""" 

- Multiprocessing settings
    - Number of MP workers (key: global/mp_n_workers, type: int, default: 4)
        The number of multiprocessing workers. Note that this number should not 
        be set too high for two reasons:
        1. File reading processes interfere with each other if too many are 
        active at once.
        2. pyFAI already inherently uses parallelization and you can only gain 
        limited performance increases for multiple parallel processes.
    - Shared buffer size limit (key: global/shared_buffer_size, type: float, default: 100, unit: MB)
        A shared buffer is used to efficiently transport data between the main 
        App and multiprocessing Processes. This buffer must be large enough to 
        store at least one instance of all result data.
- Memory settings
    - Buffer dataframe limit (key: global/shared_buffer_max_n, type: int, default: 20)
        The maximum number of datasets in the buffer. A dataset consists of all 
        results for one frame. For performance reasons, the buffer should not 
        be too large as this is only a temporary buffer.
    - Maximum image size (key: global/max_image_size, type: float, default: 100, unit: MPixel)
        The maximum image size determines the maximum size of images pydidas 
        will handle. The default is 100 Megapixels.
- GUI plot update settings
    - Plot update time (key: global/plot_update_time, type: float, default: 1.0)
        The delay before any plot updates will be processed. This will prevent 
        multiple frequent update of plots.)- Composite creation settings


**User** settings
""""""""""""""""" 

- Update settings
    - Plot update time (key: user/auto_check_for_updates, type: bool, default: True)
        Flag to set the update check behaviour. By default, the GUI will check
        for a new version after starting up, if an active internet connection
        exists. This behaviour can be disabled by setting this flag to False.
- Composite creator settings
    - Mosaic tiling border width (key: user/mosaic_border_width, type: int, default: 0, unit: px)
        The width of the border inserted between adjacent frames in the 
        composite creation.
    - Mosaic border value (key: user/mosaic_border_value, type: float, default: 0)
        The value to be put in the border pixels in mosaics.
- Plot settings
    - Histogram lower outlier fraction (key: user/histogram_outlier_fraction_low, type: float, default: 0.02)
        The lower fraction of the histogram to be cropped when using the 
        "Crop histogram outliers" button in plots in the GUI. The value is
        the absolute fraction, i.e. the default of 0.02 will ignore the lowest
        2% of pixels when setting the colormap from the histogram.
    - Histogram high outlier fraction (key: user/histogram_outlier_fraction_high, type: float, default: 0.07)
        The high fraction of the histogram to be cropped when using the 
        "Crop histogram outliers" button in plots in the GUI. The value is
        the absolute fraction, i.e. the default of 0.07 will ignore the brightest
        7% of pixels when setting the colormap from the histogram. The default of
        0.07 is set to allow masking all the gaps in Eiger detectors by default.
    - Default colormap (key: user/cmap_name, type: str, default: Gray)
        The name of the default colormap to use. The name must be a valid
        matplotlib colormap name.
    - Default color for invalid data (key: user/cmap_nan_color, type: str, default: #9AFEFF)
        The RGB color code to use for invalid / missing data to distinguish it from the
        generic colormap and its data points.
- Plugins
    - Custom plugin paths (key: user/plugin_path, type: str, default: "")
        The names of custom paths where pydidas will look for plugins. Generic plugins
        and the generic plugin path is handled independently for greater clarity.
        Multiple paths can be added by appending them with a double semicolon ";;"
        as separator.

