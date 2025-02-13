..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _scan_context:

The ScanContext class
=====================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Introduction
------------

The :py:class:`ScanContext` is the pydidas Singleton instance of the 
:py:class:`Scan <pydidas.contexts.scan.Scan>` 
class. It is used for storing and accessing global information about the scan 
layout and generic infomation like title, directory and file naming patterns.

Stored information include

    - Dimensionality (for arranging results)
    - Name (for metadata and titles only)
    - Directory (for data loading)
    - Filename pattern (for data loading)
    - Scan multiplicity (the number of each frames at each scan point).
    - Starting index of files/frames
    - Index stepping    
    - Information for each scan dimension

        - Name for the scan dimension (for reference, e.g. motor name, time)
        - Number of scan points
        - Step width between two scan points
        - Offset of the first scan points
        - Unit of the scan direction
    
These information allow to arrange the processed datasets in the correct order
and to add metadata about the scan to plots and stored datasets.

All objects are stored as :py:class:`Parameters <pydidas.core.Parameter>` and
can be accesses as described in the basic tutorial. A full list of Parameters is
given in :ref:`List of all ScanContext Parameters <scan_context_parameters>`\ .

Its instance can be obtained by calling the following code:

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.contexts.ScanContext()
    

Configuring the ScanContext
---------------------------

Global Parameters
^^^^^^^^^^^^^^^^^

The :py:class:`ScanContext <pydidas.contexts.scan.Scan>` 
has *global* Parameters for generic information, listed in detail below:


.. list-table::
    :header-rows: 1
    :class: tight-table    

    * - ScanContext Parameter name
      - data type
      - description
    * - scan_dim
      - int
      - The number of dimensions in the scan.
    * - scan_title
      - str
      - The scan title. This Parameter is only used for plot titles and
        metadata.
    * - scan_base_directory
      - pathlib.Path
      - The base directory for finding the files of the scan. 
    * - scan_name_pattern
      - str
      - The naming pattern of the scan files. Use hashes '#' for wildcards 
        which will be replaced by indices.
    * - scan_start_index
      - int
      - The starting index to subsititute the wildcards in the name pattern.
    * - scan_multiplicity
      - int
      - The number of frames acquired at each scan point.
        Note: If you want to handle multiple images individually, add them as 
        an additional scan dimension.
    * - scan_multi_image_handling
      - str
      - Flag how to handle multiple images. Choices are averaging or summation.

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.contexts.ScanContext()
    >>> SCAN.set_param_value('scan_name', 'Test_42')
    >>> SCAN.set_param_value('scan_dim', 2)
    >>> SCAN.set_param_value('scan_base_directory', '/home/user/dir_to_data')
    
.. note::

    The number of dimensions in the scan is limited to 4 which should be 
    sufficient for all applications. If you have a specific application which
    required a larger number of dimensions, please get in contact with the 
    pydidas development team to discuss your needs.

Parameters for each dimension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Parameters for each dimension are distinguished by a dimension index in the
Parameter names, respectively. In the description, the numbers are substituted
by an *i* for generality. It is important to preserve the scan order from the
experiment to have the results in the correct structure.

Each dimension is described by a total of five Parameters:

.. list-table::
    :widths: 22 10 10 58
    :header-rows: 1
    :class: tight-table
    
    * - name
      - type
      - default
      - description
    * - scan_dim{i}_label
      - str
      - ""
      - The axis name for scan direction *i*. This information will only be used 
        for labelling.
    * - scan_dim{i}_n_points
      - int
      - 0
      - The number of scan points in scan direction *i*.
    * - scan_dim{i}_delta
      - float
      - 2
      - The step width between two scan points in scan direction *i*.
    * - scan_dim{i}_offset
      - float
      - 0
      - The coordinate offset of the movement in scan direction *i* (i.e. the 
        counter / motor position for scan step #0)
    * - scan_dim{i}_unit
      - str
      - ""
      - The unit of the movement / steps / offset in scan direction *i*. This 
        value will only be used for labelling these numbers.

.. note::

    The only Parameter that must be set for each dimension is the number of 
    points :py:data:`scan_dim{i}_n_points` to allow pydidas to organize results 
    in the correct grid.
    
As example, let us configure a scan with 2 dimensions. The slow motor is the 
x-axis with 25 scan points in the range [-12.0 mm, -11.5 mm, ..., 12.0 mm] and 
the fast motor is the z-axis with 100 points in the range [150 nm, 225, nm, ..., 
7575 nm]:

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.contexts.ScanContext()
    >>> SCAN.set_param_value('scan_dim', 2)
    >>> SCAN.set_param_value('scan_dim0_label', 'x')
    >>> SCAN.set_param_value('scan_dim0_n_points', 25)
    >>> SCAN.set_param_value('scan_dim0_delta', 0.5)
    >>> SCAN.set_param_value('scan_dim0_offset', -12.0)
    >>> SCAN.set_param_value('scan_dim0_unit', 'mm')
    >>> SCAN.set_param_value('scan_dim1_label', 'x')
    >>> SCAN.set_param_value('scan_dim1_n_points', 100)
    >>> SCAN.set_param_value('scan_dim1_delta', 75)
    >>> SCAN.set_param_value('scan_dim1_offset', 150)
    >>> SCAN.set_param_value('scan_dim1_unit', 'nm')


Import of scan metadata
-----------------------

pydidas includes the option to import metadata from beamlines directly. Please
contact your beamline local contact for details.

Import functions will be implemented as required and depending on the scan
metadata available at the beamlines.

.. _scan_context_parameters:

.. include:: ../global/scan_context_params.rst