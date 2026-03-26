# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for the ToggleOptionsButton widget."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import UserConfigError
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.selection import ToggleOptionsButton
from pydidas_qtcore import PydidasQApplication  # noqa: F401


@pytest.fixture
def widget(qtbot):
    """
    Fixture to create a ToggleOptionsButton instance.

    Parameters
    ----------
    qtbot
        PyQt test helper fixture.

    Returns
    -------
    ToggleOptionsButton
        Configured button instance with linked widget and signal spy.
    """
    _linked_widget = QtWidgets.QLineEdit("Dummy")
    button = ToggleOptionsButton(linked_widget=_linked_widget)
    button.spy_sig_visibility_changed = SignalSpy(button.sig_visibility_changed)
    qtbot.addWidget(button)
    _linked_widget.show()
    button.show()
    qtbot.wait_until(lambda: button.isVisible())
    return button


# ==============================================================================
# Initialization Tests
# ==============================================================================


@pytest.mark.gui
@pytest.mark.parametrize(
    "hidden_text, shown_text",
    [
        ("Show options", "Hide options"),
        ("Display settings", "Collapse settings"),
        ("More", "Less"),
    ],
)
@pytest.mark.parametrize("visible", [True, False])
def test_init_with_custom_toggle_texts(
    hidden_text: str, shown_text: str, visible: bool
) -> None:
    """Test initialization with custom toggle button texts."""
    _linked_widget = QtWidgets.QLineEdit("Dummy")
    button = ToggleOptionsButton(
        toggle_text_shown=shown_text,
        toggle_text_hidden=hidden_text,
        linked_widget=_linked_widget,
        linked_widget_visible=visible,
    )
    assert button.linked_widget is _linked_widget
    assert button.text() == (shown_text if visible else hidden_text)
    assert _linked_widget.isVisible() == visible


@pytest.mark.gui
def test_current_icon__getter(widget) -> None:
    """
    Test that current_icon changes based on visibility state.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    """
    icon = widget.current_icon
    assert isinstance(icon, QtGui.QIcon)
    assert not icon.isNull()


@pytest.mark.gui
@pytest.mark.parametrize("initial_value", [True, False])
def test_linked_widget_visible__getter(initial_value: bool) -> None:
    """
    Test the linked_widget_visible property getter.

    Parameters
    ----------
    initial_value : bool
        The initial visibility value.
    """
    button = ToggleOptionsButton(linked_widget_visible=initial_value)
    assert button.linked_widget_visible == initial_value


@pytest.mark.gui
@pytest.mark.parametrize("value", [True, False])
def test_linked_widget_visible__setter(qtbot, widget, value: bool) -> None:
    """
    Test setting the linked_widget_visible property.

    Parameters
    ----------
    qtbot
        PyQt test helper fixture.
    widget
        ToggleOptionsButton fixture instance.
    value : bool
        The value to set.
    """
    _n_expected = widget.spy_sig_visibility_changed.n + (
        widget.linked_widget_visible != value
    )
    widget.linked_widget_visible = value
    qtbot.wait_until(lambda: widget._linked_widget.isVisible() == value, timeout=0.5)
    assert widget.linked_widget_visible == value
    assert widget.spy_sig_visibility_changed.n == _n_expected


@pytest.mark.gui
def test_linked_widget_visible_setter__with_invalid_type(widget) -> None:
    """
    Test that setter raises error with invalid type.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    """
    with pytest.raises(UserConfigError):
        widget.linked_widget_visible = "not_a_bool"


@pytest.mark.gui
@pytest.mark.parametrize("value", [1, 1.0])
def test_linked_widget_visible_setter__with_numeric_type(qtbot, widget, value) -> None:
    """
    Test that setter accepts numeric types (coerced to bool).

    Parameters
    ----------
    qtbot
        PyQt test helper fixture.
    widget
        ToggleOptionsButton fixture instance.
    value
        Numeric value to test (1 or 1.0).
    """
    widget.linked_widget_visible = False
    qtbot.wait_until(lambda: not widget._linked_widget.isVisible(), timeout=0.5)
    widget.linked_widget_visible = value
    qtbot.wait_until(lambda: widget._linked_widget.isVisible() == value, timeout=0.5)
    assert widget._linked_widget.isVisible()


@pytest.mark.gui
def test_linked_widget_getter__none() -> None:
    """Test linked_widget getter when no widget is linked."""
    button = ToggleOptionsButton()
    assert button.linked_widget is None


@pytest.mark.gui
def test_linked_widget_getter_with_widget(widget) -> None:
    """
    Test linked_widget getter with a linked widget.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    """
    assert isinstance(widget.linked_widget, QtWidgets.QWidget)


@pytest.mark.gui
@pytest.mark.parametrize(
    "widget_type",
    [QtWidgets.QWidget, QtWidgets.QLabel, QtWidgets.QPushButton],
)
@pytest.mark.parametrize("visible", [True, False])
def test_linked_widget__setter__with_different_widget_types(
    widget, widget_type: type, visible: bool
) -> None:
    """
    Test setting linked_widget with different widget types.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    widget_type : type
        Widget type to test.
    visible : bool
        Visibility state to test.
    """
    _new_widget = widget_type()
    widget.linked_widget_visible = visible
    widget.linked_widget = _new_widget
    assert widget.linked_widget is _new_widget
    assert widget.linked_widget.isVisible() == visible


@pytest.mark.gui
def test_linked_widget__setter__with_none(widget) -> None:
    """
    Test setting linked_widget to None.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    """
    widget.linked_widget = None
    assert widget.linked_widget is None


@pytest.mark.gui
def test_linked_widget__setter__with_invalid_type(widget) -> None:
    """
    Test that setter raises error with invalid type.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    """
    with pytest.raises(UserConfigError):
        widget.linked_widget = "not_a_widget"


@pytest.mark.gui
def test_set_linked_widget_with_widget(widget) -> None:
    """
    Test set_linked_widget method with a QWidget.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    """
    _new_widget = QtWidgets.QWidget()
    widget.set_linked_widget(_new_widget)
    assert widget.linked_widget is _new_widget


@pytest.mark.gui
def test_set_linked_widget__with_none(widget) -> None:
    """
    Test set_linked_widget method with None.

    Parameters
    ----------
    widget
        ToggleOptionsButton fixture instance.
    """
    widget.set_linked_widget(None)
    assert widget.linked_widget is None


@pytest.mark.gui
@pytest.mark.parametrize("initial_state", [True, False])
def test_toggle_state_changes_visibility(qtbot, widget, initial_state: bool) -> None:
    """
    Test that toggle_state changes the visibility state.

    Parameters
    ----------
    qtbot
        PyQt test helper fixture.
    widget
        ToggleOptionsButton fixture instance.
    initial_state : bool
        Initial visibility state.
    """
    widget.linked_widget_visible = initial_state
    _initial_text = widget.text()
    _n0 = widget.spy_sig_visibility_changed.n
    widget.toggle_state()
    qtbot.wait_until(
        lambda: widget.linked_widget.isVisible() == (not initial_state),
        timeout=0.5,
    )
    assert widget.spy_sig_visibility_changed.n == _n0 + 1
    assert widget.linked_widget_visible == (not initial_state)
    assert widget.text() != _initial_text
    # test repeated call
    widget.toggle_state()
    qtbot.wait_until(
        lambda: widget.linked_widget.isVisible() == initial_state, timeout=0.5
    )
    assert widget.spy_sig_visibility_changed.n == _n0 + 2
    assert widget.linked_widget_visible == initial_state
    assert widget.text() == _initial_text


@pytest.mark.gui
@pytest.mark.parametrize("initial_state", [True, False])
def test_button_click(qtbot, widget, initial_state: bool) -> None:
    """
    Test that clicking button toggles visibility.

    Parameters
    ----------
    qtbot
        PyQt test helper fixture.
    widget
        ToggleOptionsButton fixture instance.
    initial_state : bool
        Initial visibility state.
    """
    widget.linked_widget_visible = initial_state
    _initial_text = widget.text()
    qtbot.mouseClick(widget, QtCore.Qt.LeftButton)
    assert widget.text() != _initial_text
    assert widget.linked_widget_visible == (not initial_state)
    assert widget.linked_widget.isVisible() == (not initial_state)


@pytest.mark.gui
def test_linked_widget_visibility_without_linked_widget() -> None:
    """Test that no error occurs when toggling without linked widget."""
    button = ToggleOptionsButton()
    button.linked_widget_visible = True
    button.linked_widget_visible = False
    assert button.linked_widget_visible is False


if __name__ == "__main__":
    pytest.main([__file__])
