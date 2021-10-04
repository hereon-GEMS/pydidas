from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.core import Parameter, ParameterCollection, get_generic_parameter

import numpy as np

class DummyLoader(InputPlugin):
    plugin_name = 'Dummy loader Plugin'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    input_data = []
    output_data = {0: {'name': 'image', 'dim': 2,
                       'labels': ['det_y', 'det_x']}}
    default_params = ParameterCollection(
        Parameter('image_height', int, 10, name='The image height',
                  tooltip='The height of the image.'),
        Parameter('image_width', int, 10, name='The image width',
                  tooltip='The width of the image.'),
        get_generic_parameter('filename'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preexecuted = False

    def execute(self, index, **kwargs):
        _width = self.get_param_value('image_width')
        _height =self.get_param_value('image_height')
        _data = np.random.random((_width, _height))
        kwargs.update(dict(index=index))
        return _data, kwargs

    def pre_execute(self):
        self._preexecuted = True
