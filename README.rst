..
    Copyright 2023, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


pydidas
=======

|zenodo_DOI|

pydidas (the Python DIffraction Data Analysis Suite) is a toolkit for
the analysis of diffraction datasets, both live at beamlines and
offline for in-depth analysis.

pydidas uses the pyFAI engine for fast azimuthal integration, developed at
the ESRF (https://github.com/silx-kit/pyFAI).


References
----------
* Please check the citation file CITATION.cff



Installation
------------

Preparing the environment
^^^^^^^^^^^^^^^^^^^^^^^^^

Using mamba/conda
.................

Use the provided pydidas-env.yml file to create the conda environment::

    conda env create --name pydidas --file .\pydidas-env.yml

Using pip
.........

When using pip, all dependencies will be installed together with the package.
There is no need to prepare the environment further.


Building and installing pydidas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will require a pydidas wheel file to install it using pip. If you have not
downloaded a build wheel file, you need to prepare one prior to installation.

Download the pydidas source code or clone the git repository and navigate to the
folder with the project metadata files (like the README.rst). Then, install
the package and any missing dependencies::

    python -m pip install .


Note that pip might need to build a wheel from pydidas first which will take
some time. If you want to build the wheel manually, for example to keep it for
later use, simply use the following commands (again, in the pydidas folder)::

    python -m build
    python -m pip install dist\pydidas--YY.MM.DD-py3-none-any.whl

where YY.MM.DD would be substituted with the currrent version number.


Documentation
-------------

The documentation is included with the distribution, but it must be compiled by
the user first. The rational behind this is to keep the distribution
light-weight.

The documentation will be created automatically the first time, pydidas is
imported in python. This will take some time (about 30 seconds, depending on
the system) and a notification will be displayed.

The compiled documentation can be found in the "pydidas/docs/build/html" folder
and the "index.html" is the main entry point.

Alternatively, a pydidas-documentation entrypoint exists to open the
documentation.

The pydidas documentation is also available through github pages.

Referencing pydidas
-------------------

For the full citation  information of pydidas, please see the CITATION.cff file.

Pydidas can also be cited by its DOI on zenodo: 10.5281/zenodo.7568392 |zenodo_DOI|


License
-------

The pydidas source code is released under the GNU General Public License
Version 3.
The documentation is licensed under the Creative Commons Attribution 4.0
International Public License (CC-BY-4.0).
Images and logos are licensed under Creative Commons Attribution-NoDerivatives
4.0 International Public License (CC-BY-ND-4.0).
Insignificant files (e.g. changelog) are released under the CC0 1.0 Universal
Public Domain Dedication (CC0-1.0).

.. |zenodo_DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7568611.svg
