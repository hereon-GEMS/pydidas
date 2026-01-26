..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Tutorial for the DirectorySpyApp
================================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Motivation
----------
The :py:class:`DirectorySpyApp <pydidas.apps.DirectorySpyApp>` is
designed to keep track of the files in a directory and notify the user if a new
file (with a specific filename pattern) has been created or changed.
If configured to do so, it will also supply the image data of the latest image
as well as the filename.

.. note::

    While the use of different Parameters is handled in different sections of
    this manual, they must all be combined to use all capabilities of the 
    :py:class:`DirectorySpyApp <pydidas.apps.DirectorySpyApp>`. 


Setup of the DirectorySpyApp
----------------------------

This section describes the different input Parameters that can be used and gives
an overview of the :ref:`directory_spy_app_params` at the end of the 
section.

Selection of input data
^^^^^^^^^^^^^^^^^^^^^^^

First of all, the user must specify the :py:data:`directory_path` Parameter to
define the working directory. In addition, the user must decide whether the app 
will scan for all new files the selected directory or only for files matching 
a specific filename pattern. In the latter case, the :py:data:`filename_pattern` 
Parameter is used and must include the filename pattern with hashes "#" for 
the counting variable. 

The file finding behaviour is controlled through the :py:data:`scan_for_all` 
Parameter. If set to :py:data:`True`, the app will look for all files in a 
directory. If :py:data:`False`, it will only look for incremental counts 
according to the filename pattern and the current index.

.. note::

    Using the :py:data:`scan_for_all=True` setting will be slow in directories
    with many files and it is not recommended.
    
The :py:data:`filename_pattern` Parameter only includes the filename with 
hash characters as wildcards. The number of wildcard characters must correspond
to the length of the numbers to be replaced and it will be filled with leading
zeros.

.. note::
    Only a single set of wildcars is accepted. Please leave all other numbers 
    in place.

If HDF5 files are used, the dataset to use must be specified with the 
:py:data:`hdf5_key`. The frame cannot be selected as the DirectorySpyApp will 
always show the latest frame. 

See :ref:`composite_creator_app_params` for the detailed list of all Parameters.

Example 1: Scanning for all files
"""""""""""""""""""""""""""""""""

For the first example, we want to scan for all new files in the 
*/scratch/scan_42/* directory. We expect Hdf5 files with the data in the 
*entry/other_data/data/* dataset.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.DirectorySpyApp()
    >>> app.set_param_value('scan_for-all', True)
    >>> app.set_param_value('directory_path', '/scratch/scan_42/')
    >>> app.set_param_value('hdf5_key', '/entry/other_data/data')

Example 2: Scanning for new tiff files
""""""""""""""""""""""""""""""""""""""

For this example, we want to load Tiff files from the */scratch/test_scan/*
directory. The files are named *test_scan_01_0001.tiff*,
*test_scan_01_0002.tiff* etc.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.DirectorySpyApp()
    # scan_for_all is False by default, no need to set it.
    >>> app.set_param_value('directory_path', '/scratch/test_scan')
    >>> app.set_param_value('filename_pattern', 'test_scan_01_####.tiff')


Detector mask and background image
----------------------------------

Using a mask file
^^^^^^^^^^^^^^^^^

A mask file can be used by activating the :py:data:`use_det_mask` 
Parameter. This will instruct the app to apply the detector mask to the data 
frame. 

To modify the detector mask used by the DirectorySpyApp, set the 
:py:data:`detector_mask_file` Parameter to point to the mask file. The value
taken for masked pixels is controlled by the :py:data:`det_mask_val` Parameter. 
The default value is 0.

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.DirectorySpyApp()
    >>> app.set_param_value("use_detector_mask", True)
    >>> app.set_param_value("detector_mask_file", '/home/user/data/detector_mask.npy')   

    
Using a background file
^^^^^^^^^^^^^^^^^^^^^^^

Usage of a background file (which will be subtracted from all frames) can be
activated by setting the :py:data:`use_bg_file` Parameter to True.

The background file itself can be selected by specifying the :py:data:`bg_file`
Parameter. If a hdf5 file is selected, the dataset and frame can be given by
the :py:data:`bg_hdf5_key` and :py:data:`bg_hdf5_frame` Parameters. These 
values default to *entry/data/data* and 0, respectively.

As example, let us use the first frame (i.e. zero) from the 
*/scratch/scan_42/test.h5df5* file and the *entry/detector/data* dataset:

.. code-block::

    >>> import pydidas
    >>> app = pydidas.apps.DirectorySpyApp()
    >>> app.set_param_value('use_bg_file', True)
    >>> app.set_param_value('bg_file', '/scratch/scan_42/test.h5df5')
    >>> app.set_param_value('bg_hdf5_key', 'entry/detector/data')
    # Because the bg_hdf5_frame defaults to 0, this Parameter does not need to 
    # be modified:
    >>> app.get_param_value('bg_hdf5_frame')
    0

Running the DirectorySpyApp
---------------------------

Once configured, the :py:class:`DirectorySpyApp <pydidas.apps.DirectorySpyApp>` 
is run like any pydidas app, as described in detail in 
:ref:`running_pydidas_applications`.

.. warning::
    Because the DirectorySpyApp does not use tasks and is running indefinitely
    until stopped, it **cannot** be run serially.
    

To run it utilizing parallelization, set up an 
:py:class:`AppRunner <pydidas.multiprocessing.AppRunner>` and use the 
:py:meth:`start <pydidas.multiprocessing.AppRunner.start>` method:

.. code-block::

    >>> app = pydidas.apps.DirectorySpyApp()
    >>> runner = pydidas.multiprocessing.AppRunner(app)
    >>> runner.start()
    
Accessing results
-----------------

:py:class:`DirectorySpyApp <pydidas.apps.DirectorySpyApp>` results can
be only be accessed indirectly within Python.

Accessing results within Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The results can be accessed through the :py:data:`image`, :py:data:`filename` 
and :py:data:`image_metadata` properties. Note that this requires to connect 
the AppRunner :py:data:`sig_results` with the local app's 
:py:meth:`multiprocessing_store_results 
<pydidas.apps.DirectorySpyApp.multiprocessing_store_results>` method:

.. code-block::

    >>> app = pydidas.apps.DirectorySpyApp()
    >>> runner = pydidas.multiprocessing.AppRunner(app)
    >>> runner.sig_results.connect(app.multiprocessing_store_results)    
    >>> runner.start()
    >>> app.image
    array([[0.98215663, 0.30682687, 0.21160315, ..., 0.2604671 , 0.59461537,
        0.09863754],
       [0.51141869, 0.32276036, 0.43406916, ..., 0.02741798, 0.91533116,
        0.79145334],
       [0.1881628 , 0.4708237 , 0.14207525, ..., 0.26664729, 0.68337244,
        0.83566994],
       ...,
       [0.6985084 , 0.58230171, 0.11641333, ..., 0.3299515 , 0.29834082,
        0.19949315],
       [0.54581434, 0.96941275, 0.21216339, ..., 0.26659825, 0.13700608,
        0.01721194],
       [0.74946649, 0.24262777, 0.94001868, ..., 0.29572706, 0.68824381,
        0.61529555]])
    >>> app.filename
    /scratch/test_scan/test_scan_01_0004.tiff

.. _directory_spy_app_params:

DirectorySpyApp Parameters
--------------------------

    scan_for_all (type: bool, default: False)
        Flag to toggle scanning for all new files or only for files matching
        the input pattern (defined with the Parameter 
        :py:data:`filename_pattern`).
    filename_pattern (type: pathlib.Path, default: <empty Path>)
        The pattern of the filename. Use hashes "#" for wildcards which will
        be filled in with numbers. This Parameter must be set if 
        :py:data:`scan_for_all` is :py:data:`False`.
    directory_path (type: pathlib.Path, default: <empty Path>)
        The absolute path of the directory to be used. 
    hdf5_key (type: Hdf5key, default: entry/data/data)
        Used only for hdf5 files: The dataset key. 
    use_global_det_mask (type: bool, default: True)
        Keyword to enable or disable using the global detector mask as
        defined by the global mask file and mask value. 
    use_bg_file (type: bool, default: False)
        Keyword to toggle usage of background subtraction. 
    bg_file (type: pathlib.Path, default: <empty Path>)
        The name of the file used for background correction. 
    bg_hdf5_key (type: Hdf5key, default: entry/data/data)
        Required for hdf5 background image files: The dataset key with the
        image for the background file. 
    bg_hdf5_frame (type: int, default: 0)
        Required for hdf5 background image files: The image number of the
        background image in the dataset. 
        