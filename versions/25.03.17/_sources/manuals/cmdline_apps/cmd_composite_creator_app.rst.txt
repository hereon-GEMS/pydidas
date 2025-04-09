..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Tutorial for the CompositeCreatorApp
====================================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Motivation
----------
The :py:class:`CompositeCreatorApp <pydidas.apps.CompositeCreatorApp>` is
designed to combine multiple images into a composite image. Only basic 
operations of binning and cropping are applied to the raw images.
Global offsets in the image data can be handled with a mask and background file.

.. note::

    While the use of different Parameters is handled in different sections of
    this manual, they must all be combined to use all capabilities of the 
    :py:class:`CompositeCreatorApp <pydidas.apps.CompositeCreatorApp>`. 

Globally controlled settings
----------------------------

Some settings used by the CompositeCreatorApp are controlled globally by pydidas. 
These are:

- The width of the border between images in pixels 
  (`user/mosaic_border_width`)
- The value of the border pixels (`user/mosaic_border_value`)
- The maximum image size in megapixels (`global/max_image_size`)
- The path for the detector mask file (`user/det_mask`)
- The pixel value for masked pixels (`user/det_mask_val`)

and for parallel processing additionally:

- The number of parallel worker processes (`global/mp_n_workers`)

Because these settings will typically be reused quite often, they have been
implemented as global :ref:`pydidas_qsettings`. The default is a border width 
of 0 pixels and a border pixel value of 0. The default maximum size is 100 Mpx. 
To modify these values, the user needs to create a QSettings instance and adjust 
these values, if required:

.. code-block::

    >>> import pydidas
    >>> config = pydidas.core.PydidasQsettings()
    >>> config.set_value('user/mosaic_border_width', 5)
    >>> config.set_value('user/mosaic_border_value', 1)
    >>> config.set_value('global/max_image_size', 250)

Setup of the CompositeCreatorApp
--------------------------------

This section describes the different input Parameters that can be used and gives
an overview of the :ref:`composite_creator_app_params` at the end of the 
section.

Selection of input data
^^^^^^^^^^^^^^^^^^^^^^^

First of all, the user needs to define whether the app will be run in 
:py:data:`live_processing` mode or not. This flag defines whether checks for 
file existance and size will be performed before the start of the processing. 
The default setting is :py:data:`False` which will enforce file system checks. 
This value is stored in the :py:data:`live_processing` 
:py:class:`Parameter <pydidas.core.Parameter>` 
(see :ref:`composite_creator_app_params` for details).

The input data is defined through the files to use by defining the first and 
last file (or only one file if a file with multiple frames per file is used,
e.g. hdf5). The file(s) must be selected by the :py:data:`first_file` and 
:py:data:`last_file` :py:class:`Parameters <pydidas.core.Parameter>`. If not 
every file single but only every n-th file should be processed, this 
can be defined by the :py:data:`file_stepping` Parameter. pydidas will check the 
filenames for running numbers and determine the names automatically. 
Incrementing numbers do not need to be given by wildcards but must be separated
by a delimiter of "." or "_" or "-" or " ". 

Note that the first file must exist at the time the app is run because the file 
size will be used as reference for the future files.

For hdf5 files, the hdf5 dataset needs to be specified as well. The dataset 
can be given with the :py:data:`hdf5_key` Parameter. The default is 
*entry/data/data* and if this is correct, the Parameter does not need to be 
specified. A subset of images from hdf5 files can be selected by using the 
:py:data:`hdf5_first_image_num` and :py:data:`hdf5_last_image_num` Parameters 
with a frame stepping of :py:data:`hdf5_stepping`. 

See :ref:`composite_creator_app_params` for the detailed list of all Parameters.

Example 1: Loading a number of tiff files
"""""""""""""""""""""""""""""""""""""""""

For the first example, we want to load every 3rd file from a running scan 
which produces tiff files named */scratch/scan_42/test_image_0000_suffix.tiff*
to */scratch/scan_42/test_image_1200_suffix.tiff*:

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('first_file', '/scratch/scan_42/test_image_0000_suffix.tiff')
    >>> app.set_param_value('last_file', '/scratch/scan_42/test_image_1200_suffix.tiff')
    >>> app.set_param_value('file_stepping', 3)
    >>> app.set_param_value('live_processing', True)
    
Once started, this app will run until the file 
*/scratch/scan_42/test_image_1200_suffix.tiff* has been created and processed.

Example 2: Loading a subset of frames from a single hdf5 file
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

For this example, we want to load every 2nd frame for the frames 10 to 30 from 
a single hdf5 file named */scratch/test_scan/some_file.h5*.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('first_file', '/scratch/test_scan/some_file.h5')
    >>> app.set_param_value('hdf5_first_image_num', 10)
    >>> app.set_param_value('hdf5_last_image_num', 30)
    >>> app.set_param_value('hdf5_stepping', 2)

Using a mask file
^^^^^^^^^^^^^^^^^

A mask file can be used by activating the :py:data:`use_global_det_mask` 
Parameter. This will instruct the app to apply the global mask to the data 
frame. For more information on the global settings, please refer to 
:ref:`pydidas_qsettings`. The filename for the mask file must be given with the 
*user/det_mask* value and the value for the masked pixels by the 
*user/det_mask_val*.

The example below shows the code to instruct the app to use the 
*/scratch/det_mask.npy* file and substitute masked pixels with a value of zero.

.. code-block::

    >>> import pydidas
    >>> config = pydidas.core.PydidasQsettings()
    >>> config.set_value('user/det_mask', '/scratch/det_mask.npy')
    >>> config.set_value('user/det_mask_val', 0)
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('use_global_det_mask', True)
    
Using a background file
^^^^^^^^^^^^^^^^^^^^^^^

Usage of a background file (which will be subtracted from all frames) can be
activated by setting the :py:data:`use_bg_file` Parameter to :py:data:`True`.

The background file itself can be selected by specifying the :py:data:`bg_file`
Parameter. If a hdf5 file is selected, the dataset and frame can be given by
the :py:data:`bg_hdf5_key` and :py:data:`bg_hdf5_frame`. These values default to 
*entry/data/data* and 0, respectively.

As example, let us use the 0th frame from the */scratch/scan_42/test.h5df5* 
file and the *entry/detector/data* dataset:

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('use_bg_file', True)
    >>> app.set_param_value('bg_file', '/scratch/scan_42/test.h5df5')
    >>> app.set_param_value('bg_hdf5_key', 'entry/detector/data')
    # Because the bg_hdf5_frame defaults to 0, this Parameter does not need to 
    # be modified:
    >>> app.get_param_value('bg_hdf5_frame')
    0
    
Using a region of interest
^^^^^^^^^^^^^^^^^^^^^^^^^^

A region of interest (ROI) can be selected by defining the four values for 
lower and upper pixels in *x* and *y*. Usage of the ROI must be activated by
setting the Parameter :py:data:`use_roi` to :py:data:`True`. The four 
boundaries can be defined by the :py:data:`roi_xlow`, :py:data:`roi_xhigh`, 
:py:data:`roi_ylow`, :py:data:`roi_yhigh` values. To use the full range, use 
:py:data:`None` as value for the high boundaries and :py:data:`0` for the low 
boundaries.
These values are modulated by the image width and height, respectively. A value 
of :py:data:`roi_yhigh = -5` thus corresponds to cropping the five rightmost pixel 
rows.

The defaults are :py:data:`roi_xlow = 0`, :py:data:`roi_xhigh = None`, 
:py:data:`roi_ylow = 0`, and :py:data:`roi_yhigh = None`. Note that if the ROI 
is activated, all four values are used and need to be set correctly.

As example, let the input image be of size 1000 x 1000 and let us select a 
ROI of pixel rows 5 to 1000 in height and the pixel columns 120 to 900 in 
width.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('use_roi', True)
    
    # Set up the ROI in x:
    >>> app.set_param_value('roi_xlow', 120)
    >>> app.set_param_value('roi_xhigh', 900)
    # Because we know the image size is 1000, a value of -100 for roi_xhigh 
    # has the same effect as 900.
    
    # Set up the ROI in y:
    >>> app.set_param_value('roi_ylow', 5)
    # We do not need to specify a roi_yhigh value because the default of None
    # corresponds to the full height as upper y boundary:
    >>> app.get_param_value('roi_yhigh') is None
    True

Use binning
^^^^^^^^^^^

Images can be binned to reduce their size in the composite image. This operation
is controlled by the :py:data:`binning` Parameter. A value of 1 corresponds to 
the input size and is ignored. The binning must be an integer value.

.. warning::

    If a combination of binning and ROI is used, the ROI pixel coordinates
    refer to the unbinned image.

As example, we set the binning factor to re-bin images by a factor of 4 in the 
composite image:

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('binning', 4)

Image thresholds
^^^^^^^^^^^^^^^^

The range of the composite image can be restricted by using thresholds. Two
thresholds for the upper and lower value must be given. To activate the use
of thresholds, set the :py:data:`use_thresholds` Parameter to :py:data:`True`. 
The values for the lower and upper thresholds are given by the 
:py:data:`threshold_low` and :py:data:`threshold_high` Parameters, respectively. 
A value of :py:data:`None` for a threshold will disable this specific
threshold. The default value for threshold values is :py:data:`None`.

As example, let us define an upper threshold of 42.0 and disable the lower
threshold.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('use_thresholds', True)
    >>> app.set_param_value('threshold_high', 42.0)
    
    # The lower thresholds's default value is None, which will make the app
    # ignore this threshold and it does not need to be changed:
    >>> app.get_param_value('threshold_low') is None
    True

Composite layout
^^^^^^^^^^^^^^^^

The arrangement of the images in the resulting mosaic image are controlled by
the :py:data:`composite_nx` and :py:data:`composite_ny` Parameters. These 
control the number of individual images in the *x* and *y* directions, 
respectively. The numbers must be chosen in a manner that the total number 
:math:`N_{total}` is less or equal to the product :math:`N_x * N_y` but is not 
unnecessary large. Mathematically, the two following conditions need to be 
fulfilled:

.. math::

    N_x * (N_y - 1) &< N_{total} <= N_x * N_y \\
    (N_x - 1) * N_y &< N_{total} <= N_x * N_y

One dimension can be automatically adjusted in size by using the value *-1*. The
default values are `Nx = 1` and `Ny = -1`\ .

In addition, raw images can be flipped or rotated prior to inserting them into
the composite. The :py:data:`composite_image_op` Parameter allows to select the 
type of operation to be performed (if any).

The *order* in which the images are inserted in the composite can be controlled
by the :py:data:`composite_xdir_orientation` and 
:py:data:`composite_ydir_orientation` Parameters which allow to select if images
are added from the left or right and top or bottom border, respectively.

As example, we want to create a composite with a number of twenty images in y 
and we want to adjust x automatically.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('composite_nx', -1)
    >>> app.set_param_value('composite_ny', 20) 

As second example, we want to create a composite of 90 images with 10 images 
in y and starting at the left side in x.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.set_param_value('composite_nx', 9)
    >>> app.set_param_value('composite_ny', 10) 
    >>> app.set_param_value('composite_xdir_orientation', 'right-to-left')

.. tip::

    Mathematically, it is equivalent to change the orientation of the raw 
    images or to change the order of the images in the composite. However,
    users might prefer to have the composite composed in the same orientation
    as their raw data scan.


Running the CompositeCreatorApp
-------------------------------

Once configured, the :py:class:`CompositeCreatorApp <pydidas.apps.CompositeCreatorApp>` 
is run like any pydidas app, as described in detail in 
:ref:`running_pydidas_applications`.

As a recap, to run the app serially, use the :py:meth:`run 
<pydidas.apps.CompositeCreatorApp.run` method:

    >>> import pydidas
    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> app.run()

To run it utilizing parallelization, set up an 
:py:class:`AppRunner <pydidas.multiprocessing.AppRunner>` and use its 
:py:meth`start <pydidas.multiprocessing.AppRunner.start>` method:

.. code-block::

    >>> app = pydidas.apps.CompositeCreatorApp()
    >>> runner = pydidas.multiprocessing.AppRunner(app)
    >>> runner.start()
    >>> app = runner.get_app()

If any thresholding should be performed, this operation needs to be called on 
the app by the :py:data:`apply_thresholds` method. Note that it is also 
possible to provide new threshold values. Please see the 
:py:meth:`apply_thresholds <pydidas.apps.CompositeCreatorApp.apply_thresholds>`
documentation for this.

Simply call the method to update the composite image with the thresholds
provided by the associated Parameters:

.. code-block::

    # To apply the thresholds
    >>> app.apply_threshold()

    # to apply new threshold values:
    >>> app.apply_thresholds(low=0, high=42)

.. warning::

    If the :py:data:`use_thresholds` Parameter is value :py:data:`False`, 
    calling the :py:meth:`apply_thresholds 
    <pydidas.apps.CompositeCreatorApp.apply_thresholds>` method will have no 
    effect.

Accessing results
-----------------

After running the 
:py:class:`CompositeCreatorApp <pydidas.apps.CompositeCreatorApp>`, results can
be accessed either directly to store the object for further use in the Python
console or script or they can be stored.

Accessing results within Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The results can be accessed through the :py:data:`composite` property which 
will return the array with the image data:

.. code-block::

    >>> image = app.composite
    >>> type(image)
    numpy.ndarray
    
Exporting results
^^^^^^^^^^^^^^^^^

Results can be exported by using the :py:meth:`export_image 
<pydidas.apps.CompositeCreatorApp.export_image>` method in any format known to 
pydidas. The format is determined automatically from the extension:

.. code-block::

    # To export in numpy format:
    >>> app.export_image('/scratch/image.npy')
    
    # or to export as tiff
    >>> app.export_image('/scratch/image.tiff')

.. _composite_creator_app_params:

Complete list of CompositeCreatorApp Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: ../global/composite_creator_app_params.rst
