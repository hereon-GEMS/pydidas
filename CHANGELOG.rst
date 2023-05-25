.. Copyright 2021-, Helmholtz-Zentrum Hereon
.. SPDX-License-Identifier: CC0-1.0

v23.MM.DD
=========

Improvements
------------

- Plugins:

    - Added an option to apply a multiplication factor to the background in the
      SubtractBackgroundImage and Subtract1dBackgroundProfile plugins.

- General improvements:

    - Added a 'Copy experiment description from diffraction context' button in 
      the QuickIntegrationFrame to allow using an existing calibration.
    - Manually setting the beamcenter from points now works also with a single
      selected points, even if more points are in the list.
    - The Define diffraction setup frame now also displays the derived position
      of the beamcenter.

Bugfixes
--------

- Fixed an issue with the QuickIntegrationFrame which changed the intergration 
  region when changing the detector model.
- Fixed a formatting issue when opening Hdf5 files in the 
  SelectIntegrationRegionWindow.
- Fixed an issue with the FilelistManager if files with the same prefix button
  an additional suffix were present in the directory.
- Fixed an issue in the WorkflowTestFrame when output plugins were included in
  the WorkflowTree.



v23.5.22
========

Major changes
-------------

- The "Import and display workflow results" now has its own instances of 
  ScanContext and WorkflowResults and can be used in parallel to 
  the current workflow and its results.
- The structure of pydidas hdf5 result imports/exports has changed and all
  result files now have the complete processing metadata included.
- Added a QuickIntegrationFrame to run fast integrations without needing to 
  set up a full workflow.

Improvements
------------

- New features:

    - Added support for exporting the calibration results to yaml files and 
      to the pydidas DiffractionExperimentContext directly from the 
      PyfaiCalibFrame.
    - Added an action to get information about the underlying datapoint from 
      WorkflowResults plots.
    - Added a new button in the workflow result visualizations to show details 
      about the datapoint.
    - The WorkflowEditFrame now also allows to filter plugins for their name.
    - Added methods to define DiffractionExperiment parameters from given points 
      on circles and ellipses.
    - Added a window to manually fit and set the beamcenter position.
    - The 'Define diffraction setup' frame now has an option to set the 
      beamcenter manually.
    - Added a window to select the integration region graphically through 
      clicking the boundaries in an image.

- General improvements:

    - Updated pyproject.toml and removed setup.cfg
    - When leaving the TestWorkflowFrame, pop-up windows are now hidden.
    - Changed pyFAI plugins to use explicit parameters to select the ranges.
    - The EditPluginParametersWidget is now hiding all Parameters which start 
      with an underscore to allow 'private' Parameters.
    - Added 'advanced_parameters' to Plugin Parameters to allow hiding of 
      Parameters (in the GUI) which are usually not required.
    - Added a widget to select points in an image, for example for beamcenter 
      determination.
    - Added methods to get the radial range in 2theta, r, and Q to the 
      pyFAI integrationBase plugin.
    - The CropData1D plugin now accepts 'None' as bounds to disable specific 
      bounds.

- Added unique plugin configuration widgets:
    
    - Moved the windows from gui to widgets subpackage for better dependency 
      management in Plugin configuration widgets.
    - Added unique configuration widget to SubtractBackgroundImage plugin.
    - Added unique configuration widget to PyfaiIntegrationBase plugin.

- Programmatic improvements:
    
    - Exposed Scan and DiffractionExperiment in the contexts in preparation of 
      local usages. This also includes an update of the object names for 
      consistency.
    - Added explicit .copy and .deepcopy methods to 
      ObjectWithParameterCollection
    - Changed all .get_copy methods to .copy for consistency with numpy and 
      python main.
    - The PluginCollection now uses the pathlib library instead of strings for 
      management of files and paths.
    - contexts.scan_contexts importers can now select which Scan instance to 
      import to.
    - contexts.diffraction_exp_context importers can now select which 
      DiffractionExperiment instance to import to.
    - Added an update_from_tree method to the WorkflowTree.
    - Added 'counted_images_per_file' Parameter to hdf5 loaders to allow 
      exporting the number of processed images.
    - Created widgets.framework subpackage and moved framework widgets (e.g. 
      BaseFrames) into it.
    - Added an .active_plugin_header property to the WorkflowTree
    - The GenericTree.order_node_ids now also sets the active node again.
    - Added functions to fit circles and ellipses.
    - Changed names of policy and alignment constants for consistency.
    - Added 'get_pyfai_geometry', 'update_from_pyfai_geometry' and 
      'as_fit2d_geometry_values' methods to the DiffractionExperiment class for 
      easy conversion to and from pyFAI.
    - Added a signal to the DiffractionExperiment which is emitted when any of 
      its Parameters are updated.
    - Added a beamcenter property to the DiffractionExperiment.
    - Added ManuallySetIntegrationRegionController and 
      ManuallySetBeamcenterController classes to pydidas.widgets.controllers to 
      manage the corresponding widgets.
    - Added a PydidasPlotStack widget which automatically switches between 1D 
      and 2D plots and allows to plot data using a single interface.
    - Moved the CompositeCreator frame from the main toolbar menu to the 
      utilities.
    - Added an 'update_value_and_choices' method to the Parameter to change the 
      value and choices simultaneously without any incorrect intermediate 
      status.


Bugfixes
--------

- Fixed an issue in the BaseInputPlugin when using both the ScanContext 
  scan_start_index > 0 and scan_index_stepping > 1.
- Fixed an issue with the DirectorySpyFrame displaying wrong status messages.
- Fixed an issue with overlapping histogram limits in CropHistogramOutliers.
- Fixed an issue with multiprocessing process names when running multiple 
  instances.
- Fixed an issue with teh FilelistManager and compressed Hdf5 files.
- Fixed an issue with selecting data subsets (in data space) in the 
  WorkflowResultsSelector.
- Fixed an issue in the CropHistogramOutliers action with vmin > vmax and 
  numpy datatypes.
- Fixed an issue where the scan dimensions in the ResultSelectionWidgets would
  not be displayed correctly when using the 'Timeline' option.
- Fixed an issue in the ResultSelectionWidget which occured when changing the
  dimension selection for axes with unicode characters.
- Fixed a bug when importing a WorkflowTree while not all Plugins in the tree
  were registered.
- Fixed an issue when importing plugins from an empty Path object.
- Fixed an issue where the PluginCollection would emit the 'plugins updated' 
  signal prematurely which created an infinite loop.
- Fixed an issue with PydidasPlot2D when not using the singleton 
  DiffractionExperimentContext.
- Fixed an issue where the PydidasPositionInfo widget in plots would always
  reference the DiffractionExperimentContext
- Fixed an issue in pyFAIintegrationBase plugin when the subclass does not have
  the radial or azimuthal ranges.
- Fixed an issue in the PyfaiIntegrationBase plugin with the diffraction_exp
  keyword being interpreted as a parameter value.
- Fixed an issue with centering of the WorkflowTree in the WorkflowEditFrame.
- Fixed an issue where updating a Path ParameterIoWidget would not emit the 
  io_edited signal when a new file would be selected through drag & drop.
- Fixed an issue where no signal would be emitted if the choices in the 
  ParamIoWidgetComboBox were updated and the selected value was changed 
  for consistency.
- Fixed an issue in the pyFAIintegrationBase plugin where the check for the 
  re-initialization of the AzimuthalIntegrator was always performed, 
  irrespective of the implemented check.
- Fixed an issue in the WorkflowTreeEditManager where an inconsistent 
  WorkflowTree would not be displayed as such after restoring the GUI state. 
- Fixed an issue in the BasePlugin where the data consistency check would not
  give a human-readable error message.
- Fixed an issue with detector pixel sizes of zero interfering with plot widget
  position information which raised exceptions.
- Fixed an issue with the DirectorySpyApp when the first file does not start
  with the indices zero or 1.
- Fixed an issue with the FileDialog initialization when only a specific 
  file format is available without the option of all supported files.


v23.3.9
=======

Major changes
-------------

- Added a GLOBAL_CONTEXTS dictionary in contexts to have generic access to all
  contexts and to allow adding contexts in a convenient way.
- Renamed ExperimentContext to DiffractionExperimentContext to have a clear
  association and allow adding further experiments.

Improvements
------------

- Generalized the plugin processing-plugin subcategories and defined them 
  in core.constants.constants.
- Removed a redundant import from main_menu file.
- Removed quit method definition in the WorkerController and added exit method.
- Added a typecheck for lists in ObjectWithParameterCollection hash to 
  convert them to hashable tuples.  
- Added a new PydidasFileDialog which has buttons for quick access to latest 
  opened location and to ScanContext base directory.
- Added the option to add 'permanent' keyword arguments to the SingletonFactory
- Added the option to add persistent identifiers to file/directory Parameters 
  to configure their respective FileDialogs.  
- Added FWHM determination to the core.fitting routines.
- Added context menus to the nodes in the Workflow edit frame to allow moving
  and creating copies.
- Changed the Exception in the GenericIoMeta class to UserConfigError to 
  improve the user experience when trying to export data with an unsupported
  file format.
- Added a standard fontsize property to the PydidasApp in preparation for a 
  scalable font size in the UI.
- Changed the default ranges in the FitSinglePeak plugin to None which will
  default to the full input data range.
- Added a threshold for low pixel intensities in the 'Crop histogram outliers'
  action in silx plot.
- Changed the r/theta coordinate system in the silx plots to mm/deg coordinates
  to be consistent with pyFAI units.
- Added CropHistogramOutlier actions to the pyFAI calibration frame.
- Improved the handling of additional toolbars in the MainWindow.
- Allowed None in the Sum1D plugin bounds to have no limits.
- Allowed None in the Sum2D plugin bounds to have no limits.
- Added a description for the scan dimensions and their ordering.
- The PydidasFileDialog now allows to show files in a directory without having
  them selectable.
- Added axis labels and units to the workflow ResultSelectionWidget.
- Added the Dataset data unit and data label to metadata in Workflow processing
  for additional informations.
- Added a colorbar label to the PydidasPlot2d
- Improved the FitSinglePeak plugin to give better information about the output.
  
Bugfixes
--------

- Fixed an issue with the font size in Unix systems.
- Fixed outdated docstring for FrameLoader plugin class.
- Fixed an issue with the PluginCollectionBrowser widget which did not filter
  the sub-categories for processing plugins.
- Fixed outdated FioMcaLineScanSeriesLoader to work with latest release.
- Fixed an issue with datatypes in the ImageSeriesOperationsWindow.
- Fixed issues with Azimuthal sector integration Parameters which were not
  hashable.
- Fixed an issue with AppRunner threads sending their finished signal 
  prematurely on slower cpus.
- Fixed an issue in the pydidas_gui script when restoring a GUI state which 
  was invalid.
- Fixed an issue with importing the Mask file from pyFAI CalibrationContext.
- Fixed an issue with the FitSinglePeak plugin metadata when the first image
  was invalid.
- Fixed an issue where the node labels would not be displayd in the Workflow 
  tree editor.
- Fixed an issue with the ParamIoWidgetFile's FileDialog if the corresponding 
  Parameter value is not a valid path.
- Added a file exists check to the SubtractBgImage plugin.
- Fixed an issue with the ExtractAzimuthalSectors plugin when the azimuthal 
  values did not cover the full 360 degree.
- Fixed an issue with Hdf5 file loaders when using the same workflow for 
  processing files with different number of images each in one session.
- Fixed an issue preventing from resetting Parameter.choices to None.
- Fixed an issue in Dataset when squeezing multi-dimensional arrays with size 1.
- Fixed an issue when copying Dataset metadata which would not create new 
  objects.
- Fixed an issue when importing results of shape (1,) from Hdf5 files.


v23.1.25
========

Improvements
------------

- Added zenodo DOI to CFF
- Updated logo


v23.1.17
========

Major changes
-------------

- Changed the version numbering to YY.MM.DD
- Reorganized SetupScan and SetupExperiment and renamed them to ScanContext and
  ExperimentContext in the contenxts sub-package.
- Added core.fitting sub-package which allows to easily add more fitting 
  functions.
- Moved the global detector mask from the settings to the ExperimentContext
  to allow easier switching between processing different experiments.

Improvements
------------

- Improved documentation target names to unclutter namespace.
- Improved the multiprocessing speed by optimizing the functions.
- Added CITATION.CFF file.
- Added licenses for texts and images.
- Added a PyFAIazimuthalSectorIntegration plugin for arbitrary sectors.
- Added a menu entry in "help" to show the paths to the log and config files.
- Added the "property_dict" property to Dataset to get all properties at once,
  for example for copying.
- Added import_state and export_state methods to the BaseApp
- Changed missing results (i.e. not yet procesed) values to nan to have the 
  full range of the colormap available for the results.
- Changed the BaseApp.multiprocessing_pre_run and _post_run to return from
  NotImplementedError to simplify creating simple apps.
- Added an initialize_shared_memory method to the BaseApp for consistency.
- Removed the (unused) option to add Parameters to objects with keyword 
  arguments.
- Added the option to set Parameter values at object instantiation with 
  keywords.
- The DefineExperimentFrame now also checks for a mask file, if a detector mask
  has been imported from file for the pyFAI calibration.
- Reworked the RemoveOutlier plugin to be more robust.
  
Bugfixes
--------

- Fixed an issue with rois and locally (i.e. in the plugin) declared masks in
  pyFAIintegrationBase plugin.
- Fixed an issue with double initiation of the AzimuthalIntegrator in the 
  pyFAI2dIntegration plugin.
- Fixed an issue with decorator for multi-dim processing if the Plugin does not
  have detailed results.
- Fixed an issue in the Hdf5DatasetSelector which did not display the full 
  dataset name.
- Fixed an issue with the ShowDetailedPluginResults window which did not show 
  the selector for multi-dim processing if another result had been displayed 
  before.
- Fixed an issue in the FitSinglePeak plugin where detailed results were not 
  available for minimum peak heights.
- Fixed the parser for the CompositeCreatorApp.
- Fixed an issue with multiprocessing_carry in the BaseApp (relavant for 
  serial processing only).
- Fixed an issue with importing a incomplete state file.


v0.1.14
=======

Major changes
-------------

- Reorganized SetupScan and SetupExperiment and renamed them to ScanContext and
  ExperimentContext in the contenxts sub-package.
- Added core.fitting sub-package which allows to easily add more fitting 
  functions.
- Moved the global detector mask from the settings to the ExperimentContext
  to allow easier switching between processing different experiments.

Improvements
------------

- Improved documentation target names to unclutter namespace.
- Improved the multiprocessing speed by optimizing the functions.
- Added CITATION.CFF file.
- Added licenses for texts and images.
- Added a PyFAIazimuthalSectorIntegration plugin for arbitrary sectors.
- Added a menu entry in "help" to show the paths to the log and config files.
- Added the "property_dict" property to Dataset to get all properties at once,
  for example for copying.
- Added import_state and export_state methods to the BaseApp
- Changed missing results (i.e. not yet procesed) values to nan to have the 
  full range of the colormap available for the results.
- Changed the BaseApp.multiprocessing_pre_run and _post_run to return from
  NotImplementedError to simplify creating simple apps.
- Added an initialize_shared_memory method to the BaseApp for consistency.
- Removed the (unused) option to add Parameters to objects with keyword 
  arguments.
- Added the option to set Parameter values at object instantiation with 
  keywords.
- The DefineExperimentFrame now also checks for a mask file, if a detector mask
  has been imported from file for the pyFAI calibration.
- Reworked the RemoveOutlier plugin to be more robust.
  
Bugfixes
--------

- Fixed an issue with rois and locally (i.e. in the plugin) declared masks in
  pyFAIintegrationBase plugin.
- Fixed an issue with double initiation of the AzimuthalIntegrator in the 
  pyFAI2dIntegration plugin.
- Fixed an issue with decorator for multi-dim processing if the Plugin does not
  have detailed results.
- Fixed an issue in the Hdf5DatasetSelector which did not display the full 
  dataset name.
- Fixed an issue with the ShowDetailedPluginResults window which did not show 
  the selector for multi-dim processing if another result had been displayed 
  before.
- Fixed an issue in the FitSinglePeak plugin where detailed results were not 
  available for minimum peak heights.
- Fixed the parser for the CompositeCreatorApp.
- Fixed an issue with multiprocessing_carry in the BaseApp (relavant for 
  serial processing only).
- Fixed an issue with importing a incomplete state file.


v0.1.13
=======

Improvements
------------

- Made Datasets hashable.
- Added a copy method to Datasets to overwrite the generic numpy method and to
  copy the metadata as well as the array.
- Added a "circular" colormap named 'Wheel' to silx.
- Added automatic update of details in the WorkflowTestFrame.
- Tweaked the processing speed of pyFAI plugins by moving the fixed kwargs setup
  to the pre_execute method.
- Added features in the CompositeCreatorApp to control the direction in which
  images are inserted and the orientation of the inserted images.
- Added functionality that each import / export button and each fixed Parameter
  (i.e. not those in plugins) keeps a persistent reference to its last directory
  to allow opening the last directory for this entry.
- Loading a "wrong" yaml file to import ExperimentSetup settings now raises a 
  UserConfigError instead of an Assertion error.


Bugfixes
--------

- Created a workaround for an issue with pyFAI ElidedLabel class toolTip.
- Fixed an issue with deepcopies in the generic ObjectWithParameterCollection
- Fixed an issue with an inconsistent minimum size of the 
  PluginCollectionPresenter
- Fixed an issue with 1D pyFAI Plugin initializations.
- Fixed an issue with nodeIDs of PLugins in imported WorkflowTrees
- Added missing qtpy to requirements which was not missing.
- Fixed an issue in the CompositeCreatorFrame with aborting the AppRunner
- Corrected function call in ExportEigerPixelmask window.
- Fixed the docstring for the core.utils.Timer class.
- Fixed an issue with the CompositeImageManager and changed global max image
  size changes after instantiation.
- Fixed an issue in the filelist manager with file sorting.
- Fixed an issue with restoration of the CompositeCreatorFrame.
- Fixed an issue with same hashes for identical Dataset arrays.
- Fixed an issue with the tooltip event filter not exiting correctly.
- Fixed an issue where loading a non-existing state would crash the pydidas gui.

  
v0.1.12
=======

Improvements
------------

- Fields for filenames now accept drops from the OS's explorer.
- Added a CorrectSplineDistortion Plugin to apply a Fit2D / pyFAI spline on a 
  detector image.
- Dataset axis properties now default to empty strings and numpy.aranges in the
  correct length instead of None.

Bugfixes
--------

- Fixed an issue where destroyed QObjects were still referenced in the 
  SingletonFactory.
- Fixed an issue with persistent object references in the SingletonFactory for
  destroyed C++ Qt objects.
- Fixed an issue with the manual import of state files.
- Fixed an issue with the Histogram in images which include NaN.
- Fixed  an issue with 1D pyFAI integration plugins and a missing definition.


v0.1.11
=======

Major changes
-------------

- Added a Utilities frame to have easy access to various utility windows.
- Added new utility windows (Mask editing, file series operations)
- Added a global default colormap for users to select.
- Moved input settings (directory, filename pattern) to SetupScan class
  and out of the individual input plugins.

Improvements
------------

- Removed the GlobalConfigurationFrame and moved content directly to
  GlobalConfigWindow.
- Added fit2d mask images to the recognized file types.
- Child windows will now be closed upon exiting the main GUI window.
- Added a F1 help shortcut to all independent pydidas windows.
- Added an option to remove a single node from the WorkflowTree while 
  keeping its children.
- Added a data dimension consistency check to WorkflowNode
- Added multiplicity parameter to SetupScan to account for multiple images
  at the same position.
- Updated SetupScanFrame.
- Overhauled ImageMetadataManager input file selection.
- Renamed workflow/result_savers package to workflow/result_io because it
  also includes import capabilities.
- Added "move scan dimension" functionality in the SetupScanFrame.
- Updated documentation to current state.
- Updated the names of SetupScan Parameters for consistency.
- Fixed directory handling of DirectorySpyApp to always use directory_path
  Parameter.
- Separated global settings in "global settings" and "user config" to
  facilitate finding the proper settings for users.
- Added a new Plugin to extract a subset of azimuthal sectors from pyFAI 2D
  integration.
- Updated the documentation.
- Moved base svg images for the documentation to pydidas_images
- Added feature to remove all local pydidas logs.
- Organized processing plugins according to subtypes.
- Details for all sub-points are now available for multi-dimensional processing


Bugfixes
--------

- Fixed an issue with the canvas resize buttons in empty 2d plots.
- Fixed missing kwargs in PydidasPlot2D class.
- Fixed minor bugs in widget layout settings.
- Fixed an issue with the config state paths.
- Fixed an issue with removing a node when it has neither parent nor children.
- Fixed an issue with Plugin Parameter tweaking which did not call the 
  Plugin's pre_execute method.
- Fixed an issue where destroyed QObjects were still referenced in the 
  SingletonFactory.
- Fixed an issue with persistent object references in the SingletonFactory for
  destroyed C++ Qt objects.


v0.1.10
=======

Major changes
-------------

- Changed the handling of storing persistent information for the user 
  (Qt QSettings) to be version specific which allows to work with multiple
  pydidas versions in parallel.
- Added a "Always store results" flag to all plugins to allow saving of 
  intermediary data without having to use the "Keep Data" plugin. The keep data
  plugin has been removed.
- Added functionality to run selected 1d-processing plugins (FitSinglePeak,
  Remove1dPolynomialBackground) with multidimensional input data.
- Added functionality to re-order WorkflowTrees on the fly.
- Added functionality to re-order WorkflowTrees using drag & drop in the 
  graphical user interface.
- Added new feature in 2D plots to convert the coordinates to polar coordinates
  using the calibration information.

Improvements
------------

- Moved all frames and framebuilders to subpackage in gui package.
- Added the plugin names to the node result titles in case that no
  user-defined node label has been set.
- The active node is now handled by the Tree itself to have consistent and
  up to date behaviour for all consumers.
- Added a context menu in the PluginCollectionBrowser to replace plugins and 
  add them to the Workflow at designated positions.
- Added coordinate transformations to data browser (for images the same size as
  the detector defined in the SetupExperiment.
- Added feature to automatically store the GUI state on exit and added a menu
  action to restore the exit state.
- Sanitized all module docstrings.

Bugfixes
--------

- Fixed an issue with the selection of 1D data in plots.
- Fixed an issue with non-existing config paths.
- Fixed an issue with the Pyfai2dIntegration plugin.
- Fixed an issue when plugins with 2d results would return 1d output
  data (e.g. 2d-integration with only one azimuthal value).
- Fixed an issue with azimuthal units in radians in the pyFAI 2d integration
  plugin.
- Fixed an issue with RemoveOutlierPlugin which did not dectect peaks of 
  diffenent sign (e.g. in background-corrected data).  
- Fixed an issue with hanging initialization when restoring the GUI state 
  at start-up.
- Fixed an issue with the WorkflowTree edit canvas not updating correctly 
  after editing the tree and restoring the previous state.
- Fixed an issue with tweaking plugin parameters with integer input data
  (i.e. loaders).
- Fixed an issue with storing the latest open directory in the data browser.
- Fixed an issue with the integration ranges in the pyFAI integration plugin.
  

v0.1.9
======

Major changes
-------------

- Added a new SilxPlot2D class which allows to limit the figure canvas to the 
  data dimensions and back to the full window. This class also has a new feature
  to crop the top percentage of the histogram, for example to remove dead pixels.
- Added keyboard shortcuts (F1) to open the help for the active frame.
- Added a script to remove all local files and registry settings for the current 
  user.
- Added a feature to display detailed plugin results in the WorkflowTestFrame.
- Changed Exception handling and added a custom UserConfigError exception with 
  its own handling.
  
Improvements
------------

- Dataset class has been reworked to function correctly with more numpy ufuncs,
  in particularly with np.take.
- Added settings for displaying only a limited floating point precision of 
  Parameters.
- Removed redundant button to store pyFAI calibration settings.
- Changed Parameter names in ScanSetup class for better consistency.
- Changed names of buttons from "load" or "save" to "import" or "export" for 
  consistency.
- Importing WorkflowResults now also updates the ScanSetup class to allow viewing
  imported results as a scan timeline and to have the correct labels.
- The nodes in the WorkflowTree editor now also display the node IDs and labels.
- If the app is busy with locally running the Workflow in the TestWorkflowFrame,
  the mouse cursor will show a busy system.
- Added an uninstaller script to remove registry information and local data
  (e.g. logfiles)

Bugfixes
--------

- Fixed an issue with Parameter updates in the ViewResultsMixin
- Fixed an issue with QComboBoxes being too small for the text to display the
  full text.
- Fixed an issue with the PluginInWorkflowBox labels after restoring these from
  the frame state.
- Fixed an issue with WorkflowTree results export and labels with special 
  characters.
- Fixed an issue with running the Workflow with only exported data and no local
  data which raised an exception.


v0.1.8
======

Major changes
-------------

- Updated fitting functions and included a true Voigt profile, which (in its
  scipy implementation) is faster to compute than the pseudo-Voigt.
- Added a functionality to load and visualize results which have been exported
  with the pydidas WorkflowResultsSaver
- Changed handling of file extensions to extensions without leading ".".

Improvements
------------

- Added a check on the length of axis ranges in Dataset.

Bugfixes
--------

- Fixed compatibility with latest Qt (Qt 5.15)
- Fixed an issue with dictionary passing between plugins which propagated metadata 
  to up the WorkflowTree.
- Fixed an issue with Datasets where the __array_finalize__ method (e.g. slicing)
  passed the same dictionary instance of metadata instead of a copy.
- Fixed an issue with the MaskImage plugin where is did not retain the input image 
  metadata.
- Fixed an issue with the update of the node description in the WorkflowTestFrame.
- Hotfix for plugin path setting at the first startup in new system.
- Fixed an issue with data shapes for FitSinglePeak plugins.
- Fixed an issue with logger output formatting in WorkflowNode
- Fixed an issue with creation of a hdf5 dataset with the same key in a file.
- Fixed an issue in  WorkflowResultsSelector with selection of data ranges when no 
  range was given.
- Fixed an issue with the order of axis ranges in transposed Datasets.  
