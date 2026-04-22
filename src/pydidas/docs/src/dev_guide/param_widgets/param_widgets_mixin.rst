..
    This file is licensed under the
    Creative Commons Attribution 4.0 International Public License (CC-BY-4.0)
    Copyright 2026, Helmholtz-Zentrum Hereon
    SPDX-License-Identifier: CC-BY-4.0

.. _dev_guide_parameter_config_api:

ParameterWidgetsMixin structure and API
=======================================

.. note::

    This documentation page has been partially created using the AI-tool GPT-5.3-Codex.

.. contents::
    :depth: 2
    :local:


ParameterWidgetsMixIn Public API
---------------------------------

:py:class:`ParameterWidgetsMixIn <pydidas.widgets.parameter_config.ParameterWidgetsMixIn>`
is a mixin class that can be added to any ``QWidget`` subclass to provide
managed creation, access, and synchronization of
:py:class:`ParameterWidget <pydidas.widgets.parameter_config.ParameterWidget>`
instances. It maintains two internal registries:

- ``param_widgets``: maps ``refkey`` -> the raw I/O widget (``BaseParamIoWidget``).
- ``param_composite_widgets``: maps ``refkey`` -> the full ``ParameterWidget``.

Both are populated automatically by ``create_param_widget``.

.. note::

    ``ParameterWidgetsMixIn`` assumes the host class has a ``params``
    (:py:class:`ParameterCollection <pydidas.core.ParameterCollection>`) and is a
    (subclass of) ``QWidget`` with a layout manager that supports adding widgets
    (e.g. ``QGridLayout``).
    :py:class:`ParameterEditCanvas <pydidas.widgets.parameter_config.ParameterEditCanvas>`
    provides a ready-to-use base class combining both.

Methods
^^^^^^^

.. list-table::
    :widths: 40 60
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
        ``choices`` can be ``None`` to remove all choices. Emits signals only
        if the value changed and ``emit_signal`` is ``True``.
