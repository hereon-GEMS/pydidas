INPUT_PLUGIN = 0
PROC_PLUGIN = 1
OUTPUT_PLUGIN = 2

class BasePlugin:
    ptype = 'Base plugin'
    basic_plugin = True
    plugin_type = -1

    def __init__(self):
        pass

    def execute(self):
        """
        Execute the processing step."""
        raise NotImplementedError('Execute method has not been implemented.')


class InputPlugin(BasePlugin):
    ptype = 'Base plugin'
    basic_plugin = True
    plugin_type = 0

    def __init__(self):
        pass


class ProcPlugin(BasePlugin):
    ptype = 'Base plugin'
    basic_plugin = True
    plugin_type = 1

    def __init__(self):
        pass


class OutputPlugin(BasePlugin):
    ptype = 'Base plugin'
    basic_plugin = True
    plugin_type = 2

    def __init__(self):
        pass



class NoPlugin:
    basic_plugin = False