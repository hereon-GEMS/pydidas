import argparse

import pydidas
from pydidas.core import Parameter, ParameterCollection


def app_param_parser(caller=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-num_images", "-n", help="The number of images")
    parser.add_argument("-image_shape", "-i", help="The image size")
    _args = dict(vars(parser.parse_args()))
    if _args["num_images"] is not None:
        _args["num_images"] = int(_args["num_images"])
    if _args["image_shape"] is not None:
        _args["image_shape"] = tuple(
            [int(entry) for entry in _args["image_shape"].strip("()").split(",")]
        )
    return _args


class RandomImageGeneratorApp(pydidas.core.BaseApp):
    default_params = ParameterCollection(
        Parameter("num_images", int, 50),
        Parameter("image_shape", tuple, (100, 100)),
    )
    parse_func = app_param_parser


app_1 = RandomImageGeneratorApp()
num_param = app_1.get_param("num_images")
app_2 = RandomImageGeneratorApp(num_param)

print(
    "Num images: ",
    app_1.get_param_value("num_images"),
    app_2.get_param_value("num_images"),
)

app_1.set_param_value("num_images", 30)
print(
    "Num images: ",
    app_1.get_param_value("num_images"),
    app_2.get_param_value("num_images"),
)


app = RandomImageGeneratorApp(num_images=20, image_shape=(20, 20))
app.get_param_value("num_images")
