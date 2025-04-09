<!---
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0
--->


# pydidas
[![zenodo badge](https://zenodo.org/badge/DOI/10.5281/zenodo.7568610.svg)](https://doi.org/10.5281/zenodo.7568610)


pydidas (an acronym for the **Py**thon **di**ffraction **d**ata **a**nalysis **s**uite)
is a toolkit for the analysis of X-ray diffraction datasets. It is designed to
be accessible also for users with little experience in diffraction data analysis
in order to broaden the user base of diffraction techniques and to make diffraction
analysis more accessible for domain scientists.

Pydidas includes a graphical user interface and a command line interface to
embed its functionality in other projects or scripts.

## References
* Please check the citation file CITATION.cff
* Pydidas has also been issued with a global DOI for citations: 10.5281/zenodo.7568610<br> 
  [![zenodo badge](https://zenodo.org/badge/DOI/10.5281/zenodo.7568610.svg)](https://doi.org/10.5281/zenodo.7568610)


## Installation

Pydidas should be installed in a clean environment to allow pydidas to fix the
required dependency versions. This environment should be used exclusively for
pydidas and no further packages should be installed.

Pydidas requires a **Python version >= 3.11**. Note that pydidas has not yet been 
tested extensively with Python 3.13.

### Preparing the environment

Environments can be managed using any environment manager (e.g. venv,
conda/mamba). Due to dependency management issues, pydidas does not support
pre-configured conda/mamba environments anymore but relies exclusively on pip
for the dependency management.

Pip will install all dependencies together with the pydidas package.
There is no need to prepare the environment further.


### Building and installing pydidas

You will require a pydidas wheel file to install it using pip. If you have not
downloaded a build wheel file, you need to prepare one prior to installation.

### Using pip
Pydidas is available on PyPI and can be installed simply with 

    python -m pip install pydidas

#### Using a python wheel

Wheels for pydidas are available on the 
[pydidas releases](https://github.com/hereon-GEMS/pydidas/releases) webpage. 
To install a downloaded wheel, activate your chosen environment and use the 
following command:

    python -m pip install <path_to_pydidas_wheel_file.whl>

#### Using the source code directly

Download the pydidas source code or clone the git repository and navigate to the
folder with the project metadata files (like this README.md). Then, install
the package and any missing dependencies:

    python -m pip install .

Note that pip might need to build a wheel from pydidas first which will take
some time. If you want to build the wheel manually, for example to keep it for
later use, simply use the following commands (again, in the pydidas folder)::

    python -m build

This will create a tarball and a wheel file in the ``dist`` subdirectory.

> **Note:** You will need to install the build and setuptools packages manually in 
> your chosen environment if you want to build pydidas from source.

## Using pydidas

### Entry points
If installed as wheel, pydidas offers the following entry points:

  - `pydidas-gui` to start the graphical user interface.
  - `pydidas-documentation` to open the pydidas documentation in the default system
    web browser. **Note:** The pydidas module must have been run at least once 
    (either through opening the GUI or imported in a python shell) for the 
    documentation to have been created. 
  - `pydidas-clear-settings` Remove the stored registry keys for pydidas. 
  - `pydidas-updater` Start a script which automatically updates pydidas to the latest
    version available on GitHub.
  - `pydidas-remove-local-files` This script removes all local log files and stored 
    configuration files.
  - `run-pydidas-workflow` Script to run a defined workflow in the console. This script
    also requires configuration files for the scan and diffraction experiment. Please
    refer to the full documentation for more details.
  - `remove-pydidas` Remove all local config files and registry settings from the 
    system. Please note that this script will not remove the python code itself, but 
    only cleans up the system.

### Scripts
Pydidas includes multiple scripts which are located in the `src/pydidas_scripts` folder.
These can be called directly by python from the command line and they are:
  - `pydidas_gui.py` to start the GUI.
  - `pydidas_documentation.py` to open the html documentation in a browser.
  - `run_pydidas_workflow.py` to run a processing workflow on the command line.
  - `pydidas_updater_script.py` to update pydidas to the latest release published on
    GitHub.
  - `clear_local_settings.py` to remove all registry settings written by pydidas.

### Command line
Much of pydidas' functionality is also available from the command line or notebooks.
Pydidas can be imported and used as any other python module. Please refer to the 
documentaion for more details (see the section below on how to access the 
documentation). 

## Documentation

### Local documentation

The documentation is included with the distribution, but only in form of the source
to keep the distribution small. It will be compiled automatically the first time
pydidas is imported in python. This will take some time (about 30 seconds, depending on
the system) and a notification will be displayed.

The compiled documentation can be found in the
``lib/site-packages/pydidas/sphinx/html`` folder and the ***index.html*** file is the
global start page.

A ``pydidas-documentation`` entrypoint is available to open the documentation in the
system's default browser.

The graphical user interface also has a menu entry to open the help in a web browser.
Pressing F1 in the graphical user interface will also open the help in the system's 
default webbrowser.

### Online documentation

The pydidas documentation is also available online through github-pages:
https://hereon-gems.github.io/pydidas/

## Referencing pydidas

For the full citation information of pydidas, please see the CITATION.cff file.

Pydidas can also be cited by its global DOI on zenodo: 10.5281/zenodo.7568610\
[![zenodo badge](https://zenodo.org/badge/DOI/10.5281/zenodo.7568610.svg)](https://doi.org/10.5281/zenodo.7568610)


## License

The pydidas source code is released under the GNU General Public License
Version 3.
The documentation is licensed under the Creative Commons Attribution 4.0
International Public License (CC-BY-4.0).
Images and logos are licensed under Creative Commons Attribution-NoDerivatives
4.0 International Public License (CC-BY-ND-4.0).
Insignificant files (e.g. changelog) are released under the CC0 1.0 Universal
Public Domain Dedication (CC0-1.0).

## Acknolwedgements
pydidas is developed at [Helmholtz-Zentrum Hereon](https://www.hereon.de) and the 
development is supported by [DAPHNE4NFDI](https://www.daphne4nfdi.de).

The (azimuthal/radial) integration uses the [pyFAI](https://github.com/silx-kit/pyFAI)
engine for fast azimuthal integration. Some widgets are extensions of [silx](https://github.com/silx-kit/silx) 
widgets. Both ``pyFAI`` and ``silx`` are developed at the [ESRF](https://www.esrf.fr/).
