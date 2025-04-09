..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

Selecting radial integration range in image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the azimuthal range is "Full detector", nothing will be displayed to start 
with. If a range has been selected, the limits of the range will be marked by 
two lines starting from the beamcenter. Clicking on the first point will set
the inner radial limit, which will be displayed as a circle. Clicking a second
time will set the upper limit and the selected integration ROI will be displayed
as overlay.

.. list-table::
    :widths: 33 33 33
    :class: tight-table
    :header-rows: 1

    * -  .. image:: ../integration_roi/_images/roi_azi.png
            :align: center
            :width: 200
      -  .. image:: ../integration_roi/_images/roi_azi_inner_rad.png
            :align: center
            :width: 200
      -  .. image:: ../integration_roi/_images/final_roi.png
            :align: center
            :width: 200
    * - The starting azimuthal limits without any radial selection.
      - After selecting the inner radial limit, it is shown as a circle.
      - After selecting the outer radial limit as well, the final integration
        ROI is displayed.

Selecting azimuthal integration range in image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the radial range is "Full detector", nothing will be displayed to start 
with. If a range has been selected, the limits of the range will be marked by 
two circles around the beamcenter. Clicking on the first point will set the 
starting radial limit and draw a line from the beamcenter. Clicking a second
time will set the upper limit and the selected integration ROI will be displayed
as overlay.

.. list-table::
    :widths: 33 33 33
    :class: tight-table
    :header-rows: 1

    * -  .. image:: ../integration_roi/_images/roi_rad.png
            :align: center
            :width: 200
      -  .. image:: ../integration_roi/_images/roi_rad_azi_start.png
            :align: center
            :width: 200
      -  .. image:: ../integration_roi/_images/final_roi.png
            :align: center
            :width: 200
    * - The starting radial limits without any azimuthal selection.
      - After selecting the lower azimuthal limit, it is shown as a line from 
        the beamcenter.
      - After selecting the upper azimuthal limit as well, the final integration
        ROI is displayed.
