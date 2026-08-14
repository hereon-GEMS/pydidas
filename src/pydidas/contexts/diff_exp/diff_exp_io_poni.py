# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
Module with the DiffractionExperimentIoPoni class which is used to import
DiffractionExperimentContext metadata from a pyFAI poni file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DiffractionExperimentIoPoni"]


from pathlib import Path
from typing import Any

from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_context import DiffractionExperimentContext
from pydidas.contexts.diff_exp.diff_exp_io_base import DiffractionExperimentIoBase
from pydidas.core.constants import LAMBDA_IN_M_TO_E
from pydidas.core.constants.file_extensions import PONI_EXTENSIONS
from pydidas.core.constants.pyfai_names import PYFAI_DETECTOR_NAMES
from pydidas.core.lazy_imports.pyFAI import Detector, Geometry, PoniFile
from pydidas.core.utils import verify_is_new_file_or_replace_set


class DiffractionExperimentIoPoni(DiffractionExperimentIoBase):
    """
    Base class for WorkflowTree exporters.
    """

    extensions = PONI_EXTENSIONS
    format_name = "PONI"

    @staticmethod
    def export_to_file(  # type: ignore[override]
        filename: Path | str, **kwargs: Any
    ) -> None:
        """
        Write the DiffractionExperiment to a pyFAI style poni file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        **kwargs : Any, optional
            The following keyword arguments are defined:

            diffraction_exp : DiffractionExperiment, optional
                The DiffractionExperiment instance to be exported.
                The default is the DiffractionExperimentContext.
        """
        _exp: DiffractionExperiment = kwargs.get(
            "diffraction_exp", DiffractionExperimentContext()
        )
        verify_is_new_file_or_replace_set(filename, **kwargs)
        _det = _exp.get_param_value("detector_name")
        _pdata = {
            key: _exp.get_param_value(f"detector_{key}")
            for key in ["rot1", "rot2", "rot3", "poni1", "poni2"]
        }
        _pdata["detector"] = _det if _det in PYFAI_DETECTOR_NAMES else "Detector"
        _pdata["distance"] = _exp.get_param_value("detector_dist")
        _pdata["detector_config"] = {
            "pixel1": (1e-6 * _exp.get_param_value("detector_pxsizey")),
            "pixel2": (1e-6 * _exp.get_param_value("detector_pxsizex")),
            "max_shape": _exp.det_shape,
        }
        _pdata["wavelength"] = _exp.get_param_value("xray_wavelength") * 1e-10
        pfile = PoniFile(data=_pdata)
        with open(filename, "w") as _file:
            pfile.write(_file)
            _file.write("\n# This file was created by pydidas.")
            _file.write(f"\n# pydidas_det_name = {_det}")

    @classmethod
    def import_from_file(
        cls,
        filename: str | Path,
        diffraction_exp: DiffractionExperiment | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Restore the DiffractionExperimentContext from a YAML file.

        Parameters
        ----------
        filename : str or Path
            The filename of the file to be written.
        diffraction_exp : DiffractionExperiment or None, optional
            The DiffractionExperiment instance to be updated.
            The default is None.
        **kwargs : Any, optional
            Additional keyword arguments. Not used in this implementation.
        """
        geo = Geometry().load(PoniFile(data=filename))  # type: ignore[arg-type]
        with open(filename, "r") as _file:
            _content = _file.readlines()
        _imported_params = cls._update_detector_from_pyfai(geo.detector)
        _imported_params.update(cls._update_geometry_from_pyfai(geo))
        for _line in _content:
            if "pydidas_det_name" in _line:
                _det_name = _line.split("pydidas_det_name = ")[1].strip()
                _imported_params["detector_name"] = _det_name
        cls.verify_all_entries_present(_imported_params, exclude_det_mask=True)
        cls.update_diffraction_exp(_imported_params, diffraction_exp=diffraction_exp)

    @staticmethod
    def _update_detector_from_pyfai(
        det: Detector,
    ) -> dict[str, Any]:
        """
        Update the detector information from a pyFAI Detector instance.

        Parameters
        ----------
        det : Detector
            The pyFAI Detector instance.

        Returns
        -------
        dict[str, Any]
            A dictionary with the detector parameters.
        """
        if not isinstance(det, Detector):
            raise TypeError(
                f"Object '{det} (type {type(det)}' is not a Detector instance."
            )
        return {
            "detector_name": det.name,
            "detector_npixx": det.shape[1],
            "detector_npixy": det.shape[0],
            "detector_pxsizex": 1e6 * det.pixel2,
            "detector_pxsizey": 1e6 * det.pixel1,
        }

    @staticmethod
    def _update_geometry_from_pyfai(geo: Geometry) -> dict[str, Any]:
        """
        Update the geometry information from a pyFAI Geometry instance.

        Parameters
        ----------
        geo : pyFAI.geometry.Geometry
            The geometry instance.

        Returns
        -------
        dict[str, Any]
            A dictionary with the geometry parameters.
        """
        if not isinstance(geo, Geometry):
            raise TypeError(
                f"Object '{geo} (type {type(geo)}' is not a "
                "pyFAI.geometry.Geometry instance."
            )
        _geo_dict = geo.getPyFAI()
        return {
            "xray_wavelength": geo.wavelength * 1e10,
            "xray_energy": LAMBDA_IN_M_TO_E / geo.wavelength,
            "detector_dist": _geo_dict["dist"],
            "detector_poni1": _geo_dict["poni1"],
            "detector_poni2": _geo_dict["poni2"],
            "detector_rot1": _geo_dict["rot1"],
            "detector_rot2": _geo_dict["rot2"],
            "detector_rot3": _geo_dict["rot3"],
        }
