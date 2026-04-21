..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2026, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. |Parameter| replace:: :py:class:`Parameter <pydidas.core.Parameter>`
.. |ParameterWidget| replace:: :py:class:`ParameterWidget <pydidas.widgets.parameter_config.ParameterWidget>`


.. _dev_guide_parameter_widget:

ParameterWidget full structure and API
======================================

.. note::

    This documentation page has been partially created using the AI-tool GPT-5.3-Codex.

.. contents::
    :depth: 2
    :local:

ParameterWidget internal widget structure
-----------------------------------------

The |ParameterWidget|
is a composite widget designed to display and edit a single :py:class:`Parameter <pydidas.core.Parameter>`.
It is composed of three main widgets:

1. A label widget (:py:class:`PydidasLabel <pydidas.widgets.base.PydidasLabel>`)
   to show the Parameter name. Its text corresponds to the Parameter's ``name`` property.
2. The concrete I/O widget (see below)
3. A label widget (:py:class:`PydidasLabel <pydidas.widgets.base.PydidasLabel>`) to show
   the Parameter's unit, if defined. Its text corresponds to the Parameter's ``unit``
   property and is hidden if no unit is defined.


.. code-block::

    +------------------------------------------------------------------------+
    |                        ParameterWidget                                  |
    |              (composite wrapper for one Parameter)                      |
    |                                                                         |
    |  +------------------+  +-------------------------+  +----------------+  |
    |  | Label widget     |  | I/O widget              |  | Unit widget    |  |
    |  | (PydidasLabel)   |  | (BaseParamIoWidget*)    |  | (PydidasLabel) |  |
    |  |                  |  |                         |  | (Label)        |  |
    |  +------------------+  +-------------------------+  +----------------+  |
    |                             ^                                           |
    |                             | selected by dtype/choices                 |
    |                             |                                           |
    |         +--------------------------------------------------+            |
    |         | ParamIoWidgetCheckBox / ParamIoWidgetComboBox /  |            |
    |         | ParamIoWidgetFile / ParamIoWidgetHdf5Key /       |            |
    |         | ParamIoWidgetLineEdit                            |            |
    |         +--------------------------------------------------+            |
    +-------------------------------------------------------------------------+


ParameterWidget args and kwargs
-------------------------------

The :|ParameterWidget| constructor takes a single argument: The associated |Parameter|
instance. The widget behaviour will be determined by the keyword arguments. The
following keyword arguments are supported:

.. list-table::
    :widths: 20 10 70
    :header-rows: 1
    :class: tight-table

    * - kwarg
      - Type
      - Description
    * - ``width_text``
      - float, optional
      - Relative width of the Parameter name label, as a fraction of the global
        ``font_metric_width_factor``. The default is set to 55% of the total width,
        (defined in ``pydidas.core.constants.PARAM_WIDGET_TEXT_WIDTH``).
    * - ``width_unit``
      - float, optional
      - Relative width of the unit label, as a fraction of the global
        ``font_metric_width_factor``. The default is set to 7% of the total width,
        if the unit field is not empty. This default is defined in
        ``pydidas.core.constants.PARAM_WIDGET_UNIT_WIDTH``. A value of ``0``
        will disable the unit label entirely.
    * - ``linebreak``
      - bool, optional
      - When ``True``, the name label is placed on its own row above the I/O
        widget instead of side-by-side. This is useful for |Parameter| with long
        values like file system paths. The default is ``False``.
    * - ``font_metric_width_factor``
      - int, optional
      - The width of the widget in multiples of the font metric width. If None,
        the widget will use the default size policy. The default is
        ``pydidas.core.constants.FONT_METRIC_CONFIG_WIDTH``.
    * - ``validator``
      - QValidator, optional
      - A custom validator to be used in the I/O widget, if applicable.
        The default is None.
    * - ``precision``
      - int, optional
      - The precision for floating point values. Values will be rounded to
        precision digits. The default is defined in
        ``pydidas.core.constants.FLOAT_DISPLAY_ACCURACY``.
    * - persistent_qsettings_ref
      - str, optional
      - An optional QSettings reference key passed to the I/O widget for
        persisting file-dialog directories across sessions. The default is None.

In addition, all kwargs supported by the parent class :py:class:`EmptyWidget
<pydidas.widgets.factory.EmptyWidget>` are also supported and passed to the
constructor.

Signals
-------
The following signals are emitted by the ``ParameterWidget`` simultaneously
to support both direct access to the new value and a generic change notification:

- ``sig_new_value(str)``: emitted with string representation of new input.
- ``sig_value_changed()``: emitted when a value was changed.

These signals are passed through from the underlying I/O widget:

.. code-block::

    +-----------------+
    |    User input   |
    +-----------------+
            |
            v
    +-----------------+
    |   <I/O widget>  |         +--------------------+
    |   emit_signal() |  ---->  |    <I/O widget>    |         +-------------------+
    +-----------------+         | sig_new_value(str) |  ---->  |  ParameterWidget  |
       |                        +--------------------+         | update associated |
       |                                      |                |  Parameter value  |
       |      +----------------------+        |                +-------------------+
       +--->  |      <I/O widget>    |        |
              |  sig_value_changed() |        |      +--------------------+
              +----------------------+        +--->  |  ParameterWidget   |
                        |                            | sig_new_value(str) |
                        |                            +--------------------+
                        |
                        |       +---------------------+
                        +---->  |   ParameterWidget   |
                                | sig_value_changed() |
                                +---------------------+


.. note::

    Note that programmatic updates to the |Parameter| value are not automatically
    reflected in the widget display. To synchronize the display with the current
    Parameter value, use the :py:meth:`update_from_param
    <pydidas.widgets.parameter_config.ParameterWidget.update_from_param>` method.

Signal and Data Flow: User Edit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The typical interactive edit flow is:

1. User edits text/selection in a concrete I/O widget.
2. I/O widget calls ``emit_signal()`` from ``BaseParamIoWidgetMixIn``.
3. ``emit_signal()`` compares against ``_old_value`` and emits:

   - ``sig_new_value(str)`` with ``current_text``
   - ``sig_value_changed()``

4. In ``ParameterWidget.__create_param_io_widget()``, ``sig_new_value`` is
   connected to:

   - ``ParameterWidget.set_param_value`` (state update)
   - ``ParameterWidget.sig_new_value`` (forwarding)

5. ``ParameterWidget.set_param_value`` applies the new value to ``param.value``.
6. On conversion/config errors, the widget resets to old Parameter value and
   re-raises.

This keeps data conversion authoritative in the ``Parameter`` layer while the
widget layer stays responsible for display and signal semantics.

Signal and Data Flow: Programmatic Update
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Programmatic update without changing Parameter state:

1. Caller invokes ``ParameterWidget.update_display_value(value)``.
2. Composite widget forwards to ``io_widget.update_display_value(value)``.
3. I/O widget updates display in a non-emitting way (often using
   ``QSignalBlocker`` or a signal-free setter path).
4. Parameter object remains unchanged.

Programmatic update with Parameter state change:

1. Caller invokes ``ParameterWidget.set_value(value)``.
2. Underlying I/O widget ``set_value`` updates display and emits change signals.
3. Connected ``set_param_value`` updates the Parameter.

Choice Update Flow
^^^^^^^^^^^^^^^^^^

When Parameter choices change dynamically:

1. Parameter receives new value and choices.
2. ``ParameterWidget.update_choices_from_param()`` is called.
3. If current I/O widget class no longer matches requirements, the widget is
   recreated in ``__create_param_io_widget()``.
4. For choice widgets, ``update_choices(..., emit_signal=False)`` syncs display
   without broadcasting unintended edits.


Properties
----------

.. list-table::
    :widths: 20 80
    :header-rows: 1
    :class: tight-table

    * - Property
      - Description
    * - ``io_widget``
      - [read-only] The currently selected I/O widget instance for the linked Parameter.
    * - ``display_value``
      - [read-only] Current displayed value from the underlying I/O widget.
    * - ``value``
      - The linked display (and Parameter) value in its native datatype. This
        property is read/write and will trigger updates to the display and emit
        change signals when set.

Methods
-------

.. list-table::
    :widths: 30 70
    :header-rows: 1
    :class: tight-table

    * - Method
      - Description
    * - ``update_display_value(value)``
      - Refresh only the widget display without updating Parameter state or
        emitting signals.
    * - ``set_value(value)``
      - Set value through the I/O widget, including normal signal behavior.
    * - ``update_choices_from_param()``
      - Rebuild or update selection widget choices from the choices of the
        underlying and linked Parameter.
    * - ``update_from_param()``
      - Update the widget display value from the linked |Parameter|.

I/O subclasses
--------------

Widget Selection Rules
^^^^^^^^^^^^^^^^^^^^^^

|ParameterWidget| chooses the I/O widget class from the Parameter metadata:

- bool-like choices -> :py:class`ParamIoWidgetCheckBox <pydidas.widgets.parameter_config.ParamIoWidgetCheckBox>`
- list of choices -> :py:class:`ParamIoWidgetComboBox <pydidas.widgets.parameter_config.ParamIoWidgetComboBox>`
- ``Path`` dtype -> :py:class:`ParamIoWidgetFile <pydidas.widgets.parameter_config.ParamIoWidgetFile>`
- ``Hdf5key`` dtype -> :py:class:`ParamIoWidgetHdf5Key <pydidas.widgets.parameter_config.ParamIoWidgetHdf5Key>`
- other -> :py:class:`ParamIoWidgetLineEdit <pydidas.widgets.parameter_config.ParamIoWidgetLineEdit>`

The selection is dynamic and can be updated to accommodate for changes in the
Parameter's metadata (e.g. new choices list) through the
:py:meth:`update_choices_from_param <pydidas.widgets.parameter_config.ParameterWidget.update_choices_from_param>` method.

Subclass Behavior Matrix
^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
    :widths: 24 25 51
    :header-rows: 1

    * - Class
      - Primary UI control
      - Key behavior
    * - ``ParamIoWidgetCheckBox``
      - Checkbox
      - Converts bool-like values and emits on check-state changes.
    * - ``ParamIoWidgetComboBox``
      - Combo box
      - Handles choices list updates and emits on index changes.
    * - ``ParamIoWidgetLineEdit``
      - Line edit
      - Free text, optional float rounding for displayed values.
    * - ``ParamIoWidgetWithButton``
      - Line edit plus button
      - Base class for action-backed value selection widgets.
    * - ``ParamIoWidgetFile``
      - File picker button
      - Integrates dialogs and drag-and-drop path selection.
    * - ``ParamIoWidgetHdf5Key``
      - File plus dataset picker
      - Selects HDF5 datasets and stores key string values.


File and HDF5 Specialized Flow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``ParamIoWidgetWithButton`` is the base for chooser widgets.

- ``ParamIoWidgetFile``: button opens a path dialog and writes selected path.
- ``ParamIoWidgetHdf5Key``: button opens file selection, then dataset chooser,
  then writes selected dataset key.

Both subclasses rely on the same output contract: writing value through the
common I/O path so ``sig_new_value`` and ``sig_value_changed`` stay consistent.

Contributor Extension Checklist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When adding a new ``param_io_widget_*`` class:

1. Inherit from ``BaseParamIoWidgetMixIn`` and a QWidget-compatible class.
2. Implement ``current_text`` and ``update_display_value``.
3. Ensure ``update_display_value`` does not emit user-change signals.
4. Connect the widget's native interaction signal to ``emit_signal``.
5. If choices are supported, implement ``update_choices``.
6. If action button is needed, derive from ``ParamIoWidgetWithButton`` and
   implement ``button_function``.
7. Add tests in ``tests/widgets/parameter_config`` for conversion, display
   update semantics, and signal counts.
