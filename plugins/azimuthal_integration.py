from base_plugins import ProcPlugin, PROC_PLUGIN
from plugin_workflow_gui.parameter import Parameter

class AzimuthalIntegration(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_name = 'Azimuthal integration'
    params = [Parameter('beam_cente_x', param_type=float, default=-1, desc='The beam-center x coordinate.'),
              Parameter('beam_cente_y', param_type=float, default=-1, desc='The beam-center y coordinate.'),
              Parameter('bins', param_type=int, default=100, desc='The number of bins'),
              Parameter('theta_min', param_type=float, default=0, desc='The lower theta limit'),
              Parameter('theta_max', param_type=float, default=10, desc='The upper theta limit')
              ]

    def __init__(self):
        pass


    def execute(self, *data, **kwargs):
        import numpy as np
        print(f'Execute plugin {self.name} with arguments: {data}, {kwargs}')
        return np.array(np.sum(data)), kwargs