.. _scan_setup:

The ScanSetup class
===================

Introduction
------------

The :py:class:`ScanSetup <pydidas.experiment.scan_setup.scan_setup._ScanSetup>`
is the pydidas Singleton instance of the ``_ScanSetup`` class. It is
used for storing and accessing global information about the scan layout.

Stored information include

    - Dimensionality (for arranging results)
    - Name (for metadata and titles only)
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
given in :ref:`scan_setup_parameters`\ .

Its instance can be obtained by calling the following code:

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.experiment.ScanSetup()
    

Configuring the ScanSetup
-------------------------

Global Parameters
^^^^^^^^^^^^^^^^^

The :py:class:`ScanSetup <pydidas.experiment.scan_setup.scan_setup._ScanSetup` 
has two *global* Parameters for the scan title and the number of dimensions, 
referenced by the Parameter keys ``scan_name`` and ``scan_dim``:

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.experiment.ScanSetup()
    >>> SCAN.set_param_value('scan_name', 'Test_42')
    >>> SCAN.set_param_value('scan_dim', 2)
    
.. note::

    The number of dimensions in the scan is limited to 4 which should be 
    sufficient for all applications. If you have a specific application which
    required a larger number of dimensions, please get in contact with the 
    pydidas development team to discuss your needs.

Parameters for each dimension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Parameters for each dimension are distinguished by a trailing *_1*, *_2*, 
*_3*, or *_4*, respectively. In the description, the numbers are substituted
by a *_i* for generality. It is important to preserve the order from the scan
to have the results in the correct structure.

Each dimension is described by a total of five Parameters:

.. list-table::
    :widths: 15 10 15 60
    :header-rows: 1
    :class: tight-table
    
    * - name
      - type
      - default
      - description
    * - scan_dir_i
      - str
      - [empty str]
      - The axis name for scan direction 1. This information will only be used 
        for labelling.
    * - n_points_i
      - int
      - 0
      - The number of scan points in scan direction *i*.
    * - delta_i
      - float
      - 2
      - The step width between two scan points in scan direction *i*.
    * - offset_i
      - float
      - 0
      - The coordinate offset of the movement in scan direction *i* (i.e. the 
        counter / motor position for scan step #0)
    * - unit_i
      - str
      - [empty str]
      - The unit of the movement / steps / offset in scan direction *i*.

.. note::

    The only Parameter that must be set for each dimension is the number of 
    points ``n_points_i`` to allow pydidas to organize results in the correct
    grid.
    
As example, let us configure a scan with 2 dimensions. The slow motor is the 
x-axis with 25 scan points in the range [-12.0 mm, -11.5 mm, ..., 12.0 mm] and 
the fast motor is the z-axis with 100 points in the range [150 nm, 225, nm, ..., 
7575 nm]:

.. code-block::

    >>> import pydidas
    >>> SCAN = pydidas.experiment.ScanSetup()
    >>> SCAN.set_param_value('scan_dim', 2)
    >>> SCAN.set_param_value('scan_dir_1', 'x')
    >>> SCAN.set_param_value('n_points_1', 25)
    >>> SCAN.set_param_value('delta_1', 0.5)
    >>> SCAN.set_param_value('offset_1', -12.0)
    >>> SCAN.set_param_value('unit_1', 'mm')
    >>> SCAN.set_param_value('scan_dir_2', 'x')
    >>> SCAN.set_param_value('n_points_2', 100)
    >>> SCAN.set_param_value('delta_2', 75)
    >>> SCAN.set_param_value('offset_2', 150)
    >>> SCAN.set_param_value('unit_2', 'nm')


Import of scan metadata
-----------------------

pydidas includes the option to import metadata from beamlines directly. Please
contact your beamline local contact for details.

Import functions will be implemented as required and depending on the scan
metadata available at the beamlines.

.. _scan_setup_parameters:

List of all ScanSetup Parameters
--------------------------------

.. include:: ./scan_setup_params.rst