.. _global_settings_frame:

Global settings frame
=====================

The global settings frame allows the user to modify global Parameters used 
throughout pydidas. Technically, these Parameters are stored persistently in the
system registry using Qt's QSettings.

.. image::  ../../images/frames/global_settings_01_overview.png
    :align: center
    
.. note::
    The global Parameters can also be edited using the Extras > Settings menu 
    entry.

The "Restore defaults" button allows the user to change all Parameters to the 
factory default settings.

In addition, the frame only includes widgets to edit the global Parameters:

.. include:: ../global/pydidas_qsettings.rst