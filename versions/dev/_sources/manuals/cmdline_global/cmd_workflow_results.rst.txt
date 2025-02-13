..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _workflow_results:

The WorkflowResults class
=========================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Introduction
------------

The :py:class:`WorkflowResults <pydidas.workflow.WorkflowResults>` is the
Singleton instance of the
:py:class:`ProcessingResults <pydidas.workflow.ProcessingResults>`.
It is used for managing the processing results.

This class does not need any configuration as the layout of the results are
determined based on

  1. The information about the scan from the
     :py:class:`ScanContext <pydidas.contexts.scan.Scan>`
     class.
  2. The information about the processing steps from the
     :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`.

The :py:class:`WorkflowResults <pydidas.workflow.WorkflowResults>`
is only responsible for storing and presenting the results.

To access the instance, execute the following code:

.. code-block::

    >>> import pydidas
    >>> RESULTS = pydidas.workflow.WorkflowResults()

The public interface is detailed in the class documentation
(:py:class:`WorkflowResults <pydidas.workflow.WorkflowResults>`)
and this document will focus on the use case to access results.

Getting information about the results
-------------------------------------

To get more information about the results, the
:py:class:`WorkflowResults <pydidas.workflow.ProcessingResults>`
class has several properties to get general information about the stored results


.. list-table::
    :widths: 25 75
    :header-rows: 1
    :class: tight-table

    * - property name
      - description
    * - labels
      - The labels of all the stored result :py:class:`Datasets <pydidas.core.Dataset>`.
        These labels are only used as captions and for user information.
    * - shapes
      - The array shapes of the stored results.
    * - ndims
      - The number of dimensions of the stored results.

These properties each return a dictionary with the node IDs as keys and the
respective properties as values.

.. note::

    All information needs to be accessed through the node ID of the
    corresponding node in the
    :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`.

An example of what the property values look like is given below:

.. code-block::

    >>> import pydidas
    >>> RESULTS = pydidas.workflow.WorkflowResults()

    >>> RESULTS.labels
    {1: 'Azimuth full', 2: 'azimuthal range'}

    >>> RESULTS.shapes
    {1: (21, 4, 1000), 2: (21, 4, 1000)}

    >>> RESULTS.ndims
    {1: 3, 2: 3}

Accessing results
-----------------

Accessing a full Plugin Dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Metadata
""""""""

The metadata of a node ID's Dataset can be accessed using the
:py:meth:`get_result_metadata(node_id)
<pydidas.workflow.ProcessingResults.get_result_metadata>`
method. It will return a dictionary with the metadata keys and their respective
data:

.. code-block::

    >>> import pydidas
    >>> RESULTS = pydidas.workflow.WorkflowResults()
    >>> RESULTS.get_result_metadata(1)
    {'axis_labels': {0: 'Scan position', 1: 'Repeat', 2: '2theta'},
     'axis_units': {0: 'm', 1: 'number', 2: 'deg'},
     'axis_ranges': {0: array([1.  , 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09, 1.1 ,
             1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.2 ]),
      1: array([0., 1., 2., 3.]),
      2: array([1.88768122e-02, 5.66304366e-02, 9.43840610e-02, ...,
             3.76592403e+01, 3.76969939e+01, 3.77347476e+01])},
     'metadata': {}}

Note that the metadata is also included in the full :py:class:`Dataset <pydidas.core.Dataset>`
and this method is primarily intended if the user needs the metadata without
creating a copy of the full data.

Generic Data
""""""""""""

The :py:meth:`get_results(node_id) <pydidas.workflow.ProcessingResults.get_results>`
method is available to access the full Dataset with the results of a Plugin.
The calling parameter is the node ID of the particular Plugin corresponding to
the results:

.. automethod:: pydidas.workflow.ProcessingResults.get_results
    :noindex:

An example is given below:

.. code-block::

    >>> import pydidas
    >>> RESULTS = pydidas.workflow.WorkflowResults()
    >>> res1 = RESULTS.get_results(1)
    >>> type(res1)
    pydidas.core.dataset.Dataset
    >>> res1.shape
    (21, 4, 1000)
    >>> res1
    Dataset(
    axis_labels: {
        0: 'Scan position'
        1: 'Repeat'
        2: '2theta'},
    axis_ranges: {
        0: array([1.  , 1.01, 1.02, ..., 1.18, 1.19, 1.2 ])
        1: array([0., 1., 2., 3.])
        2: array([1.88768122e-02, 5.66304366e-02, 9.43840610e-02, ...,
                  3.76592403e+01, 3.76969939e+01, 3.77347476e+01])},
    axis_units: {
        0: 'm'
        1: 'number'
        2: 'deg'},
    metadata: {},
    array([[[0.04860432, 0.07182986, 0.13712727, ..., 0.70990837,
             0.54952693, 0.3378173 ],
            [0.        , 0.        , 0.08358723, ..., 0.88032216,
             0.6159408 , 0.        ],
            [0.        , 0.01557512, 0.03591977, ..., 0.8177717 ,
             0.750647  , 0.52528936],
            [0.        , 0.00159723, 0.05272374, ..., 0.91826296,
             0.51986897, 1.0225816 ]],

           ...,

           [[0.        , 0.        , 0.        , ..., 0.69608676,
             0.7253706 , 0.48062864],
            [0.17440052, 0.2533884 , 0.02119193, ..., 0.6548988 ,
             0.41295865, 0.7492686 ],
            [0.        , 0.14259325, 0.13415995, ..., 0.76227677,
             0.5542096 , 0.47257382],
            [0.13894346, 0.06785214, 0.05374042, ..., 0.85051745,
             1.200285  , 0.7369508 ]]], dtype=float32)
    )

Flattened scan dimensions
"""""""""""""""""""""""""

For some applications, it might be interesting to ignore the detailed shape of
the scan and flatten the scan to a *timeline*. The
:py:meth:`get_results_for_flattened_scan(node_id)
<pydidas.workflow.ProcessingResults.get_results_for_flattened_scan>`
method allows to get a Dataset with all the scan dimensions flattened to a
single dimension renamed to *timeline*:

.. automethod:: pydidas.workflow.ProcessingResults.get_results_for_flattened_scan
    :noindex:

An example is given below:

.. code-block::

    >>> import pydidas
    >>> RESULTS = pydidas.workflow.WorkflowResults()

    # Get the result in the generic shape:
    >>> res1 = RESULTS.get_results(1)
    >>> res1.shape
    (21, 4, 1000)

    # Get the results with the first two dimensions (from the scan) concatenated
    # to a single dimension:
    >>> res1_flat = RESULTS.get_results_for_flattened_scan(1)
    >>> res1_flat.shape
    (84, 1000)
    >>> res1_flat
    Dataset(
    axis_labels: {
        0: 'Scan timeline'
        1: '2theta'},
    axis_ranges: {
        0: array([ 0,  1,  2, ..., 81, 82, 83])
        1: array([1.88768122e-02, 5.66304366e-02, 9.43840610e-02, ...,
                  3.76592403e+01, 3.76969939e+01, 3.77347476e+01])},
    axis_units: {
        0: ''
        1: 'deg'},
    metadata: {},
    array([[0.04860432, 0.07182986, 0.13712727, ..., 0.70990837, 0.54952693,
            0.3378173 ],
           [0.        , 0.        , 0.08358723, ..., 0.88032216, 0.6159408 ,
            0.        ],
           [0.        , 0.01557512, 0.03591977, ..., 0.8177717 , 0.750647  ,
            0.52528936],
           ...,
           [0.17440052, 0.2533884 , 0.02119193, ..., 0.6548988 , 0.41295865,
            0.7492686 ],
           [0.        , 0.14259325, 0.13415995, ..., 0.76227677, 0.5542096 ,
            0.47257382],
           [0.13894346, 0.06785214, 0.05374042, ..., 0.85051745, 1.200285  ,
            0.7369508 ]], dtype=float32)
    )

Accessing a data subset
^^^^^^^^^^^^^^^^^^^^^^^

For convenience, a method to access only a subset of the data is implemented as
well:

.. automethod:: pydidas.workflow.ProcessingResults.get_result_subset
    :noindex:

This method is interesing if the user wants to access a specific subset in the
flattened data, for example the results for the frames 40 to 55 of the
experiment. This can easily be done using the :py:meth:`get_result_subset
<pydidas.workflow.ProcessingResults.get_result_subset>`
method, as demonstrated in the example below:


.. code-block::

    >>> import pydidas
    >>> RESULTS = pydidas.workflow.WorkflowResults()

    # Define the slice to get the frames 40 to 55 (note that the final index is not included):
    >>> s = slice(40, 56, 1)

    # Note that the slices must be a tuple, so we need to create a tuple with
    # the slice object:
    >>> res1 = RESULTS.get_result_subset(1, (s, ), flattened_scan_dim=True)
    >>> res1.shape
    (16, 1000)

    >>> res1
    Dataset(
    axis_labels: {
        0: 'Scan timeline'
        1: '2theta'},
    axis_ranges: {
        0: array([40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55])
        1: array([1.88768122e-02, 5.66304366e-02, 9.43840610e-02, ...,
                  3.76592403e+01, 3.76969939e+01, 3.77347476e+01])},
    axis_units: {
        0: ''
        1: 'deg'},
    metadata: {},
    array([[0.        , 0.14259325, 0.13415995, ..., 0.76227677, 0.5542096 ,
            0.47257382],
           [0.13894346, 0.06785214, 0.05374042, ..., 0.85051745, 1.200285  ,
            0.7369508 ],
           [0.04860432, 0.07182986, 0.13712727, ..., 0.70990837, 0.54952693,
            0.3378173 ],
           ...,
           [0.        , 0.07157321, 0.07099393, ..., 0.6823842 , 1.1303366 ,
            0.49410635],
           [0.        , 0.01834229, 0.13609774, ..., 0.7423366 , 0.48968357,
            1.0344652 ],
           [0.        , 0.15469511, 0.00470399, ..., 0.5591186 , 0.9095903 ,
            0.7084448 ]], dtype=float32)
    )

Saving results
--------------

Saving the results is achieved via the :py:meth:`save_results_to_disk
<pydidas.workflow.ProcessingResults.save_results_to_disk>`
method:

.. automethod::
    pydidas.workflow.ProcessingResults.save_results_to_disk
    :noindex:

For now, the only available saver is 'HDF5' and additional savers will be added
based on users' requests if deemed feasible with the file system structure.

An example is given below:


.. code-block::

    >>> import pydidas
    >>> RESULTS = pydidas.workflow.WorkflowResults()
    >>> RESULTS.save_results_to_disk('/scratch/scan42_results', 'HDF5')

    # Now that the files have been written, trying to write to the same directory
    # will raise an Exception
    >>> RESULTS.save_results_to_disk('/scratch/scan42_results', 'HDF5')
    FileExistsError: The specified directory "d:/tmp/new3" exists and is not empty. Please
    select a different directory.

    # If we set the overwrite flag, we can write to the same directory again:
    >>> RESULTS.save_results_to_disk('/scratch/scan42_results', 'HDF5', overwrite=True)
