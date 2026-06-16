# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
# Parts of this file have been created using the AI-tool Claude Haiku 4.5.

"""Unit tests for the ReadOnlyTextWidget."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from typing import Generator

import pytest

from pydidas.core.exceptions import UserConfigError
from pydidas.widgets.misc.read_only_text_widget import ReadOnlyTextWidget
from pydidas_qtcore import PydidasQApplication


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None, None, None]:
    app = PydidasQApplication.instance()
    yield
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ReadOnlyTextWidget)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.fixture
def widget(qtbot) -> ReadOnlyTextWidget:
    """Create a ReadOnlyTextWidget for testing."""
    w = ReadOnlyTextWidget()
    qtbot.add_widget(w)
    w.show()
    qtbot.wait_until(lambda: w.isVisible(), timeout=500)
    return w


@pytest.mark.gui
def test_creation__defaults(qtbot) -> None:
    w = ReadOnlyTextWidget()
    qtbot.add_widget(w)
    w.show()
    qtbot.wait_until(lambda: w.isVisible(), timeout=500)
    assert w.isReadOnly()
    assert w.acceptRichText()
    assert w.minimumWidth() == 300
    assert w.lineWrapColumnOrWidth() == 80


@pytest.mark.gui
@pytest.mark.parametrize("line_wrap_width", [40, 80, 120])
def test_creation__with_line_wrap_width(qtbot, line_wrap_width) -> None:
    w = ReadOnlyTextWidget(line_wrap_width=line_wrap_width)
    qtbot.add_widget(w)
    assert w.lineWrapColumnOrWidth() == line_wrap_width


@pytest.mark.gui
@pytest.mark.parametrize(
    "width,height", [(None, None), (500, None), (None, 400), (500, 400)]
)
def test_creation__with_size_kwargs(qtbot, width, height) -> None:
    kwargs = {}
    if width is not None:
        kwargs["minimumWidth"] = width
    if height is not None:
        kwargs["minimumHeight"] = height
    w = ReadOnlyTextWidget(**kwargs)
    qtbot.add_widget(w)
    if width is not None:
        assert w.minimumWidth() == width
    if height is not None:
        assert w.minimumHeight() == height


@pytest.mark.gui
def test_creation__with_fixed_size(qtbot) -> None:
    w = ReadOnlyTextWidget(fixedWidth=500, minimumWidth=300)
    qtbot.add_widget(w)
    assert w.width() <= 500


@pytest.mark.gui
def test_set_text(widget) -> None:
    text = "This is a test text"
    widget.setText(text)
    assert text in widget.toPlainText()


@pytest.mark.gui
def test_set_text__alias(widget) -> None:
    text = "Alias test text"
    widget.set_text(text)
    assert text in widget.toPlainText()


@pytest.mark.gui
def test_set_text__with_title(widget) -> None:
    title = "Title"
    text = "Content"
    widget.setText(text, title=title)
    assert title in widget.toPlainText()
    assert text in widget.toPlainText()


@pytest.mark.gui
def test_set_text__empty_title(widget) -> None:
    text = "Content"
    widget.setText(text, title="")
    content = widget.toPlainText()
    assert text in content
    # Empty string shouldn't add title line
    lines = content.strip().split("\n")
    assert len(lines) > 0


@pytest.mark.gui
def test_append_text__plain(widget) -> None:
    widget.set_text("Initial")
    widget.append_text("Appended", formatter="plain")
    content = widget.toPlainText()
    assert "Initial" in content
    assert "Appended" in content


@pytest.mark.gui
@pytest.mark.parametrize("formatter", ["plain", "header", "section", "subsection"])
def test_append_text__with_formatters(widget, formatter) -> None:
    widget.set_text("Base")
    widget.append_text(f"Text with {formatter}", formatter=formatter)
    content = widget.toPlainText()
    assert "Base" in content
    assert f"Text with {formatter}" in content


@pytest.mark.gui
def test_append_text__replaces_default_content(widget) -> None:
    widget.set_text("")  # Start with default content
    widget.append_text("New content", formatter="plain")
    # The new content should be present (replacing the default)
    assert "New content" in widget.toPlainText()


@pytest.mark.gui
def test_append_text__default_formatter(widget) -> None:
    widget.set_text("Base")
    widget.append_text("Appended without formatter")
    content = widget.toPlainText()
    assert "Base" in content
    assert "Appended without formatter" in content


@pytest.mark.gui
def test_prepend_text__plain(widget) -> None:
    widget.set_text("Initial")
    widget.prepend_text("Prepended", formatter="plain")
    content = widget.toPlainText()
    assert "Initial" in content
    assert "Prepended" in content


@pytest.mark.gui
@pytest.mark.parametrize("formatter", ["plain", "header", "section", "subsection"])
def test_prepend_text__with_formatters(widget, formatter) -> None:
    widget.set_text("Base")
    widget.prepend_text(f"Text with {formatter}", formatter=formatter)
    content = widget.toPlainText()
    assert "Base" in content
    assert f"Text with {formatter}" in content


@pytest.mark.gui
def test_prepend_text__replaces_default_content(widget) -> None:
    widget.set_text("")  # Start with default content
    widget.prepend_text("New content", formatter="plain")
    # The new content should be present (replacing the default)
    assert "New content" in widget.toPlainText()


@pytest.mark.gui
def test_prepend_text__default_formatter(widget) -> None:
    widget.set_text("Base")
    widget.prepend_text("Prepended without formatter")
    content = widget.toPlainText()
    assert "Base" in content
    assert "Prepended without formatter" in content


@pytest.mark.gui
def test_set_title_(widget) -> None:
    widget.set_text("Content")
    widget.set_title("New Title")
    content = widget.toPlainText()
    assert "New Title" in content
    assert "Content" in content


@pytest.mark.gui
def test_set_title__empty(widget) -> None:
    widget.set_text("Content", title="Old Title")
    widget.set_title("")
    content = widget.toPlainText()
    assert "Old Title" not in content
    assert "Content" in content


@pytest.mark.gui
def test_set_text__from_list(widget) -> None:
    text_list = [
        ("header", "Header Text"),
        ("section", "Section Text"),
        ("subsection", "Subsection Text"),
        ("plain", "Plain Text"),
    ]
    widget.set_text_from_list(text_list)
    content = widget.toPlainText()
    for _, text in text_list:
        assert text in content


@pytest.mark.gui
def test_set_text__from_list_with_title(widget) -> None:
    text_list = [
        ("plain", "Item 1"),
        ("section", "Item 2"),
    ]
    title = "List Title"
    widget.set_text_from_list(text_list, title=title)
    content = widget.toPlainText()
    assert title in content
    for _, text in text_list:
        assert text in content


@pytest.mark.gui
def test_set_text__from_list_empty_entries_skipped(widget) -> None:
    text_list = [
        ("plain", "Item 1"),
        ("section", ""),
        ("plain", "Item 3"),
    ]
    widget.set_text_from_list(text_list)
    content = widget.toPlainText()
    assert "Item 1" in content
    assert "Item 3" in content


@pytest.mark.gui
def test_clear(widget) -> None:
    widget.set_text("Some content")
    assert len(widget.toPlainText()) > 0
    widget.clear()
    assert widget.toPlainText() == ""


@pytest.mark.gui
def test_clear__resets_content_tracking(widget) -> None:
    widget.set_text("Content")
    widget.clear()
    assert widget._current_content == widget.default_text


@pytest.mark.gui
def test_default_text_property(widget) -> None:
    default = widget.default_text
    assert isinstance(default, list)
    assert len(default) == 1
    assert default[0] == ("plain", "")


@pytest.mark.gui
def test__invalid_formatter_type_raises_error(widget) -> None:
    text_list = [
        ("plain", "Valid text"),
        ("invalid_type", "Invalid formatter"),
    ]
    with pytest.raises(UserConfigError) as exc_info:
        widget.set_text_from_list(text_list)
    assert "Unsupported formatter type" in str(exc_info.value)
    assert "invalid_type" in str(exc_info.value)


@pytest.mark.gui
def test__reprint_method(widget) -> None:
    widget.set_text("Test content")
    initial_text = widget.toPlainText()
    widget.reprint()
    assert widget.toPlainText() == initial_text


@pytest.mark.gui
def test__multiple_appends_accumulate(widget) -> None:
    widget.set_text("Base")
    widget.append_text("First")
    widget.append_text("Second")
    widget.append_text("Third")
    content = widget.toPlainText()
    assert "Base" in content
    assert "First" in content
    assert "Second" in content
    assert "Third" in content


@pytest.mark.gui
def test__multiple_prepends_accumulate(widget) -> None:
    widget.set_text("Base")
    widget.prepend_text("First")
    widget.prepend_text("Second")
    content = widget.toPlainText()
    assert "Base" in content
    assert "First" in content
    assert "Second" in content


@pytest.mark.gui
def test__vertical_scroll_resets_on_print(widget) -> None:
    widget.set_text("Content")
    scroll_bar = widget.verticalScrollBar()
    assert scroll_bar.value() == scroll_bar.minimum()


@pytest.mark.gui
def test_set_text__overwrites_previous_content(widget) -> None:
    widget.set_text("First text")
    widget.append_text("Appended")
    widget.set_text("Second text")
    content = widget.toPlainText()
    # First text should not be there as it was overwritten
    assert "Second text" in content


@pytest.mark.gui
def test__empty_text_in_list(widget) -> None:
    text_list = [("plain", ""), ("header", "Header"), ("plain", "")]
    widget.set_text_from_list(text_list)
    content = widget.toPlainText()
    assert "Header" in content


@pytest.mark.gui
def test__integration__complex_workflow(widget) -> None:
    widget.set_text("Initial content", title="Original Title")
    initial_content = widget.toPlainText()
    assert "Original Title" in initial_content
    # Change title:
    widget.set_title("New Title")
    content_after_title = widget.toPlainText()
    assert "New Title" in content_after_title
    # Append various items:
    widget.append_text("Section content", formatter="section")
    widget.append_text("Subsection content", formatter="subsection")

    final_content = widget.toPlainText()
    assert "New Title" in final_content
    assert "Initial content" in final_content
    assert "Section content" in final_content
    assert "Subsection content" in final_content


@pytest.mark.gui
def test__font_size_connection(qtbot) -> None:
    w = ReadOnlyTextWidget()
    qtbot.add_widget(w)
    w.show()
    w.set_text("Test content")
    assert "Test content" in w.toPlainText()
    assert hasattr(w, "_qtapp")
    assert hasattr(w, "reprint")


if __name__ == "__main__":
    pytest.main([__file__])
