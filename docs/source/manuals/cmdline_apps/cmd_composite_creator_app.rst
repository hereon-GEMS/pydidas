Tutorial for the CompositeCreatorApp
====================================

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

Selection of input data
-----------------------

First of all, the user needs to define whether the app will be run in 
``live_processing`` mode or not. This flag defines whether checks for file 
existance and size will be performed before the start of the processing. The
default setting is ``False`` which will enforce file system checks. This value
is stored in the ``live_processing`` :py:class:`Parameter <pydidas.core.Parameter>`
(see :ref:`composite_creator_app_params` for details).

The input data is defined through the files to use by defining the first and 
last file (or only one file if a file with multiple frames per file is used,
e.g. hdf5). The file(s) must be selected by the ``first_file`` and ``last_file``
Parameters. If not every file should be used but only every n-th file, this 
can be obtained by the ``file_stepping`` Parameter. pydidas will check the 
filenames for running numbers and determine the names automatically. 
Incrementing numbers do not need to be given by wildcards but must be separated
by a delimiter of "." or "_" or "-" or " ". 

Note that the first file must exist at the time the app is run because the file 
size will be used as reference for the future files.

For hdf5 files, the hdf5 dataset needs to be specified as well. The dataset 
can be given with the ``hdf5_key`` Parameter. The default is *entry/data/data* 
and if this is correct, the Parameter does not need to be specified. 
A subset of images from hdf5 files can be selected by using the 
``hdf5_first_image_num`` and ``hdf5_last_image_num`` Parameters with a frame 
stepping of ``hdf5_stepping``. 

See :ref:`composite_creator_app_params` for the detailed list of all Parameters.

Example 1: Loading a number of tiff files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Example 2: Loading a subset of frames from a single hdf5 file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
-----------------

A mask file can be used by activating the ``use_global_det_mask`` Parameter. 
This will instruct the app to apply the global mask to the data frame. For more
information on the global settings, please refer to :ref:`pydidas_qsettings`.
The filename for the mask file must be given with the *global/det_mask* value
and the value for the masked pixels by the *global/det_mask_val*.

The example below shows the code to instruct the app to use the 
*/scratch/det_mask.npy* file and substitute masked pixels with a value of zero.

.. code-block::

	>>> import pydidas
	>>> config = pydidas.core.PydidasQsettings()
	>>> config.set_value('global/det_mask', '/scratch/det_mask.npy')
	>>> config.set_value('global/det_mask_val', 0)
	>>> app = pydidas.apps.CompositeCreatorApp()
	>>> app.set_param_value('use_global_det_mask', True)
	
Using a background file
-----------------------

Usage of a background file (which will be subtracted from all frames) can be
activated by setting the ``use_bg_file`` Parameter to True.

The background file itself can be selected by specifying the ``bg_file`` 
Parameter. If a hdf5 file is selected, the dataset and frame can be given by
the ``bg_hdf5_key`` and ``bg_hdf5_frame``. These values default to 
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
	# be modified.
	
Using a region of interest
--------------------------

A region of interest (ROI) can be selected by defining the four values for 
lower and upper pixels in *x* and *y*. Usage of the ROI must be activated by
setting the Parameter ``use_roi`` to ``True``. The four boundaries can be 
defined by the ``roi_xlow``, ``roi_xhigh``, ``roi_ylow``, ``roi_yhigh`` values.
These values are modulated by the image width and height, respectively. A value
:code:`roi_yhigh = -5` corresponds to cropping the five rightmost pixel rows.
To use the full range, use ``None`` as value for the high boundaries and ``0``
for the low boundaries.

The defaults are `roi_xlow = 0`, `roi_xhigh = None`, `roi_ylow = 0`, and 
`roi_yhigh = None`. 




.. _composite_creator_app_params:

CompositeCreatorApp Parameters
------------------------------
