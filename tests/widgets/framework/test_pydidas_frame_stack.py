# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import random
import string

import numpy as np
import pytest
from qtpy import QtWidgets

from pydidas.widgets.framework import BaseFrame, PydidasFrameStack


class _TestWidget(BaseFrame):
    ref_name = ""
    title = ""
    menu_icon = None
    menu_entry = "Test/Entry"
    menu_title = "Test"

    def __init__(self, **kwargs):
        BaseFrame.__init__(self, **kwargs)
        self.hash = hash(self)
        self.menu_entry = "".join(
            random.choice(string.ascii_letters) for i in range(20)
        )

    def frame_activated(self, index): ...


@pytest.fixture
def frames():
    """Create a list of test frames for cleanup."""
    frame_list = []
    yield frame_list
    # Cleanup
    while frame_list:
        w = frame_list.pop()
        try:
            w.deleteLater()
        except RuntimeError:
            pass


@pytest.fixture
def stack_with_frames(frames):
    """Create a PydidasFrameStack with 4 registered frames."""
    stack = PydidasFrameStack()
    for i in range(4):
        w = _TestWidget()
        stack.register_frame(w)
        frames.append(w)
    return stack, frames


def test_init() -> None:
    """Test PydidasFrameStack initialization."""
    obj = PydidasFrameStack()
    assert isinstance(obj, QtWidgets.QStackedWidget)
    assert hasattr(obj, "frame_indices")
    assert hasattr(obj, "current_frames")
    assert hasattr(obj, "frame_names")


def test_register_frame(frames) -> None:
    """Test registering a single frame."""
    stack = PydidasFrameStack()
    w = _TestWidget()
    stack.register_frame(w)
    frames.append(w)
    assert stack.widget(0) == w


def test_register_frame_duplicate(frames) -> None:
    """Test registering a duplicate frame raises KeyError."""
    stack = PydidasFrameStack()
    w = _TestWidget()
    stack.register_frame(w)
    frames.append(w)
    with pytest.raises(KeyError):
        stack.register_frame(w)


def test_get_widget_by_name__known_name(stack_with_frames) -> None:
    """Test retrieving a widget by registered name."""
    stack, frames = stack_with_frames
    _w = stack.get_widget_by_name(stack.widget(0).menu_entry)
    assert _w == frames[0]


def test_get_widget_by_name__not_registered(stack_with_frames) -> None:
    """Test retrieving unregistered widget by name raises KeyError."""
    stack, _ = stack_with_frames
    with pytest.raises(KeyError):
        stack.get_widget_by_name("no such widget")


def test_get_all_widget_names(stack_with_frames) -> None:
    """Test retrieving all registered widget names."""
    stack, frames = stack_with_frames
    _names = stack.frame_names
    assert len(frames) == len(_names)
    for w in frames:
        assert w.menu_entry in _names


def test_activate_widget_by_name(stack_with_frames) -> None:
    """Test activating a widget by name."""
    stack, frames = stack_with_frames
    stack.activate_widget_by_name(frames[-1].menu_entry)
    assert stack.currentIndex() == len(frames) - 1


def test_activate_widget_by_name_wrong_name(stack_with_frames) -> None:
    """Test activating widget with wrong name raises KeyError."""
    stack, _ = stack_with_frames
    with pytest.raises(KeyError):
        stack.activate_widget_by_name("no such name")


def test_remove_widget_by_name(stack_with_frames) -> None:
    """Test removing a widget by name."""
    stack, frames = stack_with_frames
    stack.remove_widget_by_name(frames[-1].menu_entry)


def test_remove_widget_by_name_wrong_name(stack_with_frames) -> None:
    """Test removing widget with wrong name raises KeyError."""
    stack, _ = stack_with_frames
    with pytest.raises(KeyError):
        stack.remove_widget_by_name("no such name")


def test_removeWidget_widget_not_registered(stack_with_frames, frames) -> None:
    """Test removing unregistered widget raises KeyError."""
    stack, _ = stack_with_frames
    w = _TestWidget()
    frames.append(w)
    with pytest.raises(KeyError):
        stack.removeWidget(w)


def test_removeWidget(stack_with_frames) -> None:
    """Test removing a registered widget."""
    stack, frames = stack_with_frames
    w = frames[1]
    stack.removeWidget(w)
    _indices = set(stack.frame_indices.values())
    assert w.menu_entry not in stack.frame_indices
    assert w not in stack.current_frames
    assert _indices == set(np.arange(stack.count()))


def test_addWidget(stack_with_frames, frames) -> None:
    """Test addWidget raises NotImplementedError."""
    stack, _ = stack_with_frames
    w = _TestWidget()
    frames.append(w)
    with pytest.raises(NotImplementedError):
        stack.addWidget(w)


def test_reset(stack_with_frames) -> None:
    """Test resetting the stack."""
    stack, _ = stack_with_frames
    stack.reset()
    assert stack.count() == 0
    assert stack.current_frames == []
    assert stack.frame_indices == {}


def test_is_registered(stack_with_frames) -> None:
    """Test checking if widget is registered."""
    stack, frames = stack_with_frames
    assert stack.is_registered(frames[0])


def test_is_registered_wrong_widget(stack_with_frames, frames) -> None:
    """Test checking if unregistered widget returns False."""
    stack, _ = stack_with_frames
    w = _TestWidget()
    frames.append(w)
    assert not stack.is_registered(w)
