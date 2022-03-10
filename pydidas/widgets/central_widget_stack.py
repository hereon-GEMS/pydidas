# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the CentralWidgetStack which is a QStackedWidget and is used as
the central widget in the pydidas GUI. All frames can be accessed through
the CentralWidgetStack once they have been registered.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CentralWidgetStack']

from qtpy import QtWidgets

from ..core import SingletonFactory


class _CentralWidgetStack(QtWidgets.QStackedWidget):
    """
    The _CentralWidgetStack is a QStackedWidget with references to all
    the possible top level widgets.
    Widgets are responsible for registering themself with this class to
    allow a later reference. For the pydidas main application, the main
    window takes care of registration.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.

    Attributes
    ----------
    widgets : list
        A list of all the registed widgets.
    widget_indices : dict
        A dictionary with (widget_name: index) entries to reference
        widgets with their names.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget_indices = {}
        self.widgets = []

    def register_widget(self, ref_name, widget):
        """
        Register a widget with the stacked widget.

        This method will register a widget and hold a reference to the widget
        index by the supplied name.

        Parameters
        ----------
        ref_name : str
            The identifier.
        widget : QWidget
            The widget to be registered.

        Raises
        ------
        KeyEror
            When a widget with the same name has already been registered
            to prevent duplicate entries in the index reference.
        """
        if ref_name in self.widget_indices:
            raise KeyError(f'A widget with the name "{ref_name}" has already '
                           'been registered with the CentralWidgetStack. '
                           'The new widget has not been registered.')
        index = super().addWidget(widget)
        widget.frame_index = index
        self.currentChanged.connect(widget.frame_activated)
        self.widgets.append(widget)
        self.widget_indices[ref_name] = index

    def get_name_from_index(self, index):
        """
        Get the widget reference name associated with the widget indexed at
        index.

        This method searches the dictionary of (name: index) entries and
        returns the name key for the index value.

        Parameters
        ----------
        index : int
            The widget index.

        Returns
        -------
        str
            The reference name.
        """
        key_list = list(self.widget_indices.keys())
        val_list = list(self.widget_indices.values())
        return key_list[val_list.index(index)]

    def get_widget_by_name(self, ref_name):
        """
        Get a widget from its reference name.

        This method will return the widget registered with the reference
        name, if it exists.

        Parameters
        ----------
        ref_name : str
            The reference name of the widget.

        Raises
        ------
        KeyError
            If no widget with the reference name has been registered.

        Returns
        -------
        widget : QtWidgets.QWidget
            The widget referenced by the name.
        """
        if ref_name not in self.widget_indices:
            raise KeyError(f'No widget with the name "{ref_name}" has been'
                           ' registered.')
        return self.widget(self.widget_indices[ref_name])

    def get_all_widget_names(self):
        """
        Get the names of all registered widgets.

        Returns
        -------
        list
            The list of all names of registered widgets.
        """
        return [w.ref_name for w in self.widgets]

    def activate_widget_by_name(self, ref_name):
        """
        Set the widget referenced by name to the active widget.

        Parameters
        ----------
        ref_name : str
            The reference name of the widget.

        Raises
        ------
        KeyError
            If no widget with the name has been registered.
        """
        if ref_name not in self.widget_indices:
            raise KeyError(f'No widget with the name "{ref_name}" has been'
                           ' registered with the CENTRAL_WIDGET_STACK.')
        index = self.widget_indices[ref_name]
        self.setCurrentIndex(index)

    def remove_widget_by_name(self, ref_name):
        """
        Remove a widget by its reference name.

        This method finds the widget associated with the reference name and
        deletes it from the QStackedWidget.
        Note: This does not delete the widget ifself, only the reference in
        the QStackedWidget.

        Parameters
        ----------
        ref_name : str
            The referene name of the widget

        Raises
        ------
        KeyError
            If the reference name has not been used for registering a widget.
        """
        if ref_name not in self.widget_indices:
            raise KeyError(f'No widget width the name "{ref_name}" has been '
                           'registered.')
        _widget = self.widgets[self.widget_indices[ref_name]]
        self.removeWidget(_widget)


    def addWidget(self, widget=None, name=None):
        """
        Overload the QStackedWidget.addWidget method to deactivate it.

        Widgets should be added through the register_widget method which
        also demands a reference name.

        Raises
        ------
        NotImplementedError
            Reference to the register_widget method is given.
        """
        raise NotImplementedError(
            'Please use the "register_widget(name, widget)" method.')

    def removeWidget(self, widget):
        """
        Remove a widget from the QStackdWidget.

        This overloaded method removed a widget from the QStackedWidget and
        also de-references it from the metadata.

        Parameters
        ----------
        widget : QWidget
            The widget to be remvoed from the QStackedWidget.

        Raises
        ------
        KeyError
            If the widget is not registed.
        """
        if widget not in self.widgets:
            raise KeyError(f'The widget "{widget}" is not registered.')
        widget.frame_index = None
        _index = self.widgets.index(widget)
        _ref_name = self.get_name_from_index(_index)
        self.widgets.remove(widget)
        self.currentChanged.disconnect(widget.frame_activated)
        for _key, _cur_index in self.widget_indices.items():
            if _cur_index > _index:
                self.widget_indices[_key] -= 1
                self.widget(_cur_index).frame_index -= 1
        del self.widget_indices[_ref_name]
        super().removeWidget(widget)

    def reset(self):
        """
        Reset the CentralWidgetStack and delete all widgets from itself.
        """
        while len(self.widgets) > 0:
            self.removeWidget(self.widgets[0])

    def is_registered(self, widget):
        """
        Check if a widget is already registered.

        This method checks if a widget is already registered and returns
        the bool result.

        Parameters
        ----------
        widget : QWidget
            The widget which might already be registered.

        Returns
        -------
        bool
            This will be True is the widget has been registered, and False
            if not.
        """
        return widget in self.widgets

    def change_reference_name(self, new_name, widget):
        """
        Change the reference name for a widget.

        This method changes the internal reference name for the widget and
        stored the supplied new_name.

        Parameters
        ----------
        new_name : str
            The new reference name.
        widget : QWidget
            The widget of which the refernce name shall be changed.

        Raises
        ------
        KeyError
            If the widget is not registered at all.
        """
        if not self.is_registered(widget):
            raise KeyError(f'The widget "{widget}" is not registered.')
        index = self.widgets.index(widget)
        name = self.get_name_from_index(index)
        if name != new_name:
            del self.widget_indices[name]
            self.widget_indices[new_name] = index
            self.widget(index).ref_name = new_name


CentralWidgetStack = SingletonFactory(_CentralWidgetStack)
