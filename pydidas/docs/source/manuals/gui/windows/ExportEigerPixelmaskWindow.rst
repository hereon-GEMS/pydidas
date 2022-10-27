.. _export_eiger_mask_window:

Export Eiger mask window
========================

.. image:: images/export_eiger_mask_window.png
    :align: center

The *Export Eiger mask window* is fairly simple as it only allows to export the
Eiger detector-internal pixel mask for dead and defunct pixels as an image.

The first Parameter allows to select the *_master* file from the data 
acquisition with the Eiger detector. Because the internal structure of these 
files is always identical, there is no need to specify the Hdf5 dataset.

The second Parameter is the filename for the export. Any format supported by
pydidas can be used for the export.

After setting both Parameters, use the :py:data:`Export pixelmask` button to
write the mask file.
