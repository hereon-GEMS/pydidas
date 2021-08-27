from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.core import Parameter, ParameterCollection

import numpy as np

class DummyLoader(InputPlugin):
    plugin_name = 'Dummy loader Plugin'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    input_data = []
    output_data = {0: {'name': 'image', 'dim': 2, 'labels': ['det_y', 'det_x']}}
    default_params = ParameterCollection(
        Parameter('The image height', int, default=10, refkey='image_height',
                  tooltip='The height of the image.'),
        Parameter('The image width', int, default=10, refkey='image_width',
                  tooltip='The width of the image.'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, index, **kwargs):
        _width = self.get_param_value('image_width')
        _height =self.get_param_value('image_height')
        _data = np.random.random((_width, _height))
        kwargs.update(dict(index=index))
        return _data, kwargs
