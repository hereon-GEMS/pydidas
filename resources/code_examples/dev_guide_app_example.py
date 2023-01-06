import time
import argparse
import multiprocessing as mp

import numpy as np

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
    attributes_not_to_copy_to_slave_app = [
        "shared_array",
        "shared_index_in_use",
        "_tasks",
    ]
    parse_func = app_param_parser

    def __init__(self, *args, **kwargs):
        pydidas.core.BaseApp.__init__(self, *args, **kwargs)
        self._config["buffer_n"] = 20
        self._config["shared_memory"] = {}
        self._config["carryon_counter"] = 0
        self.shared_array = None
        self.shared_index_in_use = None
        self.results = None

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self._tasks = np.arange(self.get_param_value("num_images"))
        # only the master must initialize the shared memory, the slaves are passed
        # the reference:
        if not self.slave_mode:
            self.initialize_shared_memory()
        # create the shared arrays:
        self.shared_index_in_use = np.frombuffer(
            self._config["shared_memory"]["flag"].get_obj(), dtype=np.int32
        )
        self.shared_array = np.frombuffer(
            self._config["shared_memory"]["data"].get_obj(), dtype=np.float32
        ).reshape((self._config["buffer_n"],) + self.get_param_value("image_shape"))
        self.results = np.zeros(
            (self._tasks.size,) + self.get_param_value("image_shape")
        )

    def initialize_shared_memory(self):
        _n = self._config["buffer_n"]
        _num = int(
            self._config["buffer_n"] * np.prod(self.get_param_value("image_shape"))
        )
        self._config["shared_memory"]["flag"] = mp.Array("I", _n, lock=mp.Lock())
        self._config["shared_memory"]["data"] = mp.Array("f", _num, lock=mp.Lock())

    def multiprocessing_get_tasks(self):
        return self._tasks

    def multiprocessing_pre_cycle(self, index):
        """
        Sleep for 50 ms for every 5th task.
        """
        print("\nProcessing task ", index)
        if index % 5 == 0:
            print("Index divisible by 5, sleeping ...")
            time.sleep(0.05)
        return

    def multiprocessing_carryon(self):
        """
        Count up and carry on only for every second call.
        """
        self._config["carryon_counter"] += 1
        _carryon = self._config["carryon_counter"] % 2 == 0
        print("Carry on check: ", _carryon)
        return _carryon

    def multiprocessing_func(self, index):
        """
        Create a random image and store it in the buffer.
        """
        _shape = self.get_param_value("image_shape")
        # now, acquire the lock for the shared array and find the first empty
        # buffer position and write the image to it:
        _index_lock = self._config["shared_memory"]["flag"]
        while True:
            _index_lock.acquire()
            _zeros = np.where(self.shared_index_in_use == 0)[0]
            if _zeros.size > 0:
                _buffer_pos = _zeros[0]
                self.shared_index_in_use[_buffer_pos] = 1
                break
            _index_lock.release()
            time.sleep(0.01)
        self.shared_array[_buffer_pos] = np.random.random(_shape).astype(np.float32)
        _index_lock.release()
        return _buffer_pos

    def multiprocessing_store_results(self, task_index, buffer_index):
        _index_lock = self._config["shared_memory"]["flag"]
        _index_lock.acquire()
        self.results[task_index] = self.shared_array[buffer_index]
        self.shared_index_in_use[buffer_index] = 0
        _index_lock.release()


app = RandomImageGeneratorApp()
app.multiprocessing_pre_run()

app_slave = app.get_copy(slave_mode=True)
app_slave.multiprocessing_pre_run()

index = 10
buffer_index = app_slave.multiprocessing_func(index)
app.shared_index_in_use
app.shared_array[buffer_index, 0, 0:5]
app_slave.shared_array[buffer_index, 0, 0:5]

app.multiprocessing_store_results(index, buffer_index)
app.results[index, 0, 0:5]
