# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Class to run pydidas workflows with an event loop from the command line.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ExecuteWorkflowRunner"]


import argparse
from pathlib import Path

from qtpy import QtCore

from pydidas.apps.execute_workflow_app import ExecuteWorkflowApp
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import UserConfigError
from pydidas.multiprocessing import AppRunner
from pydidas.workflow import ProcessingTree, WorkflowResults, WorkflowTree
from pydidas_qtcore import PydidasQApplication


SCAN = ScanContext()
TREE = WorkflowTree()
RES = WorkflowResults()
EXP = DiffractionExperimentContext()


class ExecuteWorkflowRunner(QtCore.QObject):
    """
    Class to run pydidas workflows from the command line with parallelization.

    The WorkflowRunner can be run from the command line and creates and handles
    a Qt EventLoop for processing.

    Parameters are all handled as kwargs to allow argument parsing and arbitrary
    orders, but an output directory as well as all three of Workflow, Scan, and
    DiffractionExperiment must be supplied, either through parsed command line
    arguments or as keyword arguments.

    Keyword arguments will override given command line inputs.

    Parameters
    ----------
    **kwargs : dict
        Supported keyword arguments are:

        workflow : Union[Path, str, ProcessingTree]
            The filename to the workflow or a ProcessingTree instance.
        scan : Union[Path, str, Scan]
            The filename to the stored Scan or a Scan instance.
        diffraction_exp : Union[Path, str, DiffractionExperiment]
            The filename to the stored DiffractionExperiment or a
            DiffractionExperiment instance. Note that 'diffraction_experiment'
            is also available as alias.
        output_directory : Union[Path, str]
            The directory to write results to.
        verbose : bool, optional
            Flag to enable printed output message. Do not use this setting for
            remote processing. The default is False.
        overwrite : bool, optional
            Flag to enable writing of results to existing directories, possibly
            overwriting existing results. The default is False.
    """

    def __init__(self, **kwargs: dict):
        QtCore.QObject.__init__(self, None)
        self._qtapp = PydidasQApplication.instance()
        self.parse_args_for_pydidas_workflow()
        self.update_parsed_args_from_kwargs(**kwargs)

    def parse_args_for_pydidas_workflow(self):
        """
        Parse the command line arguments for the run_pydidas_workflow script.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose status updates in the console output.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help=("Enable overwriting of existing results."),
        )
        parser.add_argument(
            "-workflow", "-w", help="The filename with the Workflow to use."
        )
        parser.add_argument(
            "-scan", "-s", help="The filename with the Scan configuration to use."
        )
        parser.add_argument(
            "-diffraction_exp",
            "-d",
            help="The filename with the diffraction experiment configuration to use.",
        )
        parser.add_argument(
            "-output_dir",
            "-o",
            help="The output directory to store results in.",
        )
        _options, _unknown = parser.parse_known_args()
        self.parsed_args = dict(vars(_options))

    def update_parsed_args_from_kwargs(self, **kwargs: dict):
        """
        Update the parsed arguments with the given keyword arguments.

        For the specific supported keyword arguments, please check the class
        definition.

        Parameters
        ----------
        kwargs : dict
            The dictionary with the user-provided keyword-arguments

        Raises
        ------
        UserConfigError
            If both the 'diffraction_experiment' and 'diffraction_exp' keywords
            are provided.
        """
        if "workflow" in kwargs:
            self.parsed_args["workflow"] = kwargs["workflow"]
        if "scan" in kwargs:
            self.parsed_args["scan"] = kwargs["scan"]
        if "diffraction_experiment" in kwargs and "diffraction_exp" in kwargs:
            raise UserConfigError(
                "Both 'diffraction_exp' and 'diffraction_experiment' keywords "
                "were used in the run_pydidas_workflow script. Please supply one "
                "one of the keywords."
            )
        if "diffraction_experiment" in kwargs:
            kwargs["diffraction_exp"] = kwargs["diffraction_experiment"]
        if "diffraction_exp" in kwargs:
            self.parsed_args["diffraction_exp"] = kwargs["diffraction_exp"]
        if "output_dir" in kwargs:
            self.parsed_args["output_dir"] = kwargs["output_dir"]
        if "verbose" in kwargs:
            self.parsed_args["verbose"] = kwargs["verbose"]
        if "overwrite" in kwargs:
            self.parsed_args["overwrite"] = kwargs["overwrite"]

    @staticmethod
    @QtCore.Slot(float)
    def _print_progress(progress: float):
        """
        Print the current progress in the same line.

        Parameters
        ----------
        progress : float
            The current progress.
        """
        _n_chars = int(60 * progress)
        _txt = (
            "\u2588" * _n_chars
            + "-" * (60 - _n_chars)
            + "|"
            + f" {100 * progress:05.2f}% "
        )
        print(_txt, end="\r", flush=True)

    @QtCore.Slot(str)
    def _process_messages(self, message: str):
        """
        Process messages from the AppRunner and pass them to the app instance.

        Parameters
        ----------
        message : str
            The message to be processed.
        """
        self._app.received_signal_message(message)

    @QtCore.Slot()
    def _store_results_to_disk(self):
        """
        Store the WorkflowResults to disk.
        """
        RES.save_results_to_disk(
            self.parsed_args["output_dir"],
            "HDF5",
            overwrite=self.parsed_args["overwrite"],
        )
        self._qtapp.quit()

    def process_scan(self, **kwargs: dict):
        """
        Process a scan.

        This method will check if new metadata has been provided in the given
        keywords and will update the stored arguments respectively.

        Parameters
        ----------
        **kwargs : dict
            The updated keyword arguments. For the full list of supported keyword
            arguments, please refer to the global class docstring.
        """
        self.update_parsed_args_from_kwargs(**kwargs)
        self.check_all_args_okay()
        self.update_contexts_from_stored_args()
        self.execute_workflow_in_apprunner()

    def update_contexts_from_stored_args(self):
        """
        Update the global contexts from the stored arguments.
        """
        if isinstance(self.parsed_args["scan"], Scan):
            SCAN.update_from_scan(self.parsed_args["scan"])
        elif isinstance(self.parsed_args["scan"], (str, Path)):
            SCAN.import_from_file(self.parsed_args["scan"])

        if isinstance(self.parsed_args["diffraction_exp"], DiffractionExperiment):
            EXP.update_from_diffraction_exp(self.parsed_args["diffraction_exp"])
        elif isinstance(self.parsed_args["diffraction_exp"], (str, Path)):
            EXP.import_from_file(self.parsed_args["diffraction_exp"])

        if isinstance(self.parsed_args["workflow"], ProcessingTree):
            TREE.update_from_tree(self.parsed_args["workflow"])
        elif isinstance(self.parsed_args["workflow"], (str, Path)):
            TREE.import_from_file(self.parsed_args["workflow"])

    def check_all_args_okay(self):
        """
        Check that all required (keyword) arguments have been set.

        Raises
        ------
        UserConfigError
            If the configuration is incomplete or problematic.
        """
        _missing_keys = [
            f"{_name}: -{_key} {_val}"
            for _key, _name, _val in [
                ["scan", "Scan", "filename"],
                ["workflow", "WorkflowTree", "filename"],
                ["diffraction_exp", "DiffractionExperiment", "filename"],
                ["output_dir", "Output directory", "directory"],
            ]
            if self.parsed_args[_key] is None
        ]
        if len(_missing_keys) > 0:
            raise UserConfigError(
                "The following keys are required for processing but missing:\n - "
                + "\n - ".join(_missing_keys)
            )
        _output_dir = Path(self.parsed_args["output_dir"])
        if (
            _output_dir.is_dir()
            and len(list(_output_dir.iterdir())) > 0
            and not self.parsed_args["overwrite"]
        ):
            raise UserConfigError(
                "The specified output directory is not empty and overwriting of "
                "existing files has not been enabled. Please change the output "
                "directory or enable overwriting of existing files-"
            )

    def execute_workflow_in_apprunner(self):
        """
        Execute the given workflow in an AppRunner with a QEventLoop.
        """
        self._app = ExecuteWorkflowApp()

        try:
            runner = AppRunner(self._app)
            runner.sig_results.connect(self._app.multiprocessing_store_results)
            if self.parsed_args["verbose"]:
                runner.sig_progress.connect(self._print_progress)
            runner.sig_message_from_worker.connect(self._process_messages)
            runner.finished.connect(self._store_results_to_disk)
            runner.start()
            if self.parsed_args["verbose"]:
                print("Processing progress:")
            self._qtapp.exec_()
        except UserConfigError:
            runner.requestInterruption()
            if self.parsed_args["verbose"]:
                print("\nAborted workflow processing because of illegal configuration.")
            return
        if self.parsed_args["verbose"]:
            print("\nProcessing finished successfully.")
