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

Using conda
...........

Use the provided environment.yml file to create the conda environment::

    conda env create --name pydidas --file .\pydidas-env.yml

Using pip
.........

Use the provided requirements.txt to install all necessary packages::

    pip install -r requirements.txt
    
Building and installing pydidas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the active enviroment (or distribution), navigate to the folder with the 
pydidas repository and install pydidas using pip::

    pip install .

Note that pip might need to build a wheel from pydidas first which will take
some time.


Documentation
-------------

The documentation is included with the distribution, but it must be compiled by
the user first. The rational behind this is to keep the distribution 
light-weight. 

To make the documentation, make sure sphinx is installed. It is shipped with 
pydidas, but depending on system settings and python installation, the 
*sphinx-build* command might not be in the system's path.

1. Navigate to the "pydidas/docs" sub-folder
2. Run "make html" to create the html documentation. (Note: on windows you might
   need to call ".\make.bat html".)
3. Navigate to the "pydidas/docs/build/html" folder and open "index.html".


Referencing pydidas
-------------------

For the full citation  information of pydidas, please see the CITATION.cff file.

Pydidas can also be cited by its DOI on zenodo: 10.5281/zenodo.7568392 |zenodo_DOI|


License
-------

pydidas is released under the GNU General Public License Version 3. A copy
of the full license is provided with the pydidas. For more information on the
individual files, please refer to the LICENSE.md file.


.. |zenodo_DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7568611.svg