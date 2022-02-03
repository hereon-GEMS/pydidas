Data browsing frame
===================

The data browsing frame allows the visualization of two-dimensional data.
The frame is divided in two parts: On the left (1), a directory explorer allows
to browse the full file system and select files. The right side (2) is used by 
a visualization widget. The implementation is a `silx ImageView widget 
<http://www.silx.org/doc/silx/latest/modules/gui/plot/imageview.html#module-silx.gui.plot.ImageView>`_\ .

.. image:: ../../../../media/frames/data_browsing_01_overview.png
    :width: 600px
    :align: center
    
The size of the widgets can be adjusted by using the two arrow buttons (3) and
(4) to enlarge the iamge view or directory explorer, respectively. Alternatively,
the splitter between the two frames can be dragged by the mouse to change the
relative sizes. 

.. warning::

    The two main widgets have a defined minimum size. If the user dras the 
    splitter further, the respective widget will be hidden. It can be enlarged
    again by capturing and dragging the slider from the edge towards the center.
    

Directory explorer
------------------

The directory explorer is used to select the data to be displayed. The exact
look and feel will depend on the used operating system and might be different
from the screenshots shown here.

A single click on an item will just highlight the item but will otherwise be 
ignored. Double-clicking on a folder (or the arrow next to a folder) will 
expand or collapse the folder, depending on the folder's current state. 
Double-clicking on a file will instruct pydidas to open the selected file. If 
the data format is readable and the file contains two-dimensional data, the 
content will be displayed in the ImageView widget. In case of hdf5 datasets, an
aditional selection field will be shown to select the data frame. 

The hdf5 data selection widget
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The hdf5 data selection widget is shown below.

.. image:: ../../../../media/frames/data_browsing_02_hdf5.png
    :width: 600px
    :align: center

The first row allows the user to select dataset filters for specific names.
For example, the Eiger detector master file has a number of datasets for 
detector specific settings like offsets and calibrations for the different 
modules. If the respective box is ticked, these datasets will not be shown in 
the drop-down list. Additional filters for datasets can be set on their minimum
size (the total number of datapoints, not per axis) and minimum data dimension.
Any changes to the filters will update the list of filtered datasets 
immediately. 

To select a dataset, simply select the corresponding hdf5 dataset key from the 
list. This will update the selection of the data frame.

.. note::

    For three-dimensional datasets, pydidas will assume that the first dimension 
    in the dataset is always the frame number and the second and third 
    dimensions correspond to the detector data frame.
    
The data frame can be selected by dragging the slider, clicking on an arrow or
by entering a new number. Clicking on "Show full frame" will show the selected 
frame in the ImageView widget. 

.. note::

    Changing the selected frame will only trigger an update of the ImageView
    if the "Auto update" checkbox is ticked.
    
ImageView visualization widget
------------------------------

The `ImageView <http://www.silx.org/doc/silx/latest/modules/gui/plot/imageview.html#module-silx.gui.plot.ImageView>`_
widget is part of the ESRF `silx <https://github.com/silx-kit/silx>`_ library.
It has 5 main parts which are shown in the screenshot below.

 .. image:: ../../../../media/frames/data_browsing_03_imageview.png
    :width: 600px
    :align: center

The menu (1) includes shortcuts for the various actions and the main display (2)
shows the selected data. Histograms of the data in the view are shown for a 
horizontal (3) and vertical (4) integration. The currently visible subset of the
data with respect to the full dataset is shown in (5).

Menu
^^^^

The menu items are described in detail below:

.. include:: ../silx/imageview.rst







