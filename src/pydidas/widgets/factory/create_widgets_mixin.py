# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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

"""
Module with the CreateWidgetsMixIn class which can be inherited from to
add convenience widget creation methods to other classes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CreateWidgetsMixIn"]


from typing import Dict, List, Optional, Tuple

from qtpy import QtWidgets
from qtpy.QtWidgets import QWidget

from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory.empty_widget import EmptyWidget
from pydidas.widgets.factory.pydidas_checkbox import PydidasCheckBox
from pydidas.widgets.factory.pydidas_combobox import PydidasComboBox
from pydidas.widgets.factory.pydidas_label import PydidasLabel
from pydidas.widgets.factory.pydidas_lineedit import PydidasLineEdit
from pydidas.widgets.factory.pydidas_pushbutton import PydidasPushButton
from pydidas.widgets.factory.radio_button_group import RadioButtonGroup
from pydidas.widgets.utilities import get_widget_layout_args


class CreateWidgetsMixIn:
    """
    A mixin class to allow easy widget creation in their host classes.

    The CreateWidgetsMixIn class includes methods for easy adding of widgets
    to the layout. The create_something methods from the factories are called
    and in addition, the layout and positions can be set.

    Use the "gridPos" keyword to define the widget position in the parent's
    layout.
    """

    def __init__(self):
        self._widgets = {}
        self.__index_unreferenced = 0

    def create_spacer(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a QSpacerItem and set its properties.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs: dict
            Any attributes supported by QSpacerItem with a setAttribute method
            are valid kwargs. In addition, the gridPos key allows to specify
            the spacer's position in its parent's layout.
        """
        _parent = kwargs.get("parent_widget", self)
        if isinstance(_parent, str):
            _parent = self._widgets[_parent]

        _policy = kwargs.get("policy", QtWidgets.QSizePolicy.Minimum)
        _spacer = QtWidgets.QSpacerItem(
            kwargs.pop("fixedWidth", 20),
            kwargs.pop("fixedHeight", 20),
            _policy,
            kwargs.pop("vertical_policy", _policy),
        )
        apply_qt_properties(self, **kwargs)
        _layout_args = get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addItem(_spacer, *_layout_args)
        if ref is None:
            ref = f"unreferenced_{self.__index_unreferenced:03d}"
            self.__index_unreferenced += 1
        self._widgets[ref] = _spacer

    def create_label(self, ref: Optional[str], text: str, **kwargs: dict):
        """
        Create a PydidasLabel and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        text : str
            The label's displayed text.
        **kwargs : dict
            Any attributes supported by QLabel with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the label's position in its parent's layout.
            The 'fontsize_offset', 'bold', 'italic', 'underline' keywords can
            be used to control the font properties.
        """
        self.create_any_widget(ref, PydidasLabel, text, **kwargs)

    def create_line(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a line widget.

        This method creates a line widget (implemented as flat QFrame) as separator
        and adds it to the parent widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any additional keyword arguments. All QFrame attributes with setAttribute
            implementation are valid kwargs.
        """
        kwargs["frameShape"] = kwargs.get("frameShape", QtWidgets.QFrame.HLine)
        kwargs["frameShadow"] = kwargs.get("frameShadow", QtWidgets.QFrame.Sunken)
        kwargs["lineWidth"] = kwargs.get("lineWidth", 2)
        kwargs["fixedHeight"] = kwargs.get("fixedHeight", 3)
        self.create_any_widget(ref, QtWidgets.QFrame, **kwargs)

    def create_vertical_line(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a vertical line widget.

        This method creates a vertical line widget (implemented as flat QFrame) as
        separator and adds it to the parent widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any additional keyword arguments. All QFrame attributes with setAttribute
            implementation are valid kwargs.
        """
        kwargs["frameShape"] = kwargs.get("frameShape", QtWidgets.QFrame.HLine)
        kwargs["frameShadow"] = kwargs.get("frameShadow", QtWidgets.QFrame.Sunken)
        kwargs["lineWidth"] = kwargs.get("lineWidth", 2)
        kwargs["fixedWidth"] = kwargs.get("fixedWidth", 3)
        self.create_any_widget(ref, QtWidgets.QFrame, **kwargs)

    def create_lineedit(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a PydidasLineEdit and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any attributes supported by QLineEdit with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the LineEdit's position in its parent's layout.
            The 'fontsize_offset', 'bold', 'italic', 'underline' keywords can
            be used to control the font properties.
        """
        self.create_any_widget(ref, PydidasLineEdit, **kwargs)

    def create_button(self, ref: Optional[str], text: str, **kwargs: Dict):
        """
        Create a QPushButton and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any attributes supported by QPushButton with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the button's position in its parent's layout.
            The 'fontsize_offset', 'bold', 'italic', 'underline' keywords can
            be used to control the font properties.
            The button's clicked method can be connected directly, by specifing
            the slot through the 'clicked' kwarg.
        """
        self.create_any_widget(ref, PydidasPushButton, text, **kwargs)
        if "clicked" in kwargs and ref is not None:
            self._widgets[ref].clicked.connect(kwargs.get("clicked"))

    def create_spin_box(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a QSpinBox for integer values and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any attributes supported by QSpinBox with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the SpinBox's position in its parent's layout. The
            default range is set to (0, 1), if it is not overridden with the
            'range' keyword.
        """
        kwargs["range"] = kwargs.get("range", (0, 1))
        self.create_any_widget(ref, QtWidgets.QSpinBox, **kwargs)

    def create_double_spin_box(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a QDoubleSpinBox for floating point values and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any attributes supported by QSpinBox with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the SpinBox's position in its parent's layout. The
            default range is set to (0, 1), if it is not overridden with the
            'range' keyword.
        """
        kwargs["range"] = kwargs.get("range", (0, 1))
        self.create_any_widget(ref, QtWidgets.QDoubleSpinBox, **kwargs)

    def create_progress_bar(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a QProgressBar and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any attributes supported by QProgressBar with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the QProgressBar's position in its parent's layout.
        """
        self.create_any_widget(ref, QtWidgets.QProgressBar, **kwargs)

    def create_check_box(self, ref: Optional[str], text, **kwargs: Dict):
        """
        Create a PydidasCheckBox and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        text : str
            The CheckBox's descriptive text.
        **kwargs : dict
            Any attributes supported by QCheckBox with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the QProgressBar's position in its parent's layout.
            The 'fontsize_offset', 'bold', 'italic', 'underline' can be used
            to control the font properties or generic Qt properties.
        """
        self.create_any_widget(ref, PydidasCheckBox, text, **kwargs)

    def create_combo_box(self, ref: Optional[str], **kwargs: Dict):
        """
        Create a PydidasComboBox and store the widget.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any attributes supported by QComboBox with a setAttribute method
            are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the QComboBox's position in its parent's layout.
            The 'fontsize_offset', 'bold', 'italic', 'underline' can be used
            to control the font properties or generic Qt properties.
        """
        self.create_any_widget(ref, PydidasComboBox, **kwargs)

    def create_radio_button_group(
        self, ref: Optional[str], entries: List, **kwargs: Dict
    ):
        """
        Create a RadioButtonGroup widget and set its properties.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        text : str
            The CheckBox's descriptive text.
        **kwargs : dict
            Any attributes supported by the generic QWidget with a setAttribute
            method are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the RadioButtonGroup's position in its parent's layout.
            The 'fontsize_offset', 'bold', 'italic', 'underline' can be used
            to control the font properties or generic Qt properties.
            The 'entries' keyword takes a list of entries for the buttons and the
            number of rows and columns can be specified with the 'rows' and
            'columns' keywords, respectively.
        """
        self.create_any_widget(ref, RadioButtonGroup, entries, **kwargs)

    def create_empty_widget(self, ref: Optional[str], **kwargs: Dict):
        """
        Create an ampty QWidget with a agrid layout.

        Parameters
        ----------
        ref : str, optional
            The reference string for storing the widget. If None, the widget
            will automatically get a unique reference number.
        **kwargs : dict
            Any attributes supported by the generic QWidget with a setAttribute
            method are valid kwargs. In addition, the 'gridPos' keyword can be used
            to specify the QWidget's position in its parent's layout.
        """
        self.create_any_widget(ref, EmptyWidget, **kwargs)

    def create_any_widget(
        self, ref: Optional[str], widget_class: type, *args: Tuple, **kwargs: Dict
    ):
        """
        Create any widget with any settings and add it to the layout.

        Note
        ----
        Widgets must support generic args and kwargs arguments. This means
        that generic PyQt widgets cannot be created using this method. They
        can be added, however, using the ``add_any_widget`` method.

        Parameters
        ----------
        ref : Optional[str]
            The reference name in the _widgets dictionary.
        widget_class : type
            The class type of the widget.
        *args : args
            Any arguments for the widget creation.
        **kwargs : dict
            Keyword arguments for the widget creation.

        Raises
        ------
        TypeError
            If the reference "ref" is not of type string.
        """
        if hasattr(widget_class, "init_kwargs"):
            _init_kwargs = {}
            for _key in widget_class.init_kwargs:
                if _key in kwargs:
                    _init_kwargs[_key] = kwargs.pop(_key)
            _widget = widget_class(*args, **_init_kwargs)
        else:
            _widget = widget_class(*args)
        self.add_any_widget(ref, _widget, **kwargs)

    def add_any_widget(
        self, ref: Optional[str], widget_instance: QWidget, **kwargs: dict
    ):
        """
        Add any existing widget to the layout and apply settings to it.

        Parameters
        ----------
        ref : Optional[str]
            The widget reference key.
        widget_instance : QWidget
            The widget instance.
        **kwargs : dict
            Any attributes supported by the specific QWidget with a setAttribute
            method are valid kwargs. In addition, 'layout_kwargs' is a valid key
            to pass a dictionary with attributes for the widget's layout.
        """
        if not (isinstance(ref, str) or ref is None):
            raise TypeError("Widget reference must be None or a string.")
        _parent = kwargs.pop("parent_widget", self)
        _layout_kwargs = kwargs.pop("layout_kwargs", None)
        if isinstance(_parent, str):
            _parent = self if _parent == "::self::" else self._widgets[_parent]

        apply_qt_properties(widget_instance, **kwargs)
        if _layout_kwargs is not None:
            apply_qt_properties(widget_instance.layout(), **_layout_kwargs)
        if _parent is not None:
            _layout_args = get_widget_layout_args(_parent, **kwargs)
            _parent.layout().addWidget(widget_instance, *_layout_args)
        if ref is None:
            ref = f"unreferenced_{self.__index_unreferenced:03d}"
            self.__index_unreferenced += 1
        self._widgets[ref] = widget_instance
