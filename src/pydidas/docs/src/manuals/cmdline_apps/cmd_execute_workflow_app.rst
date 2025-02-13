..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _execute_workflow_app:

Tutorial for the ExecuteWorkflowApp
===================================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Motivation
----------

The :py:class:`ExecuteWorkflowApp <pydidas.apps.ExecuteWorkflowApp>` is one of 
the most important objects in pydidas as it allows to process workflows. Note 
that most of the configuration is not performed by the ExecuteWorkflowApp itself
but by the global objects for 
:py:class:`ScanContext <pydidas.contexts.scan.Scan>`,
:py:class:`DiffractionExperimentContext 
<pydidas.contexts.diff_exp.DiffractionExperimentContext>`,
and :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`.

Documentation on the use of these objects is given in :ref:`scan_context`,
:ref:`diffraction_exp_context` and :ref:`workflow_tree`, respectively.

Globally controlled settings
----------------------------

Some settings for parallel processing additionally used by the 
ExecuteWorkflowApp are controlled globally by pydidas. These are:

- The number of parallel worker processes (`global/mp_n_workers`)
- The size of the data exchange buffer (in MB) (`global/shared_buffer_size`)
- The number of datasets which can be held in the buffer 
  (`global/shared_buffer_max_n`)

Because these settings will typically be set up once for each workstation and
then reused quite often, they have been implemented as global 
:ref:`pydidas_qsettings`. 

The default values for multiprocessing are 4 worker processes, a maximum shared 
buffer size of 100 MB and a maximum of 20 datasets in the buffer. These settings
should normally work quite well and it is not recommended to change them without
thorough thought. 

.. warning::
    
    For standard applications, the number of independent processes should not be 
    increased because pyFAI uses inherent multiprocessing in addition to the 
    pydidas multiprocessing and synergies can only be achieved by parallelizing 
    the processing and data loading.
    
    Loading from disk with too many processes also slows all processes down as
    the processes interfere with each other for file access to disk. 
    
    Only plugins with long serial computations (e.g. fitting, depending on 
    the implementation) might benefit from more processes but this has to be 
    weighted against disk access to the raw data.
    
The global detector mask file must be specified with the full and absolute path.
The detector mask can be supplied in any image format.

To modify these values, the user needs to create a QSettings instance and adjust 
these values, if required:

.. code-block::

    >>> import pydidas
    >>> config = pydidas.core.PydidasQsettings()
    >>> config.set_value('global/mp_n_workers', 2)

Setup of the ExecuteWorkflowApp
-------------------------------

The ExecuteWorkflowApp has only a very limited number of Parameters because it 
uses the aforementioned objects (
:py:class:`ScanContext <pydidas.contexts.scan.Scan>`,
:py:class:`DiffractionExperimentContext 
<pydidas.contexts.diff_exp.DiffractionExperimentContext>`,
and :py:class:`WorkflowTree <pydidas.workflow.ProcessingTree>`)
which include most of the required configuration.

In the app, only the flags for *live processing* and for automatic saving of
results need to be set.

Live processing
^^^^^^^^^^^^^^^

The live processing flag determines whether pydidas will check all files at
the start of processing or accept file names without corresponding written 
files. This flag is modified using the :py:data:`live_processing` Parameter:

    >>> import pydidas
    >>> app = pydidas.apps.ExecuteWorkflowApp()
    >>> app.set_param_value('live_processing', True)

Automatic saving
^^^^^^^^^^^^^^^^

The ExecuteWorkflowApp includes the possibility to write results dynamically to
disk as soon as they have been processed. The behaviour is controlled by the 
:py:data:`autosave_results``flag. A parent directory for all results must be 
defined using the :py:data:`autosave_dir` Parameter and the saving format can 
be selected using the :py:data:`autosave_format` Parameter. The different 
formats are predefined and only implemented formats can be chosen. To query the 
available choices, please look at the code in the example below:

.. code-block::
    
    >>> import pydidas
    >>> app = pydidas.apps.ExecuteWorkflowApp()
    
    # We will activate the auto-saving and specify the path:
    >>> app.set_param_value('autosave_results', True)
    >>> app.set_param_value('autosave_dir', '/scratch/data/scan42_results')
    
    # To check, for the available formats, we need to get the Parameter and check
    # its choices property:
    >>> app.get_param('autosave_format').choices 
    ['None', 'HDF5']
    
    # Now, update the formats:
    >>> app.set_param_value('autosave_format', 'HDF5')

.. warning::

    Note that auto-saving each frame will result will have a significant 
    performance cost because the output files will need to be accessed for 
    each processed scan point. Using auto-saving is only encouraged for very 
    long processing times, e.g. multiple fittings for each scan data point.


Running the ExecuteWorkflowApp
------------------------------

Once configured, the :py:class:`ExecuteWorkflowApp <pydidas.apps.ExecuteWorkflowApp>` 
is run like any pydidas app, as described in detail in 
:ref:`running_pydidas_applications`.

As a recap, to run the app serially, use the :py:meth:`run 
<pydidas.apps.ExecuteWorkflowApp.run>` method:

    >>> import pydidas
    >>> app = pydidas.apps.ExecuteWorkflowApp()
    >>> app.run()

To run it utilizing parallelization, set up an 
:py:class:`AppRunner <pydidas.multiprocessing.AppRunner>` and use the 
:py:meth:`start <pydidas.multiprocessing.AppRunner.start>` method:

.. code-block::

    >>> app = pydidas.apps.ExecuteWorkflowApp()
    >>> runner = pydidas.multiprocessing.AppRunner(app)
    >>> runner.start()
    # After running, get the updated app with the results back:
    >>> app = runner.get_app()


Accessing results
-----------------

Using autosave
^^^^^^^^^^^^^^

If autosave has been enabled, the results are written to files and can be 
accessed externally by any program which can read the defined data type.

.. note::
    Please be advised that accessing the data while processing is still running
    can corrupt the output files and make them illegible.

Accessing results within Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The results from the ExecuteWorkflowApp are written in the global 
:py:class:`WorkflowResults <pydidas.workflow.WorkflowResults>` (the 
Singleton instance of :py:class:`ProcessingResults
<pydidas.workflow.ProcessingResults>`) which is described in
detail in :ref:`workflow_results`.

List of all ExecuteWorkflowApp Parameters
-----------------------------------------

    - live_processing (type: bool, default: False)
        Set live processing to True if the files do not yet exist at process 
        startup. This will skip checks on file existence and size.
    - autosave_results (type: bool, default: False)
        Save the results automatically after finishing processing. The results 
        for each plugin will be saved in a separete file (or files if multiple 
        formats have been selected).
    - autosave_dir (type: Union[str, Path], default: [empty])
        The directory for autosave files.
    - autosave_format (type: str, default: 'HDF5')
        The file format(s) for the data to be saved after the workflow has been 
        excuted. All data will be saved in a single folder for each run with 
        one file for each plugin. Note that the Parameter choices are defined
        in pydidas and the value can only correspond to any of these choices.

