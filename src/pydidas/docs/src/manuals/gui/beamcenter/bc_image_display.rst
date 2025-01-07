..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0


Image display
^^^^^^^^^^^^^

The image display is a :ref:`PydidasPlot2d <plot_plot2d>` with all the 
functionality described in the linked description. In addition, clicking with
the left mouse buttons allows to store the selected positions. Points are 
visualized by different symbols, as explained below.

.. list-table::
    :widths: 5 95
    :class: tight-table
    :header-rows: 1

    * - point symbol
      - description
    * -  .. image:: ../beamcenter/_images/bc_point.png
            :align: center
      - A generic **x** marker to signal that this point has been stored.
    * -  .. image:: ../beamcenter/_images/bc_selected_point.png
            :align: center
      - Selected points are highlighted with a filled circle.
    * -  .. image:: ../beamcenter/_images/bc_center.png
            :align: center
      - The beamcenter is marker with a diamond-shaped marker.