pyDIDAS
=======

pyDIDAS (the Python DIffraction Data Analysis Suite) is a toolkit for
the analysis of diffraction datasets, both live at the beamline and
offline for in-depth analysis.


Module structure
----------------

There are several subfolders included in the distribution

* pydidas: The code for the python module.
* tests: unit tests for the code. This should not concern the generic user.
* docs: the documentation.
* plugins: Individual processing plugins
* scripts: ready-to-use scripts to run the software.

Installation
------------

To be added.

Documentation
-------------

The documentation is included with the distribution, but it must be compiled by
the user first. The rational behind this is to keep the distribution light-weight.

To make the documentation, make sure sphinx is installed. It is shipped with the
Anaconda python distribution or can be installed via pip.

1. Navigate to the "docs" sub-folder
2. Run "make html" to create the html documentation. (Note, on windows you might
   need to call ".\make html".)
3. Navigate to the "docs/build/html" and open "index.html".

Note that you will have many warning during "make" because sphinx will detect
the overloaded methods with the same name as in parent classes.

License
-------

pydidas is released under the GNU GENERAL PUBLIC LICENSE Version 3. A copy
of the full license is provided with the pydidas.
