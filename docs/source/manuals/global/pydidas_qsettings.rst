

- Multiprocessing settings
    - Number of MP workers (key: mp_n_workers, type: int, default: 4)
        The number of multiprocessing workers. Note that this number should not 
        be set too high for two reasons:
        1. File reading processes interfere with each other if too many are 
        active at once.
        2. pyFAI already inherently uses parallelization and you can only gain 
        limited performance increases for multiple parallel processes.
    - Shared buffer size limit (key: shared_buffer_size, type: float, default: 100, unit: MB)
        A shared buffer is used to efficiently transport data between the main 
        App and multiprocessing Processes. This buffer must be large enough to 
        store at least one instance of all result data.
    - Buffer dataframe limit (key: shared_buffer_max_n, type: int, default: 20)
        The maximum number of datasets in the buffer. A dataset consists of all 
        results for one frame. For performance reasons, the buffer should not 
        be too large as this is only a temporary buffer.
- Detector settings
    - Detector mask file (key: det_mask, type: Path, default: '' [empty Path])
        The path to the detector mask file.
    - Detector mask value (key: det_mask_val, type: float, default: 0)
        The value to be used for the pixels masked on the detector. Note that 
        this value will only be used for displaying the images. For pyFAI 
        integration, the pixels will be fully masked and not be included.
- Composite creation settings
    - Mosaic tiling border width (key: mosaic_border_width, type: int, default: 0, unit: px)
        The width of the border inserted between adjacent frames in the 
        composite creation.
    - Mosaic border value (key: mosaic_border_value, type: float, default: 0)
        The value to be put in the border pixels in mosaics.
    - Mosaic maximum size (key: mosaic_max_size, type: float, default: 100, unit: Mpx)
        The maximum size (in megapixels) of mosaic images.

- Plotting settings
    - Plot update time (key: plot_update_time, type: float, default: 1.0)
        The delay before any plot updates will be processed. This will prevent 
        multiple frequent update of plots.)