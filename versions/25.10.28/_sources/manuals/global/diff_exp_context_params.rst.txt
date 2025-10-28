..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Full list of Parameters for DiffractionExperimentContext 
--------------------------------------------------------

- xray_wavelength (float, unit: Angstrom, default: 1.0)
    The X-ray wavelength. Any changes to the wavelength will also update 
    the X-ray energy setting.   
- xray_energy (float, unit: keV, default: 12.398)
    The X-ray energy. Changing this parameter will also update the X-ray 
    wavelength setting.
- detector_name (str, default: "detector")
    The detector name (in pyFAI nomenclature if used for automatic 
    configuration).
- detector_npixx (int, default: 0)
    The number of detector pixels in x direction (horizontal).
- detector_npixy (int, default: 0)
    The number of detector pixels in x direction (vertical).
- detector_pxsizex (float, unit: um, default: -1)
    The detector pixel size in X-direction.
- detector_pxsizey (float, unit: um, default: -1)
    The detector pixel size in Y-direction.
- detector_mask_file (str, default: .)
    The path to the detector mask file. If empty, this defaults to no detector 
    mask. 
- detector_dist (float, unit: m, default: 1.0)
    The sample-detector distance.
- detector_poni1 (float, unit: m, default: 0.0)
    The detector PONI1 (point of normal incidence; in y direction). This is 
    measured in meters from the detector origin.
- detector_poni2 (float, unit: m, default: 0.0)
    The detector PONI2 (point of normal incidence; in x direction). This is 
    measured in meters from the detector origin.
- detector_rot1 (float, unit: rad, default: 0.0)
    The detector rotation 1 (yaw; lefthanded around the "up"-axis)
- detector_rot2 (float, unit: rad, default: 0.0)
    The detector rotation 2 (pitching the detector; positive direction is 
    tilting the detector top upstream while keeping the bottom of the 
    detector stationary.
- detector_rot3 (float, unit: rad, default: 0.0)
    The detector rotation 3 (roll; around the beam axis; right-handed when 
    looking downstream with the beam.)
