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
    """
    basic_plugin = True
    plugin_type = BASE_PLUGIN
    plugin_name = ''
    params = {}

    def __init__(self):
        pass

    def execute(self):
        """
        Execute the processing step."""
        raise NotImplementedError('Execute method has not been implemented.')

    def get_hint_text(self):
        try:
            _name = self.__name__
        except:
            _name = self.__class__.__name__
        rvals = []
        rvals = [['Name', f'{self.plugin_name}\n']]
        rvals.append(['Class name', f'{_name}\n'])
        rvals.append(['Plugin type', f'{ptype[self.plugin_type]}\n'])
        rvals.append(['Plugin description', f'{self.__doc__}\n'])
        pstr = ''
        for param in self.params:
            pstr += f'\n{param}: {self.params[param]}'
        rvals.append(['Parameters', pstr[1:]])
        # rstr = (f'Name: {self.plugin_name}\n'
        #         f'Class name: {_name}\n'
        #         f'Plugin type: {ptype[self.plugin_type]}\n\n'
        #         f'Plugin description:\n{self.__doc__}\n\n'
        #         'Parameters:')
        # for param in self.params:
        #     rstr += f'\n{param}: {self.params[param]}'
        return rvals


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """
    basic_plugin = True
    plugin_type = INPUT_PLUGIN

    def __init__(self):
        super().__init__()


class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.
    """
    basic_plugin = True
    plugin_type = PROC_PLUGIN

    def __init__(self):
        super().__init__()


class OutputPlugin(BasePlugin):
    """
    The base class for output (file saving / plotting) plugins.
    """
    basic_plugin = True
    plugin_type = OUTPUT_PLUGIN

    def __init__(self):
        super().__init__()


class NoPlugin:
    basic_plugin = False