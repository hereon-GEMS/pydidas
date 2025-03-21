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
The pydidas_updater_script allows to automatically download the latest version of
pydidas from GitHub and replace the available version.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["run_update"]


import os
import shutil
import stat
import subprocess
import sys
import traceback
from pathlib import Path

import requests

from pydidas_scripts.remove_local_files import (
    remove_pydidas_log_files,
    remove_pydidas_stored_gui_states,
)


def get_latest_release_tag() -> str:
    """
    Get the latest release version of pydidas from GitHub.

    Returns
    -------
    str :
        The string for the latest release version.
    """
    _url = "https://api.github.com/repos/hereon-GEMS/pydidas/releases/latest"
    _response = requests.get(_url, timeout=5)
    _response.raise_for_status()
    _tag = _response.json()["tag_name"]
    if _tag.startswith("v"):
        return _tag[1:]
    return _tag


def get_local_version() -> str:
    """
    Get the locally installed pydidas version number.

    Returns
    -------
    str :
        The string for the remote version.
    """
    _versions = {}
    for _path in sys.path:
        _version_file = Path(_path).joinpath("pydidas", "version.py")
        if _version_file.is_file():
            with open(_version_file, "r") as _f:
                _lines = _f.readlines()
            for _line in _lines:
                if _line.startswith("__version__ ="):
                    _versions[_version_file] = _line.split('"')[1]
    if len(_versions) == 0:
        raise ModuleNotFoundError("No pydidas version found in python path.")
    if len(_versions) > 1:
        raise NameError(
            "Found multiple versions of pydidas in python's path. Cannot update "
            "pydidas automatically. Found versions in:\n"
            "\n- ".join([str(_fname) for _fname in _versions])
        )
    return list(_versions.values())[0]


def check_update_necessary_and_wanted(local_version: str, remote_version: str) -> bool:
    """
    Check if an update is necessary.

    Parameters
    ----------
    local_version : str
        The locally installed version number.
    remote_version : str
        The remote (GitHub) version number.

    Returns
    -------
    bool
        Flag whether the update is necessary and wanted by the user.
    """
    if local_version >= remote_version:
        print_status(
            f"The local version {local_version} is up to date"
            "\n=== with the remote repository.\n=== No update required.",
        )
        input("Press <Enter> to continue.")
        return False
    _reply = input(
        f"\nDo you want to update pydidas from version {local_version} to "
        f"{remote_version}? Yes / [No]: "
    )
    return _reply.upper() in ["Y", "YES"]


def print_status(status: str):
    """
    Print the status in a formatted "box".

    Parameters
    ----------
    status : str
        The status message to be printed.
    """
    print("\n")
    print("=" * 80 + "\n")
    print("=== " + status)
    print("\n" + "=" * 80 + "\n")


def download_wheel(version: str, path: Path) -> Path:
    """
    Download the wheel file from the GitHub repository.

    Parameters
    ----------
    version : str
        The version string of the remote pydidas version.
    path : Path
        The path to download the wheel file.

    Returns
    -------
    Path
        The full path to the downloaded wheel file.
    """
    _wheel_version = ".".join(str(int(_item)) for _item in version.split("."))
    _wheel_filename = f"pydidas-{_wheel_version}-py3-none-any.whl"
    _url = (
        f"https://github.com/hereon-GEMS/pydidas/releases/download/v{version}/"
        + _wheel_filename
    )
    _response = requests.get(_url, stream=True)
    _response.raise_for_status()
    with open(path.joinpath(_wheel_filename), "wb") as _file:
        for _chunk in _response.iter_content(chunk_size=8192):
            _file.write(_chunk)
    return path.joinpath(_wheel_filename)


def install_wheel(wheel_filepath: Path, verbose: bool = True):
    """
    Install the wheel with the given filename.

    Parameters
    ----------
    wheel_filepath: Path
        The name of the wheel file.
    verbose : bool, optional
        Flag whether to print the status messages. The default is True.
    """
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ]
    )
    if verbose:
        print_status("Installing wheel")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            str(wheel_filepath),
            "--no-warn-script-location",
        ]
    )


def remove_outdated_documentation():
    """
    Remove the outdated documentation files.
    """
    _path = get_location_of_installed_pydidas().joinpath("pydidas", "sphinx")
    if _path.is_dir():
        shutil.rmtree(_path)


def get_location_of_installed_pydidas() -> Path:
    """
    Get the path of the directory with the installed pydidas version.

    Returns
    -------
    Path
        pydidas's parent path.
    """
    _results = []
    for _root in sys.path:
        if Path(_root).joinpath("pydidas", "__init__.py").is_file():
            _results.append(_root)
    if len(_results) == 0:
        raise ModuleNotFoundError(
            "No installed version of pydidas has been found. Please check and update "
            "pydidas manually."
        )
    if len(_results) > 1:
        raise NameError(
            "Found more than one referenced pydidas versions. Please update pydidas "
            "manually in the correct location, remove the duplicate paths from "
            "sys.path or delete the duplicate packages."
        )
    return Path(_results[0])


def backup_local_version(path: Path, version: str, verbose: bool = True):
    """
    Move the old pydidas files to a backup location in case the update fails.

    Parameters
    ----------
    path : Path
        The installation path of the pydidas package.
    version : str
        The version string of the local version.
    verbose : bool, optional
        Flag whether to print the status messages. The default is True.
    """
    if verbose:
        print_status("Backing up old version")
    for _name in [
        "pydidas",
        "pydidas_plugins",
        "pydidas_scripts",
        f"pydidas-{_distributed_version_in_python(version)}.dist-info",
    ]:
        if path.joinpath(f"{_name}_pre_update").is_dir():
            shutil.rmtree(path.joinpath(f"{_name}_pre_update"))
        shutil.copytree(
            path.joinpath(_name),
            path.joinpath(f"{_name}_pre_update"),
        )


def _distributed_version_in_python(version: str) -> str:
    """
    Get the version in python nomenclature without leading zeros.

    Parameters
    ----------
    version : str
        The original version string.

    Returns
    -------
    str
        The version string with stripped leading zeros.
    """
    return ".".join([_item.removeprefix("0") for _item in version.split(".")])


def restore_pre_update_files(location: Path, version: str, remote_version: str):
    """
    Restore the files from the pre-update save to the working directory.

    Parameters
    ----------
    location : Path
        The location where pydidas is installed.
    version : str
        The locally installed version identifier.
    remote_version : str
        The remote version identifier.
    """
    for _name in [
        "pydidas",
        "pydidas_plugins",
        "pydidas_scripts",
        f"pydidas-{_distributed_version_in_python(version)}.dist-info",
    ]:
        if location.joinpath(f"{_name}_pre_update").is_dir():
            if location.joinpath(_name).is_dir():
                shutil.rmtree(location.joinpath(_name))
            shutil.move(
                location.joinpath(f"{_name}_pre_update"), location.joinpath(_name)
            )
    if location.joinpath(f"pydidas-{remote_version}.dist-info").is_dir():
        shutil.rmtree(location.joinpath(f"pydidas-{remote_version}.dist-info"))


def remove_temp_data(path: Path):
    """
    Remove all temporary update data at the given path.

    Parameters
    ----------
    path : Path
        The path of the update's temporary files.
    """
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            for _root, _dirs, _files in os.walk(path):
                for _name in _files:
                    _fname = os.path.join(_root, _name)
                    os.chmod(_fname, stat.S_IWUSR)
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=False)
    except PermissionError:
        pass


def remove_pydidas_backup(path: Path, version: str):
    """
    Remove the local pydidas backup after completing the update.

    Parameters
    ----------
    path : Path
        The site-packages path where pydidas is installed.
    version : str
        The locally installed version identifier.
    """
    for _name in [
        "pydidas",
        "pydidas_plugins",
        "pydidas_scripts",
        f"pydidas-{_distributed_version_in_python(version)}.dist-info",
    ]:
        if path.joinpath(f"{_name}_pre_update").is_dir():
            try:
                shutil.rmtree(path.joinpath(f"{_name}_pre_update"))
            except PermissionError:
                pass


def run_update():
    """
    Run the full updating pipeline.
    """
    _local_version = get_local_version()
    _remote_version = get_latest_release_tag()
    _should_update = check_update_necessary_and_wanted(_local_version, _remote_version)
    if not _should_update:
        return
    _success = False
    _path = Path(sys.executable).parent.joinpath(".temp", "pydidas")
    _pydidas_location = get_location_of_installed_pydidas()
    try:
        os.makedirs(_path)
        backup_local_version(_pydidas_location, _local_version)
        remove_outdated_documentation()
        _wheel = download_wheel(_remote_version, _path)
        install_wheel(_wheel)
        remove_pydidas_log_files(_local_version, verbose=False, confirm_finish=False)
        remove_pydidas_stored_gui_states(
            _local_version, verbose=False, confirm_finish=False
        )
        remove_outdated_documentation()
        _success = True
    except Exception:
        restore_pre_update_files(_pydidas_location, _local_version, _remote_version)
        print_status(
            "An error occurred during the update. Restoring previous version "
            f"{_local_version} of pydidas."
            "\nPlease note that any problems with the pip update process may "
            "have caused a broken environment."
        )
        print(traceback.format_exc())
    finally:
        print_status("Removing temporary data")
        remove_temp_data(_path)
        remove_pydidas_backup(_pydidas_location, _local_version)
        if _success:
            print_status(f"Finished pydidas update to version {_remote_version}")
        input("Press <Enter> to finish the updater script.\n")


if __name__ == "__main__":
    run_update()
