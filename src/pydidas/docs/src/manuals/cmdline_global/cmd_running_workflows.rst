..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


.. |WorkflowTree| replace:: :py:class:`WorkflowTree <pydidas.workflow.processing_tree.ProcessingTree>`

.. |Scan| replace:: :py:class:`Scan <pydidas.contexts.scan.scan.Scan>`

.. |DiffractionExperiment| replace:: :py:class:`DiffractionExperiment <pydidas.contexts.diff_exp.diff_exp.DiffractionExperiment>` 

.. |ExecuteWorkflowRunner| replace:: :py:class:`ExecuteWorkflowRunner <pydidas.apps.execute_workflow_runner.ExecuteWorkflowRunner>`

.. |process_scan| replace:: :py:meth:`process_scan <pydidas.apps.execute_workflow_runner.ExecuteWorkflowRunner.process_scan>`


Running pydidas workflows from the command line
===============================================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Required information
--------------------

To run pydidas workflows (as defined in the |WorkflowTree|) with parallelization 
support from the command line, the following information must be provided by 
the user:

    - The |WorkflowTree| to be used.
    - The |Scan| configuration.
    - The |DiffractionExperiment| configuration.
    - An output directory to save the results. Note that this directory must
      be empty or an overwrite flag must be given.

Pydidas includes the |ExecuteWorkflowRunner| class to facilitate running 
workflows from the command line.

The ExecuteWorkflowRunner
-------------------------

The |ExecuteWorkflowRunner| is designed to be easily used from a script, but
all the required information can also be passed as keyword arguments. 

One of its main features is that it creates and handles an event loop of a 
QApplication to allow pydidas processing to communication using Qt's signals 
and slots.

Setup
^^^^^

The |ExecuteWorkflowRunner| supports the following keywords:

    - workflow
    - scan
    - diffraction_exp
    - output_directory
    - verbose
    - overwrite

All keywords also have a parsed equivalent, as described below:

.. list-table::
    :widths: 15 20 20 45
    :header-rows: 1
    :class: tight-table

    * - Keyword name
      - Accepted types
      - equivalent parsed arg
      - Notes
    * - workflow
      - Path, str, |WorkflowTree|
      - -workflow / -w
      - The parsed argument can only be used to point to files with exported
        |WorkflowTree| instances.
    * - scan
      - Path, str, |Scan|
      - -scan / -s
      - The parsed argument can only be used to point to files with exported
        |Scan| instances.
    * - diffraction_exp
      - Path, str, |DiffractionExperiment|
      - -diffraction_exp / -d
      - The parsed argument can only be used to point to files with exported
        |DiffractionExperiment| instances.
    * - output_directory
      - Path, str
      - --output_dir / -o
      - 
    * - verbose
      - bool
      - --verbose
      - Flag to enable printed status messages to the terminal.
    * - overwrite
      - bool
      - --overwrite
      - Flag to enable overwriting of files and export results to existing,
        non-empty directories.
      
Running a workflow
^^^^^^^^^^^^^^^^^^ 

Running a workflow is very simple and only requires calling the 
|process_scan| method, as shown in the example below.

.. code-block::

    import pydidas

    def run_workflow():
        executor = pydidas.apps.ExecuteWorkflowRunner(
            workflow='/home/username/data/experiment/workflow.yml',
            scan='/home/username/data/experiment/scan01.yml',
            diffraction_exp='/home/username/data/experiment/exp.yml',
            output_dir='/home/username/data/experiment/results/scan01',
        )
        executor.process_scan()

    if __name__ == '__main__':
        run_workflow()

The code above will execute the workflow, save the results in the given
directory and exit the event loop for additional user input. **Please be aware
that the call to the ExecuteWorkflowRunner must be made from within a function
due to using of python's** :mod:`multiprocessing` **module.**

.. tip::
    
    All the keywords from the initialization can also be given in the 
    |process_scan| method, for example:

    .. code-block::

        executor.process_scan(scan='/home/username/data/experiment/scan02.yml')

Batch processing
^^^^^^^^^^^^^^^^

Batch processing is easily done as it only requires to update the necessary
information between |process_scan| calls.

For example, running the same workflow for multiple scans can be done as
follows:

.. code-block::

    >>> import pydidas
    >>> executor = pydidas.apps.ExecuteWorkflowRunner(
    ...     workflow='/home/username/data/experiment/workflow.yml',
    ...     diffraction_exp='/home/username/data/experiment/exp.yml',
    ... )
    >>> for i_scan in range(1, 6):
    ...     executor.process_scan(
    ...         scan=f'/home/username/data/experiment/scan{i_scan:02d}.yml',
    ...         output_dir=f'/home/username/data/experiment/results/scan{i_scan:02d}',
    ...     )


Command line script
-------------------

Pydidas also includes a ready-to-use script to execute from the command line.
It is called ``run_pydidas_workflow.py`` and is located in the ``pydidas_scripts``
directory. 

If pydidas was installed with pip, a ``run-pydidas-workflow`` entrypoint was
created and can be used. Otherwise, simply call the script with the python 
interpreter:

.. code:: bash

    python pydidas_scripts/run_pydidas_workflow.py 
        -workflow /home/username/data/experiment/workflow.yml
        -scan /home/username/data/experiment/scan01.yml
        -diffraction_exp /home/username/data/experiment/exp.yml
        -output_dir /home/username/data/experiment/results/scan01
        --overwrite
        --verbose
