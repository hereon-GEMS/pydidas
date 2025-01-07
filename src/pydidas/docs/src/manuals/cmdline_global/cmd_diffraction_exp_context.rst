..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _diffraction_exp_context:

The DiffractionExperimentContext class
======================================

.. contents::
    :depth: 2
    :local:
    :backlinks: none

Introduction
------------

The :py:class:`DiffractionExperimentContext 
<pydidas.contexts.diff_exp.diff_exp.DiffractionExperimentContext>`
is the pydidas Singleton instance of the 
:py:class:`DiffractionExperiment
<pydidas.contexts.diff_exp.DiffractionExperiment>`
class. It is used for storing and accessing global information about the 
experimental setup. Stored information include

- X-ray energy
- detector model (pixel numbers and sizes)
- detector geometry.

All objects are stored as :py:class:`Parameters <pydidas.core.Parameter>` and
can be accesses as described in the basic tutorial. A full list of Parameters is
given in :ref:`Full list of Parameters for DiffractionExperimentContext 
<diffraction_exp_context_parameters>`\ .

Its instance can be obtained by running the following code:

.. code-block::

    >>> import pydidas
    >>> EXP = pydidas.contexts.DiffractionExperimentContext()

Configuring the DiffractionExperimentContext
--------------------------------------------

X-ray energy and wavelength
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The X-ray energy and wavelength are two coupled Parameters and any changes to 
one will cause the other Parameter to be updated as well. They can be accessed
through the keys :py:data:`xray_energy` and :py:data:`xray_wavelength`, 
respectively. 

Please see also the example below:

.. code-block::

    >>> import pydidas
    >>> EXP = pydidas.contexts.DiffractionExperimentContext()
    >>> EXP.get_param_value('xray_wavelength')
    1
    >>> EXP.get_param_value('xray_energy')
    12.398
    
    # Now, set the wavelength and check the energy:
    >>> EXP.set_param_value('xray_wavelength', 2)
    >>> EXP.get_param_value('xray_energy')
    6.199209921660013

    # Or change the X-ray energy:
    >>> EXP.set_param_value('xray_energy', 12)
    >>> EXP.get_param_value('xray_wavelength')
    1.0332016536100022

The detector
^^^^^^^^^^^^

The detector is defined by the following Parameters:

.. list-table::
    :widths: 20 10 10 60
    :header-rows: 1
    :class: tight-table

    * - Parameter
      - type
      - unit
      - description
    * - detector_name
      - str
      - n/a
      - The detector name in pyFAI nomenclature.
    * - detector_npixx
      - int
      - pixel
      - The number of detector pixels in x direction (horizontal).
    * - detector_npixy
      - int
      - pixel
      - The number of detector pixels in y direction (vertical).
    * - detector_pxsizex
      - float
      - um
      - The detector pixel size in X-direction.
    * - detector_pxsizey
      - float
      - um
      - The detector pixel size in Y-direction.
    * - detector_mask_file (optional)
      - str
      - n/a
      - The path and filename for the detector mask file. This file is used in 
        pyFAI integration plugins.

The :py:data:`detector_name` is only relevant for referencing any pyFAI object 
but is included in the metainformation and should be set correctly. The 
Parameters for numbers of pixels and pixelsize exactly what the name suggests.

Defining the detector manually
""""""""""""""""""""""""""""""

The detector can be defined manually if required, for example for a prototype
detector which is not inclued in pyFAI, by setting all Parameters values:

.. code-block::

    >>> import pydidas
    >>> EXP = pydidas.contexts.DiffractionExperimentContext()
    >>> EXP.set_param_value('detector_name', 'A detector with very small asymmetric pixels')
    >>> EXP.set_param_value('detector_npixx', 1024)
    >>> EXP.set_param_value('detector_npixy', 2048)
    >>> EXP.set_param_value('detector_pxsizex', 25)
    >>> EXP.set_param_value('detector_pxsizey', 12.5)

Using a pyFAI detector
""""""""""""""""""""""

If the detector is defined in pyFAI, this library can be used to update the 
detector settings automatically by giving the detector name in the 
:py:meth:`set_detector_params_from_name 
<pydidas.contexts.diff_exp.DiffractionExperiment.set_detector_params_from_name>`
method:

.. code-block::

    >>> import pydidas
    >>> EXP = pydidas.contexts.DiffractionExperimentContext()
    >>> EXP.set_detector_params_from_name('Eiger 9M')
    >>> EXP.get_param_value('detector_name')
    'Eiger 9M'
    >>> EXP.get_param_value('detector_npixx')
    3110
    >>> EXP.get_param_value('detector_npixy')
    3269
    >>> EXP.get_param_value('detector_pxsizex')
    75.0
    >>> EXP.get_param_value('detector_pxsizey')
    75.0
    
The geometry
^^^^^^^^^^^^

pydidas uses the pyFAI geometry. In short, it uses the point of normal 
incidence (PONI), the orthogonal projection of the origin (i.e. the sample) on 
the detector. 

.. tip::

    The pyFAI geometry is described in detail in this pyFAI document:
    `Default geometry in pyFAI <https://pyfai.readthedocs.io/en/master/geometry.html#default-geometry-in-pyfai>`_\ .

The pyFAI coordinate system used the :math:`x_1` (up), :math:`x_2` and 
:math:`x_3` (along the beam direction) coordinates. The :math:`x_2` axis is 
defined to create a right-handed coordinate system with the :math:`x_1` and 
:math:`x_3` axes.

The PONI defines the :math:`x_1` and :math:`x_2` coordinates of the detector 
(measured from the origin at the top left corner) and the distance in beam 
direction defines the :math:`x_3` coordinate (detector distance).

Three rotations (:math:`rot_1`: mathmatically negative around the axis pointing 
up; :math:`rot_2`: mathematically negative around the :math:`x_2` axis; 
:math:`rot_3`: mathematically positive (!) around the X-ray beam direction) are 
used to move the detector with respect to the origin (sample) are applied to 
the detector to transform the detector geometry into the experimental geometry.

The correspondence between pyFAI geometry and pydidas DiffractionExperimentContext
Parameter names is given below:

.. list-table::
    :header-rows: 1

    * - pyFAI parameter name
      - corresponding pydidas Parameter
      - unit
    * - :math:`poni_1`
      - detector_poni1
      - m
    * - :math:`poni_2`
      - detector_poni2
      - m
    * - :math:`dist`
      - detector_dist
      - m
    * - :math:`rot_1`
      - detector_rot1
      - rad
    * - :math:`rot_2`
      - detector_rot2
      - rad
    * - :math:`rot_3`
      - detector_rot3
      - rad

Defining the geometry
"""""""""""""""""""""

These Parameters can be accessed and updated by the pydidas Parameter names as
given in the table above. For an example, see below:

.. code-block::

    >>> import pydidas
    >>> EXP = pydidas.contexts.DiffractionExperimentContext()
    >>> EXP.set_param_value('detector_poni1', 0.114731)
    >>> EXP.set_param_value('detector_poni2', 0.123635)
    >>> EXP.set_param_value('detector_dist', 0.235885)
    >>> EXP.set_param_value('detector_rot1', -0.011062669)
    >>> EXP.set_param_value('detector_rot2', -0.002172149)
    >>> EXP.set_param_value('detector_rot3', 0.0)
    

Import and Export
-----------------

The DiffractionExperimentContext settings can be imported and exported to files, based on
the available im-/exporters. The standard distribution ships with support for
YAML files and pyFAI .poni files. Both types are supported for import and 
export. The format will be determined automatically based on the file extension.

Imports and exports are started by calling the 
:py:meth:`import_from_file(filename) 
<pydidas.contexts.diff_exp.DiffractionExperiment.import_from_file>`
and 
:py:meth:`export_to_file(filename) 
<pydidas.contexts.diff_exp.DiffractionExperiment.export_to_file>`,
respectively. The filename must include the absolute path to the file. 

.. warning::

    Importing the :py:class:`DiffractionExperimentContext 
    <pydidas.contexts.diff_exp.DiffractionExperiment>`
    from file will overwrite all current values without asking for confirmation.

An example to demonstrate these methods is given below:

.. code-block::

    >>> import pydidas
    >>> EXP = pydidas.contexts.DiffractionExperimentContext()
    >>> EXP.get_param_values_as_dict()
    {'xray_wavelength': 1,
     'xray_energy': 12.398,
     'detector_name': 'detector',
     'detector_npixx': 0,
     'detector_npixy': 0,
     'detector_pxsizex': -1,
     'detector_pxsizey': -1,
     'detector_dist': 1,
     'detector_poni1': 0,
     'detector_poni2': 0,
     'detector_rot1': 0,
     'detector_rot2': 0,
     'detector_rot3': 0}
    >>> EXP.export_to_file('/scratch/exp_settings_test.yaml')

    # now, we update the local settings:
    >>> EXP.set_detector_params_from_name('Eiger 9M')
    >>> EXP.get_param_values_as_dict()
    {'xray_wavelength': 1,
     'xray_energy': 12.398,
     'detector_name': 'Eiger 9M',
     'detector_npixx': 3110,
     'detector_npixy': 3269,
     'detector_pxsizex': 75.0,
     'detector_pxsizey': 75.0,
     'detector_dist': 1,
     'detector_poni1': 0,
     'detector_poni2': 0,
     'detector_rot1': 0,
     'detector_rot2': 0,
     'detector_rot3': 0}
    
    # If we load the settings from the stored file, these settings will be lost
    # and the saved state will be restored:
    >>> EXP.import_from_file('/scratch/exp_settings_test.yaml')
    >>> EXP.get_param_values_as_dict()
    {'xray_wavelength': 1,
     'xray_energy': 12.398,
     'detector_name': 'detector',
     'detector_npixx': 0,
     'detector_npixy': 0,
     'detector_pxsizex': -1,
     'detector_pxsizey': -1,
     'detector_dist': 1,
     'detector_poni1': 0,
     'detector_poni2': 0,
     'detector_rot1': 0,
     'detector_rot2': 0,
     'detector_rot3': 0}

.. _diffraction_exp_context_parameters:

.. include:: ../global/diff_exp_context_params.rst
