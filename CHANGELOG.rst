.. Copyright 2021 - 2025, Helmholtz-Zentrum Hereon
.. SPDX-License-Identifier: CC0-1.0


v25.04.08
=========

Improvements
------------
- Added a plugin to save 2d data in ASCII format.
- Improved the behaviour of the WorkflowTestFrame to display only results from the 
  current WorkflowTree.
- Improved the fio input plugins to allow more generic metadata definitions.
- Modifed the way custom plugin widgets are handles and create a base class
  for custom widgets to inherit from.
- Added a generic xscale to fio plugins to have a more generalized use case covered.
- Added a plugin to load 1d profiles from HDF5 files.
- Moved calculation of radial unit conversions to core.utils.scattering_geometry
  module.
- Added plugins for sin^2(chi) residual stress calculations.
- Added importers/exporters for HDF5 formats for Scan, DiffractionExp and 
  ProcessingTree.


Bugfixes
--------
- Fixed an issue when graphically selecting integration regions using "Q / A^-1"
  or "2theta / rad" as units.
- Fixed an issue in the DataViewer where the selected button was not updated 
  when the view was changed due to the data dimensionality.
- Fixed an issue in the WorkflowTestFrame when switching the dataset with active
  selection based on data values.
- Fixed the error message when user select a HDF5 dataset which does not exist.
- Fixed an issue which occured when running workflows with no nodes with results.
- Fixed an issue where selecting a filename would introduce a trailing space.
- Fixed missing Parameters for output formats and overwriting in WorkflowRunFrame
- Fixed an issue in the pyFAI names where the LUT entries were missing.

v25.03.17
=========

Improvements
------------
- Changed the structure of the repository. The source code for all subpackages is
  now located in the src/ folder
- Replaced the default azimuthal integration range to (-180, 180) or (0, 360)
  respectively instead of None to have more consistent ranges (pyFAI issue #2291)
- Updated Sum1dData plugin to use np.sum directly for improved performance.
- Extended Sum2dData plugin to work on an arbitrary number of dimensions.
- Added a calling option to add a `-screen <i>` command line option to force the 
  GUI on the selected screen.
- ExecuteWorkflowApp now works with dynamic plugin shapes, i.e. the plugin result
  shapes can be dynamically modified during runtime.
- Updated the classmethods of FitFuncBase to include attributes which correspond 
  to the fit result output labels.
- Added a test mode flag to the WorkflowTree to prevent the creation of directories
  in output plugins when testing workflows.
- Programmatic improvements:
    - Removed the basic_plugin class attribute from Plugins and shifted the check
      to the core code of the base plugins.
    - Changed the internal handling of multiprocessing arguments (e.g. Queue objects)
      for more streamlined code.
    - Added a multiprocessing Lock to worker process logging for consistent 
      output formatting.
    - Added a new signal to the BaseApp and app multiprocessing to prepare
      ExecuteWorkflowApp update.
    - Updated WorkflowResults contexts to accept dynamic result shapes.
    - Removed redundant code from plugins (because of changes in shape handling).
    - Switched to using ruff instead of black, flake8 and isort in github actions.
	- Moved the pydidas, pydidas_qtcore and pydidas_plugins folders to src.
	- Renamed `slaves` to `clones`
	- Changed the builder of the DefineScanFrame to use functions instead of an 
	  abstract class.
	- Restructured the layout of the __init__ files for more clarity.
	- Added a second category of importers named 'beamline file formats'
	 to Scan and added a second registry in the ScanIo.
	- Changed the creation of generic toolbar menus to use a dictionary which 
	  can easily be extended by 3rd parties.
	- Added widgets to select axes for data display also based on metadata.
- Improved the formatting when displaying Plugin information.
- Improved the behaviour of the logging and status widget and added options to
  hide and show it.
- Added support for pytest tests in the CI pipeline. 
- Added import functionality for Sardana FIO files to the Scan import.
- Added a range property to the Parameter to limit the allowed range of Parameters
  for numerical values.
- Pydidas result exports in hdf5 format writes metadata neXus-compatible
- Added a new interface for browsing and slicing data based on its metadata.
- Renamed WorkflowResults and WorkflowResultsContext to ProcessingResults
  (for the general class) and WorkflowResults (for the singleton instance)
  for consistency, similarly to ProcessingTree and WorkflowTree.
- Modified the ViewResultsFrame to use the new DataViewer for more 
  convenient data exploration.
- Modified the WorkflowRunFrame to use the new DataViewer for more convenient
  data exploration.
- Added a new plugin to load a series of MCA data from file files located in 
  a single directory.
- Added a new plugin to crop data by either its indices or data values.
- Modified the TestWorkflowFrame to use the new DataViewer for more convenient
  data exploration.


Bugfixes
--------
- Fixed an issue when trying to read hdf5 metadata from non-hdf5 files.
- Fixed in issue in Parameter where sub-type checking in tuple/set/list Parameters
  was not enforced.
- Fixed an issue with PydidasPlot2D when cs_transform was disabled.
- Fixed an issue with pickling unittest plugins loaded through the PluginRegistry.
- Fixed an issue in the WorkflowNode which allowed accessing outdated results.
- Fixed an issue when preparing to run an empty Workflow.
- Fixed an issue when restoring the GUI to a different screen in multiscreen systems.
- Fixed an issue with inspecting detailed results for fit plugins when the first 
  fit point had an invalid result (e.g. peak intensity too low).
- Fixed an issue when copying a ProcessingTree which had no nodes.
- Fixed an issue when entering `None` for path parameters.
- Fixed an issue with formatting of regex strings in the qr_presets
- Fixed an issue where the SplashScreen would still show when an exception was 
  raised during GUI initialization.
- Fixed an issue when the font family is not supportted by matplotlib where the
  user notification would not be correctly formatted.
- Fixed the pyFAIcalibFrame to be compatible with pyFAI 2024.09
- Fixed an issue with the WorkerController when the thread shutdown was toggled
  while waiting in a sleep state.
- Fixed a bug in fitting plugins which only returned a single fit parameter.
- Fixed a bug where WorkflowResults could not be exported again after import.
- Fixed an issue where the Fit plugin would not store the background at the peak
  positions correctly.
- Fixed an issue where a given y label in a Plot1D was overwritten by Dataset
  metadata.
- Fixed an issue in Dataset where calling .T would not transpose the axis metadata.
- Fixed an issue in PydidasPlot1D where optional dictionary entries were queried
  directly without a get call.
- Fixed an issue in pyFAI integration base when using radians as azimuthal unit
  and the full detector


v24.09.19
=========

Improvements
------------
- Replaced the data viewer in the DataBrowsingFrame with a modern silx 
  DataViewerFrame.
- Improved the design of the DataBrowsingFrame and selectors for raw or hdf5 
  data are now located directly above the plots.
- Added type-checking for Datasets axis_ranges and axis_units.  
- Added mean, sum, min, max, sort methods to Dataset to keep metadata 
  consistent.
- Added reshape metadata handling to Dataset.
- Added a new plugin to convert pyFAI integration results to d-spacing.
- Added check boxes for Parameters with only True/False choices.
- Improved the documentation for GitHub pages which now includes documentation
  for older versions.
- Added support for images with non-uniform axes.
- Added a new plugin to convert integration results to d-spacing.
- Removed dependency of qtawesome to circumvent issues with fonts in Windows.

Bugfixes
--------
- Fixed an issue where a exception message would be copied to the clipboard
  without clicking the corresponding button.
- Fixed an issue with using ROI in plugins in a WorkflowTree
- Fixed an issue when using slicing on importing Hdf5 files with pydidas 
  metadata.
- Fixed an issue in Dataset's flatten implementation.
- Fixed an issue with restoring the UI after the number of screens was reduced.  
- Fixed an issue in Dataset's reshape after using np.array with ndmin parameter.
- Fixed an issue when deleting the root WorkflowNode with multiple children.
- Fixed inconsistencies in plugin docstrings.
- Fixed an issue with fit plugins which would not forward the result units in 
  the WorkflowTestFrame on repeated calls.
- Fixed a bug in histogram calculations with high outliers.
- Fixed a bug where qtawesome would hand with access issues to fonts on Windows
  systems.
- Fixed an issue with silx plot widgets when changing the font size through
  PydidasQApplication.
- Fixed an issue with the restored window size after closing pydidas.
- Fixed an issue with the display of Parameter choices in the GUI when 
  Parameters only allowed True or False.
- Fixed an issue with sphinx (version >7) which changed built-in types when 
  running in the same process as the main program.
- Fixed an issue on linux where editing the WorkflowTree in the GUI caused a 
  segmentation fault.
- Fixed an issue in generic_node.connect_parents_to_children method.
- Fixed an issue when trying to open illegible hdf5 files in DataBrowsingFrame



v24.06.05
=========

Improvements
------------
- Improved the naming and tooltips of scan parameters with respect to the 
  file numbers and indices.
- Added the ParameterCollection creation the the ParameterCollectionMixin
  class initialization.
- Added a setting to change the default NaN color which is used to mark
  invalid or missing data.
- Separated the path for generic plugins from user-defined custom plugin paths
  for greater clarity.
- Programmatic improvements:
    - Changed the default behaviour of the hdf5 file loader to import the full
      dataset instead of only a single frame.
    - Allowed to use `None` for hdf5 dataset slicing to load the full dataset.
- Added an option to specify a required dimensionality when importing data.
- The import_data and export_data functions now read/write the pydidas Dataset 
  metadata to/from the file.
- Added a flag to toggle plugin detailed_results generation to minimize 
  overhead in full processing.
- Added support for np.ndarray as Parameter values.
- Added documentation for Plugin development.

Bugfixes
--------
- Fixed a display issue in the title of the logging dockable widget.
- Fixed an issue in the pyFAI calibration frame where the supported file 
  formats where not correctly available in the file dialog.
- Fixed an issue with settings the X-ray energy / wavelength in the 
  DiffractionExperimentContext on the command line with wrong data types.
- Fixed an issue with convenience type conversions in the Parameter class.
- Fixed an issue with possibly joining queues twice on exit of WorkerController.
- Fixed an issue with the `unregister_all_paths` method of the PluginRegistry
  which did not permanently remove the paths.
- Fixed an issue in the ImageSeriesOperationsWindow where the correctness of 
  the output filename was not checked until after the operation.
- Fixed an issue where Dataset axis ranges could be None.
- Fixed an issue where Dataset axis labels / units could be None.
- Fixed an issue in the ParamIoWidgetLineEdit where setting the value would 
  compare the new str with a generic typed item.
- Fixed an issue where a selection of a ´wrong´ mask by a user would raise
  a pyFAI assertion error without a human-readable error message.
- Fixed a bug which would display wrong numbers for allowed scan points in the 
  WorkflowTestFrame.
  

v24.03.25
=========

Improvements
------------
- Changed a number of filenames and paths (mainly in the documentation) to 
  reduce the total length of the file names.
- Updated files to new black 2024 style.
- Added pyFAI units for 'q / A^-1' and '2theta / rad'.
- Added Kratky-type (x vs. y*x**2) plots to the PydidasPlot1D class.

Bugfixes
--------
- Fixed an issue with propagation of plugin result shapes for fitting plugins.
- Fixed an issue where changing the ScanContext after processing would prevent 
  writing results to file.
- Fixed an issue where exporting data would store wrong contexts when changing
  the global contexts after processing.
- Fixed an issue with the pyFAIcalib frame where setting the detector first
  and then selecting an image would not allow to use the colormap adjustment 
  buttons in the plot widget.
- Fixed an issue with testing workflows when changing the contexts.
- Fixed an issue where WorkflowTree import exceptions where not correctly 
  handled.
- Fixed an issue when asking to display detailed results for a scan point and 
  no node is currently selected.
- Fixed an issue trying to open binary (i.e. raw) files in the DataBrowsingFrame
- Fixed an issue which would not display the correct default colormap after the 
  user changed the default.
- Fixed an issue in the updater script with versions which had leading zeros.
- Fixed an issue in the remove_local_files script when directories did not 
  exist.  
- Fixed an issue with accessing WorkflowResults when the PluginCollection has
  been re-initialized.
  

v24.01.18
=========

Improvements
------------

- Added Github actions for formatting, unittesting and automatic deployment
  of github pages.
- Updated metadata files (README, sphinx make-files, .flake8)
- Changed the behaviour of the GUI file dialogues to (re)use only one instance
  of the file dialog to mitigate issues with slow file systems.
- ParameterWidgets with numbers which allow None now treat an empty string
  as None.
- Multi-peak fitting plugins now start numbering peaks with zero to be 
  consistent with python style.
- Prepared the structure for fitting plugins with an arbitrary number of
  peaks.

Bugfixes
--------
- Fixed an issue with ipython where pydidas could not be imported in the 
  ipython console due to ipython's running QApplication.
- Fixed an issue with fitting plugins where peak boundaries could lead to
  an exception when the initial peak fit was outside of the boundaries.
- Fixed an issue in the TweakPluginParameterWindow where the stratch scaling
  was wrong.
- Fixed an issue with the error message due to missing parameters in the 
  run_pydidas_workflow script.
- Fixed an issue with the ResultSelectionWidget call of the 
  ShowInformationForResult window.


v23.12.08
=========

Improvements
------------

- Added an exporter for SpecFile .dat format and merged all exporters for 
  ASCII-type files in a single plugin.
- Added additional keyword options to the AcknowledgeBox.
- Added update checks to the menu and to the pydidas_gui startup script.
- Added an option to change the logging level with a command line calling 
  option '-logging-level LEVEL'.
- Added the ExecuteWorkflowRunner class to handle running workflows from the 
  command line.

- Programmatic improvements:

    - Renamed the _WorkflowTree to ProcessingTree to allow easier direct 
      access  the class and updated references.
    - Added a feature to the AppRunner which automatically calls the 
      multiprocessing_pre_run method of the input app if it has not yet 
      been called manually by the user.
    - Added a status property to the PydidasQApplication and connected 
      it to the PydidasStatusWidget for easier submission of status 
      messages.
    - Added a FileReadError exception class and exception catching in 
      the file reading.
    - Changed the names of the Scan import/export registry classes to more 
      consistent names.
    - Added a context manager to handle file reading errors more
      generically.

Bugfixes
--------

- Fixed an issue where boolean QSettings could not be read automatically
  without explicit dtype.
- Fixed a Qt5 issue with font scaling in the AcknowledgeBox widget.
- Fixed an issue with persistent plugin paths which were not updated in case
  that pydidas has been moved to a new location.
- Fixed an issue where tweaking a Plugin in the WorkflowTree would clear the 
  plugin's node_id.
- Fixed an issue where the result selection would reset after processing 
  when results were already selected during processing in the 
  WorkflowRunFrame.
- Fixed an issue in the RunWorkflowFrame where aborting the processing would
  lead to a frozen GUI.
- Fixed an issue with plugin paths during unittests when production and 
  development versions are installed on the same machine.
- Fixed an issue with consistency signals in PluginInWorkflowBox widget.
- Fixed an issue with unsorted files in the filelist manager in Unix.
- Fixed an issue with QSettings storage of bool values in Unix.
- Fixed an issue when copying a plugin would create a new 
  DiffractionExperiment and not keep the global context
- Fixed an issue with updating the PluginCollection from the GUI's 
  UserConfigWindow.
- Fixed an issue where running the sphinx-build externally would trigger 
  building the documentation twice.


v23.10.20
=========

Improvements
------------

- General improvements:

    - Moved the functions to get resource icons and images to the resources
      subpackage.
    - Created a pydidas_qtcore package to bundle all the core Qt functionalities
      which need to be loaded prior to starting the UI.
    - Added support for changing the default font and fontsize.
    - Removed STANDARD_FONT_SIZE constant and added dynamic standard_font_size 
      to PydidasQApplication.
    - Improved the detailed output from fitting plugins.
    - During active processing, editing diffraction setup, scan and workflow 
      are disabled.
    - All widgets now scale dynamically with font height and width to allow
      using pydidas with any system font.
    - Added an option to select points for the beamcenter with a 2-click
      method to select the peak centers more easily.
    - Added option to import Fit2d geometry for the DiffractionExperiment
    - Added a version tag to exported WorkflowTrees to improve handling of 
      trees from different versions with changed requirements.
    - Improved the docstring for fitting plugins to allow better feature
      usage also by inexperienced users.
    - Added support for image masks in the manual beamcenter selection window
      to filter out the masked values for the histogram.
    
- Programmatic updates:

    - Changed handling of Qt icons in preparation for Qt6 support.
    - Changed the factory creation of ParameterWidgets to remove patched 
      circular dependencies.
    - Changed the widgets.factory to remove unnecessary intermediate functions
      for widget creation and added more custom pydidas widgets.
    - ParameterWidgets use the new Pydidas widgets and scale automatically with
      the font size.
    - Added type hints to contexts, gui, widget subpackages.
    - Updated the nomenclature of PydidasQSettings method names for 
      consistency.
    - Updated the names of Dataset "update_axis" methods for 
      consistency.
    - Moved the generic parameter definitions to core.generic_params subpackage.
    - Renamed _PluginCollection to PluginRegistry to have a distinct name 
      from its singleton instance 'PluginCollection'.

Bugfixes
--------

- Fixed an issue with wrong signal signaturs in WorkflowTreeEditManager.
- Fixed a bug in the Remove1dPolynomialBackground plugin which forced a 
  polynomial order setting of 3.
- Fixed an issue with pyFAI's calib2 app and additional argparse arguments.
- Fixed an issue when deleting the root node in a GenericTree.
- Fixed an issue where plugin labels were not updated in the WorkflowEditFrame
  when the plugins had a custom widget.
- Fixed an issue when displaying Hdf5 files in the DirectoryExplorer which did
  not have any valid datasets.
- Fixed a bug when copying objects (Apps, Plugins) with objects with linked
  Parameters where the linking got lost.
- Fixed an issue with the RoiSliceManager and numpy integer datatypes.
- Fixed a bug in the GenericNode where copying the node would keep references
  to the original parent.
- Fixed an issue in the DirectorySpyApp with changes in the exceptions raised
  from tifffile if a tiff file could not be read.
- Fixed a bug in the FWHM calculation of the scipy Voigt profile.


v23.07.05
=========

Improvements
------------

- General improvements:

    - Exposed the read_hdf5_dataset function directly in 
      pydidas.data_io.low_level_readers.
    - Added a new action to quickly access silx's autoscale to mean +/- 3 std  
      in PydidasPlot2D and PydidasImageView
    - PydidasPlot2D will now compare the image size with the detector image size
      and if the two images are of the same size, it will set the aspect ratio
      to 'same'.
    - Removed the '3D' visualization option from pyFAI calibration because it 
      requires pyopengl and raises exceptions when the Detector is not yet 
      set up and when the 3D visualization window is closed.
    - Improved the widgets.factory to allow parent string references.
    - Added a frame for image mathematics.
    - Added an option in the TestWorkflowFrame to select scan points by their 
      detector image number.
    
- Plugins:

    - Added a 'total count intensity' output to fit plugins.
    - Added 'detailed_results' to CreateDynamicMask plugin to check the created
      mask.
    - Added a 'rolling average' plugin for 1D data.

Bugfixes
--------

- Fixed an issue in the pydidas_gui script which caused a segmentation fault on 
  exit in Linux.
- Fixed an issue with Qt's QStandardLocation folder name inconsistencies between
  windows and Linux.
- Improved an exception message for Parameter's value setter.
- Fixed an issue with the centering of the WorkflowTree in the WorkflowEditFrame
- Fixed an issue in the peak fitting plugins where narrow peaks were not picked 
  up correctly during initial parameter estimates.
- Fixed an issue in the DirectorySpyApp where the tifffile would return an empty
  array instead of an exception for unreadable files.
- Fixed an issue in the DirectorySpyApp when the directory is empty.
- Fixed an isssue in the pyFAIintegrationBase, where setting the azimuthal ROI
  would not work, if the boundaries where updated in a specific order.
- Fixed an issue where the GUI scripts would stop during state restoration if 
  the state was invalid.
- Fixed an issue in the BaseFitPlugin where changing the output settings would
  not update the shape correctly.
- Fixed an issue where the result selection range was not updated correctly 
  after changing the scan dimensions.
- Fixed an issue where specifying the peak starting guess outside of the data
  range would raise a ValueError.
- Fixed an issue with Scan multiplicity > 1 which would not store results 
  correctly.
- Fixed an issue in the ShowInformationForResult window with Scan multiplicity 
  > 1.
- Fixed an issue with the basic PydidasWindow when not running with a 
  PydidasQApplication.


v23.06.16
=========

Improvements
------------

- Plugins:

    - Added an option to apply a multiplication factor to the background in the
      SubtractBackgroundImage and Subtract1dBackgroundProfile plugins.
    - pyFAI integration plugins now can accept custom masks as keyword argument
      in the execute method.
    - Added a new plugin for creating dynamic detector masks based on data
      thresholds.
    - Added new plugins for double and triple peak fitting.
    - The output selection for fitting plugins can now be done using checkboxes
      for the various options.
    - Added Parameters for pyFAI's 'correctSolidAngle' and 
      'polarization_correction' to pyFAI plugins.
    - Reworked the fitting plugins to add double and triple-peak fitting
      capabilities.
    - Added a 'background at peak' output for peak fitting plugins.
      
- General improvements:

    - Added a 'Copy experiment description from diffraction context' button in 
      the QuickIntegrationFrame to allow using an existing calibration.
    - Manually setting the beamcenter from points now works also with a single
      selected points, even if more points are in the list.
    - The Define diffraction setup frame now also displays the derived position
      of the beamcenter.
    - Added a splash screen at startup to display the give feedback about 
      startup of the GUI.
    - Updated the ParameterCollectionMixin to accept all kwargs. Kwargs matching
      Parameters will update their values and other kwargs will be ignored.
    - Added a 'param_values' property to the ObjectWithParameterCollection for 
      quicker access.
    - Added functionality to the widgets factory to reference parent_widgets by
      their string reference key.
    - Added a script to update pydidas in place in the current python 
      environment.
    - Added an entrypoint script to open the documentation.

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
- Fixed an uncomprehensible exception message when the selected indices for
  reading a hdf5 dataset were out of bounds.
- Fixed an issue with copying Parameters, when the default value was not in the 
  currently allowed choices.
- Fixed an issue in Dataset when adding new dimensions after the last dimension.
- Fixed an issue in ParamIoWidget when the type conversion was not successful.
- Fixed an isssue in Dateset, where the getitem_key was not reset after 
  returning a single item instead of a new Dataset.
- Fixed an issue with custom plugin configuration widgets with advanced 
  parameters.
- Fixed an issue when starting up where calling the sphinx process to create 
  the documentation would crash the GUI.


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
    - contexts.scans importers can now select which Scan instance to 
      import to.
    - contexts.diff_exp importers can now select which 
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
