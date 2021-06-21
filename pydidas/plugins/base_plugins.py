import abc
import copy

BASE_PLUGIN = -1
INPUT_PLUGIN = 0
PROC_PLUGIN = 1
OUTPUT_PLUGIN = 2

ptype = {BASE_PLUGIN: 'Base plugin',
         INPUT_PLUGIN: 'Input plugin',
         PROC_PLUGIN: 'Processing plugin',
         OUTPUT_PLUGIN: 'Output plugin'}

class BasePlugin:
    """
    The base plugin class from which all plugins inherit.

    Class attributes are:

    Class attributes
    ----------------
    basic_plugin : bool
        A keyword to mark basic plugin classes.
    plugin_type : int
        A key to discriminate between the different types of plugins
        (input, processing, output)
    parameters : list
        A list with the class parameters which are required to perform
        the execute operation.
    input_data : dict
        Dictionary with the required input data set descrptions
    output_data : dict
        Dictionary with a description of the output datasets.
    """
    basic_plugin = True
    plugin_type = BASE_PLUGIN
    plugin_name = 'Base plugin'
    parameters = []
    input_data = []
    output_data = []

    def __init__(self):
        """Setup the class."""
        #because lists are mutable, create a new list and copy the class
        #parameters items into it:
        self.params = []
        for param in self.parameters:
            self.params.append(copy.copy(param))
        if self.plugin_type not in [-1, 0, 1, 2]:
            raise ValueError('Unknown value for the plugin type')


    def execute(self, *data, **kwargs):
        """
        Execute the processing step.
        """
        raise NotImplementedError('Execute method has not been implemented.')

    def get_class_description(self, return_list=False):
        """
        Get a description of the plugin.

        This method can generate a description of the plugin with name,
        plugin type, class name and parameters and the docstring.
        The default return is a formatted string but a list of entries can
        be created with the return_list keyword.

        Parameters
        ----------
        return_list : bool, optional
            Keyword to toggle return . The default is False.

        Returns
        -------
        _desc : str or list
            The descripion of the plugin.
        """
        if self.__class__ == type:
            _name = self.__name__
        else:
            _name = self.__class__.__name__
        if return_list:
            _desc = [['Name', f'{self.plugin_name}\n']]
            _desc.append(['Class name', f'{_name}\n'])
            _desc.append(['Plugin type', f'{ptype[self.plugin_type]}\n'])
            _desc.append(['Plugin description', f'{self.__doc__}\n'])
            pstr = ''
            for param in self.params:
                pstr += f'\n{str(param)}'
            _desc.append(['Parameters', pstr[1:]])
        else:
            _desc = (f'Name: {self.plugin_name}\n'
                     f'Class name: {_name}\n'
                     f'Plugin type: {ptype[self.plugin_type]}\n\n'
                     f'Plugin description:\n{self.__doc__}\n\n'
                     'Parameters:')
            for param in self.params:
                _desc += f'\n{param}: {self.params[param]}'
        return _desc

    def set_param(self, param_name, value):
        """
        Set a parameter value.

        This method sets the parameter

        Parameters
        ----------
        param_name : TYPE
            DESCRIPTION.
        value : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        for param in self.params:
            if param.name == param_name:
                param.value = value

    def add_param(self, param):
        if param.name in [p.name for p in self.params]:
            raise KeyError(f'A parameter with the name {param.name} already'
                           ' exists.')
        self.params.append(param)

    def get_param_value(self, param_name):
        for param in self.params:
            if param.name == param_name:
                return param.value
        raise KeyError(f'A parameter with the name {param.name} does not'
                       ' exist.')

    def get_param_names(self):
        return [p.name for p in self.params]

    def restore_defaults(self, force=False):
        if not force:
            raise NotImplementedError('Confirmation of restoring plugin'
                                      ' defaults not yet implemented.')
        for param in self.params:
            param.restore_default()

    @staticmethod
    def check_if_plugin():
        return True

    @staticmethod
    def has_unique_param_config_widget():
        return False


    def param_config_widget(self):
        raise NotImplementedError('Generic plugins do not have a unique'
                                  ' parameter config widget.')


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """
    basic_plugin = True
    plugin_type = INPUT_PLUGIN


class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.
    """
    basic_plugin = True
    plugin_type = PROC_PLUGIN


class OutputPlugin(BasePlugin):
    """
    The base class for output (file saving / plotting) plugins.
    """
    basic_plugin = True
    plugin_type = OUTPUT_PLUGIN



class PluginMeta(metaclass=abc.ABCMeta):
    ...

PluginMeta.register(InputPlugin)
PluginMeta.register(OutputPlugin)
PluginMeta.register(ProcPlugin)
