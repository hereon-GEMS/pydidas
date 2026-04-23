..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2026, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _dev_guide_param_config_widgets_introduction:

Developers guide for Parameter config widget
============================================

.. note::

    This documentation page has been partially created using the AI-tool
    GPT-5.3-Codex.

.. contents::
    :depth: 1
    :local:

This page is the quick reference for the public API.

Public Module Interface
-----------------------

The package ``pydidas.widgets.parameter_config`` exports the following main
public entry classes:

- :py:class:`ParameterWidget <pydidas.widgets.parameter_config.ParameterWidget>`:
  The standard widget to display and edit a single :py:class:`Parameter
  <pydidas.core.Parameter>` in the GUI.
- :py:class:`ParameterWidgetsMixIn <pydidas.widgets.parameter_config.ParameterWidgetsMixIn>`:
  A mix-in to add ParameterWidget management to any QWidget subclass.
- :py:class:`ParameterEditCanvas <pydidas.widgets.parameter_config.ParameterEditCanvas>`:
  An empty widget with access to the :py:class:`ParameterWidgetsMixIn
  <pydidas.widgets.parameter_config.ParameterWidgetsMixIn>` functionality for
  dynamic ParameterWidget creation and layout.

``ParameterWidget`` is the user-facing composite widget for one
:py:class:`Parameter <pydidas.core.Parameter>`.

All ``QWidgets`` used in the ``pydidas`` user interface which require
manipulations of :py:class:`Parameters <pydidas.core.Parameter>` should inherit
from the :py:class:`ParameterWidgetsMixIn
<pydidas.widgets.parameter_config.ParameterWidgetsMixIn>` class and use its
:ref:`public API <dev_guide_parameter_widgets_mixin_api>`.

.. _dev_guide_parameter_widgets_mixin_api:

ParameterWidgetsMixIn public API
---------------------------------

:py:class:`ParameterWidgetsMixIn
<pydidas.widgets.parameter_config.ParameterWidgetsMixIn>` is a mixin class that
can be added to any ``QWidget`` subclass to provide managed creation, access,
and synchronization of :py:class:`ParameterWidget
<pydidas.widgets.parameter_config.ParameterWidget>` instances.

.. note::

    ``ParameterWidgetsMixIn`` assumes the host class has a ``params``
    (:py:class:`ParameterCollection <pydidas.core.ParameterCollection>`) and is
    a (subclass of) ``QWidget`` with a layout manager that supports adding
    widgets (e.g. ``QGridLayout``). :py:class:`ParameterEditCanvas
    <pydidas.widgets.parameter_config.ParameterEditCanvas>` provides a
    ready-to-use base class combining both.

Methods
^^^^^^^

All user interaction

.. list-table::
    :widths: 30 70
    :header-rows: 1
    :class: tight-table

    * - Method
      - Description
    * - ``create_param_widget(param, **kwargs)``
      - Create a ``ParameterWidget`` for a ``Parameter`` instance or refkey
        string and add it to the layout. Registers the widget in both
        ``param_widgets`` and ``param_composite_widgets`` under the Parameter's
        ``refkey``. Supported kwargs are detailed below.
    * - ``toggle_param_widget_visibility(refkey, visible)``
      - Show or hide the ``ParameterWidget`` registered under ``refkey``.
    * - ``update_param_widget_value(refkey, value)``
      - Update the display of the widget registered under ``refkey`` without
        changing the underlying ``Parameter`` value and without emitting
        signals.
    * - ``set_param_and_widget_value(refkey, value, emit_signal=True)``
      - Atomically update both the ``Parameter`` value and the widget display.
        Emits ``sig_new_value`` and ``sig_value_changed`` only if the value
        actually changed and ``emit_signal`` is ``True``.
    * - ``set_param_and_widget_value_and_choices(key, value, choices, emit_signal=True)``
      - Update the ``Parameter`` value and its choices, then synchronize the
        widget (rebuilding the I/O widget if the widget type needs to change).
        ``choices`` can be ``None`` to remove all choices. Emits signals only if
        the value changed and ``emit_signal`` is ``True``.


Attributes
^^^^^^^^^^

For accessing the widgets, the following attributes are available:

.. list-table::
    :widths: 20 80
    :header-rows: 1
    :class: tight-table

    * - Attribute
      - Description
    * - ``param_widgets``
      - Dictionary mapping Parameter ``refkey`` to the raw I/O widget instance.
    * - ``param_composite_widgets``
      - Dictionary mapping Parameter ``refkey`` to the full ``ParameterWidget``
        instance.

These dictionaries are populated when widgets are created through the
:py:meth:`create_param_widget
<pydidas.widgets.parameter_config.ParameterWidgetsMixIn.create_param_widget>`
method.

ParameterWidget public API
--------------------------

All user-interaction with the :py:class:`ParameterWidget
<pydidas.widgets.parameter_config.ParameterWidget>` should happen through the
following API contract. For internal behavior and signal/data flow, see
:ref:`dev_guide_parameter_widget`.

Signals
^^^^^^^

The following signals are emitted by the ``ParameterWidget`` simultaneously
to support both direct access to the new value and a generic change
notification:

- ``sig_new_value(str)``: emitted with string representation of new input.
- ``sig_value_changed()``: emitted when a value was changed.

Properties
^^^^^^^^^^

.. list-table::
    :widths: 20 80
    :header-rows: 1
    :class: tight-table

    * - Property
      - Description
    * - ``io_widget``
      - [read-only] The currently selected I/O widget instance for the linked
        Parameter.
    * - ``display_value``
      - [read-only] Current displayed value from the underlying I/O widget.
    * - ``value``
      - The linked display (and Parameter) value in its native datatype. This
        property is read/write and will trigger updates to the display and emit
        change signals when set.

Methods
^^^^^^^

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

Example Usage
-------------

This short example creates a Parameter and an associated ParameterWidget, then
performs different operations to demonstrate the API. Note that all other
necessary imports and application setup are assumed to be in place.

.. code-block:: python

    >>> from pydidas.core import Parameter
    >>> from pydidas.widgets.parameter_config import ParameterWidget, ParameterEditCanvas
    >>> param = Parameter("param1", int, 42)
    >>> canvas = ParameterEditCanvas()
    >>> canvas.params.add_param(param)
    >>> canvas.create_param_widget("param1")
    >>> widget = canvas.param_composite_widgets["param1"]
    >>> widget.value
    42

    # setting the widget value also updates the associated Parameter and emits signals
    >>> widget.set_value(100)
    >>> widget.value
    100
    >>> param.value
    100

    # Updating the display value only changes the widget display without
    # affecting the Parameter or emitting signals:
    >>> widget.update_display_value(200)
    >>> widget.value
    200
    >>> param.value
    100

    # The associated I/O widget can be accessed directly through the `io_widget` property:
    >>> widget.io_widget
    <pydidas.widgets.parameter_config.param_io_widget_lineedit.ParamIoWidgetLineEdit(0x22b5c91c530) at 0x0000022B61E46F00>

   # Now, we set a new value and choices for the Parameter, then update both the Parameter and the widget:
    >>> param.choices is None
    True
    >>> param.set_value_and_choices(300, choices=[100, 200, 300, 400])
    >>> param.value
    300
    >>> param.choices
    [100, 200, 300, 400]
    # Now programmatically update the widget to reflect the new choices
    # (this will rebuild the I/O widget to a combo box):
    >>> widget.update_choices_from_param()
    >>> widget.io_widget
    <pydidas.widgets.parameter_config.param_io_widget_combobox.ParamIoWidgetComboBox(0x22b54983850) at 0x0000022B6850F100>
    >>> widget.value
    300
    # Updating the widget value through the new combo box also updates the Parameter and emits signals:
    >>> widget.value = 200
    >>> widget.value
    200
    >>> param.value
    200

Further reading
---------------

.. toctree::
    :maxdepth: 2

    param_widget.rst
    param_widgets_mixin.rst
