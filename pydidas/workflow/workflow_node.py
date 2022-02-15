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
Module with the WorkflowNode class which is a subclasses GenericNode
with additional support for plugins and a plugin chain.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowNode']

from copy import copy
from numbers import Integral

from ..plugins import BasePlugin
from ..core.utils import pydidas_logger, LOGGING_LEVEL
from .generic_node import GenericNode


logger = pydidas_logger()
logger.setLevel(LOGGING_LEVEL)


class WorkflowNode(GenericNode):
    """
    The WorkflowNode subclass of the GenericNode has an added plugin attribute
    to allow it to execute plugins, either individually or the full chain.
    """
    kwargs_for_copy_creation = ['plugin', '_result_shape']

    def __init__(self, **kwargs):
        kwargs = self.__preprocess_kwargs(**kwargs)
        super().__init__(**kwargs)
        self.__confirm_plugin_existance_and_type()
        self.__process_node_id()
        self.plugin.node_id = self._node_id
        self.results = None
        self.result_kws = None
        self._result_shape = None

    def __preprocess_kwargs(self, **kwargs):
        """
        Preprocess the keyword arguments and store and remove the node_id key
        from them.

        The node ID key must be set after the plugin has been stored to
        force syncing of Plugin node ID and WorkflowNode node ID.

        Parameters
        ----------
        **kwargs : dict
            The calling keyword arguments.

        Returns
        -------
        kwargs : dict
            The calling keyword arguments (minus the node_id key).
        """
        self.plugin = None
        self.__tmp_node_id = kwargs.get('node_id', None)
        if 'node_id' in kwargs:
            del kwargs['node_id']
        return kwargs

    def __confirm_plugin_existance_and_type(self):
        """
        Verify that a plugin exists and is of the correct type.

        Raises
        ------
        KeyError
            If no plugin has been selected.
        TypeError
            If the plugin is not an instance of BasePlugin.
        """
        if self.plugin is None:
            raise KeyError('No plugin has been supplied for the WorkflowNode.'
                           ' Node has not been created.')
        if not isinstance(self.plugin, BasePlugin):
            raise TypeError('Plugin must be an instance of BasePlugin (or '
                            'subclass).')

    def __process_node_id(self):
        """
        Process the node ID and set if for both the WorkflowNode and the
        Plugin.
        """
        if self.__tmp_node_id is not None:
            self.node_id = self.__tmp_node_id
        del self.__tmp_node_id

    @property
    def node_id(self):
        """
        Get the node_id.

        Note: This property needs to be reimplemented to allow a subclassed
        node_id.setter in the WorkflowNode.

        Returns
        -------
        node_id : Union[None, int]
            The node_id.
        """
        return self._node_id

    @node_id.setter
    def node_id(self, new_id):
        """
        Set the node_id.

        Parameters
        ----------
        new_id : Union[None, int]
            The new node ID.

        Raises
        ------
        TypeError
            If the type of the new ID is not int or None.
        """
        if new_id is None or isinstance(new_id, Integral):
            self._node_id = new_id
            self.plugin.node_id = new_id
            return
        raise TypeError('The new node_id is not of a correct type and has not'
                        ' been set.')

    def prepare_execution(self):
        """
        Prepare the execution of the plugin chain by calling the pre_execute
        methods of all plugins.
        """
        self.plugin.pre_execute()
        for _child in self._children:
            _child.prepare_execution()

    def execute_plugin(self, *args, **kwargs):
        """
        Execute the plugin associated with the node.

        Parameters
        ----------
        *args : tuple
            Any arguments which need to be passed to the plugin.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin.

        Returns
        -------
        results : tuple
            The result of the plugin.execute method.
        kws : dict
            Any keywords required for calling the next plugin.
        """
        return self.plugin.execute(*args, **kwargs)

    def execute_plugin_chain(self, arg, **kwargs):
        """
        Execute the full plugin chain recursively.

        This method will call the plugin.execute method and pass the results
        to the node's children and call their execute_plugin_chain methods.
        Note: No result callback is intended. It is assumed that plugin chains
        are responsible for saving their own data at the end of the processing.

        Parameters
        ----------
        *args : tuple
            Any arguments which need to be passed to the plugin.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin.
        """
        logger.debug(f'Starting plugin node #{self.node_id}')
        res, reskws = self.plugin.execute(copy(arg), **copy(kwargs))
        for _child in self._children:
            logger.debug('Passing result to child')
            _child.execute_plugin_chain(res, **reskws)
        logger.debug(f'Saving data node #{self.node_id}')
        if self.is_leaf and self.plugin.output_data_dim is not None:
            self.results = res
            self.result_kws = reskws

    def dump(self):
        """
        Dump the node to a saveable format.

        The dump includes information about the parent and children nodes but
        not the nodes itself. References to the nodeIDs are stored to allow
        reconstruction of the tree.
        Note: This dump is *not* recursive and will only save references to
        the child layer of the node.

        Returns
        -------
        dict
            The dict with all required information about the node.
        """
        _parent = (None if self.parent is None
                   else self.parent._node_id)
        _children = [child._node_id for child in self._children]
        _rep = dict(node_id=self.node_id,
                    parent=_parent,
                    children=_children,
                    plugin_class=self.plugin.__class__.__name__,
                    plugin_params=[p.export_refkey_and_value()
                                   for p in self.plugin.params.values()])
        return _rep

    def propagate_shapes_and_global_config(self):
        """
        Calculate the Plugin's shape of the results and push this to the node's
        children.
        """
        self.update_plugin_result_data_shape()
        self.propagate_to_children()

    def update_plugin_result_data_shape(self):
        """
        Update the result shape from the Plugin's input image shape and legacy
        operations.
        """
        self.plugin.update_legacy_image_ops_with_this_plugin()
        self.plugin.calculate_result_shape()
        self._result_shape = self.plugin.result_shape

    def propagate_to_children(self):
        """
        Propagate the global binning and ROI to the children.
        """
        for _child in self._children:
            _child_plugin = _child.plugin
            _child_plugin.input_shape = self.plugin.result_shape
            if not self.plugin.new_dataset:
                _child_plugin._legacy_image_ops = (
                    self.plugin._legacy_image_ops[:])
                _child_plugin._original_image_shape = (
                    self.plugin._original_image_shape)
            _child.propagate_shapes_and_global_config()

    @property
    def result_shape(self):
        """
        Get the result shape of the plugin, if it has been calculated yet.

        Returns
        -------
        Union[tuple, None]
            Returns the shape of the Plugin's results, if it has been
            calculated. Else, returns None.
        """
        return self._result_shape

    def __hash__(self):
        """
        Get the hash value for the WorkflowNode.

        The hash value is calculated by using the plugin, the number of
        children and the parent.

        Returns
        -------
        int
            The hash value.
        """
        _hashables = [len(self._children), self._parent, self._node_id,
                      self.plugin]
        _hashes = tuple(hash(_item) for _item in _hashables)
        return hash(_hashes)
