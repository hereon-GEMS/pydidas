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
#
# This file was created using an AI tool and was modified by
# the pydidas team.

"""
Module with unittests for pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.widgets.base_classes import EmptyWidget
from pydidas_qtcore import PydidasQApplication


@pytest.fixture
def qtapp() -> PydidasQApplication:
    return PydidasQApplication.instance()


@pytest.mark.gui
def test_widget_reacts_to_font_signal_before_destruction(qtbot, qtapp):
    widget = EmptyWidget()
    qtbot.add_widget(widget)
    _orig_fontsize = qtapp.font_size
    try:
        qtapp.sig_new_fontsize.emit(_orig_fontsize + 5)
        qtbot.wait(10)
        assert widget.font().pointSizeF() == pytest.approx(_orig_fontsize + 5)
    finally:
        qtapp.sig_new_fontsize.emit(_orig_fontsize)
        qtbot.wait(10)


@pytest.mark.gui
def test_emitting_font_signals_after_widget_destruction_does_not_raise(qtbot, qtapp):
    widget = EmptyWidget()
    qtbot.add_widget(widget)
    widget.deleteLater()
    qtbot.wait(20)

    # These emissions must not raise, even though a (now-destroyed) widget
    # was previously connected to these signals. Without disconnecting the
    # widget's slots on destruction, this used to raise a RuntimeError
    # ("Internal C++ object already deleted") from within the Qt event
    # loop, which pytest-qt reports as a test failure.
    qtapp.sig_new_fontsize.emit(qtapp.font_size)
    qtapp.sig_new_font_family.emit(qtapp.font_family)
    qtapp.sig_new_font_metrics.emit(*qtapp.font_metrics)
    qtbot.wait(20)


@pytest.mark.gui
def test_many_widgets_destroyed_repeatedly_do_not_raise(qtbot, qtapp):
    # Regression test for repeated create/destroy cycles, to guard against
    # any leftover/stale connections accumulating over time.
    for _ in range(10):
        widget = EmptyWidget()
        qtbot.add_widget(widget)
        widget.deleteLater()
        qtbot.wait(5)
    qtapp.sig_new_fontsize.emit(qtapp.font_size)
    qtapp.sig_new_font_family.emit(qtapp.font_family)
    qtapp.sig_new_font_metrics.emit(*qtapp.font_metrics)
    qtbot.wait(20)


if __name__ == "__main__":
    pytest.main([__file__])
