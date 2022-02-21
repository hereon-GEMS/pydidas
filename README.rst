pydidas
=======

pydidas (the Python DIffraction Data Analysis Suite) is a toolkit for
the analysis of diffraction datasets, both live at the beamline and
offline for in-depth analysis.


Module structure
----------------

There are several subfolders included in the distribution

* pydidas: The code for the python module.
* pydidas/docs: the documentation.
* tests: unit tests for the code. This should not concern the generic user.
* plugins: Individual processing plugins
* scripts: ready-to-use scripts to run the software.

Installation
------------

For now, the pydidas package is not yet available through Anaconda. To install 
it, navigate to the directory with the source files and run the following
command:

.. code-block::

    python -m pip install .

Then, install the required dependencies using anaconda by running this command
in the same directory:

.. code-block::

    conda install --file requirements.txt

.. note::

    If you do not want to use Anaconda for dependency management, you can also
    install pydidas and all required modules using 
    `python -m pip install -r requirements.txt .`

Documentation
-------------

The documentation is included with the distribution, but it must be compiled by
the user first. The rational behind this is to keep the distribution light-weight.

To make the documentation, make sure sphinx is installed. It is shipped with the
Anaconda python distribution or can be installed via pip.

1. Navigate to the "pydidas/docs" sub-folder
2. Run "make html" to create the html documentation. (Note, on windows you might
   need to call ".\make html".)
3. Navigate to the "pydidas/docs/build/html" folder and open "index.html".

Note that you will have many warning during "make" because sphinx will detect
the overloaded methods with the same name as in parent classes.

License
-------

pydidas is released under the GNU GENERAL PUBLIC LICENSE Version 3. A copy
of the full license is provided with the pydidas.
