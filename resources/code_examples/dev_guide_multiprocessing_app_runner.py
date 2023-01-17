import numpy as np
from qtpy import QtCore

import pydidas


class TestApp(pydidas.core.BaseApp):
    def __init__(self, *args, **kwargs):
        pydidas.core.BaseApp.__init__(self, *args, **kwargs)
        self._n = 20
        self.results = np.zeros((self._n))

    def multiprocessing_get_tasks(self):
        return np.arange(self._n)

    def multiprocessing_func(self, index):
        return 3 * index + 5

    @QtCore.Slot(int, object)
    def multiprocessing_store_results(self, index, *args):
        self.results[index] = args[0]


class TestObject(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.app = None
        self.results = []

    @QtCore.Slot(object)
    def store_app(self, app):
        self.app = app

    @QtCore.Slot(int, object)
    def store_results(self, index, *results):
        self.results.append([index, results[0]])


def run_app_runner():
    app = QtCore.QCoreApplication([])

    tester = TestObject()
    test_app = TestApp()
    app_runner = pydidas.multiprocessing.AppRunner(test_app)

    app_runner.sig_final_app_state.connect(tester.store_app)
    app_runner.sig_results.connect(tester.store_results)
    app_runner.sig_finished.connect(app.exit)

    timer = QtCore.QTimer()
    timer.singleShot(10, app_runner.start)
    app.exec_()

    print("Raw results as received from the signal:")
    print("Results: ", tester.results)
    print(
        "\nThe test app does not have any stored results because it was not connected:"
    )
    print("test_app.results: ", test_app.results)
    print("\nThe final app has all the results stored internally in the correct order:")
    print("final_app.results:", tester.app.results)


if __name__ == "__main__":
    run_app_runner()
