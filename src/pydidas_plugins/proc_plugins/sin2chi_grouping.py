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
A module for grouping d-spacing values according the sin^2(chi) values.

This data grouping is a necessary step for the sin^2(chi) method.
This module expects a pydidas Dataset with d-spacing values [nm, A] and
chi values [deg]. Label for d-spacing is `position`.
"""

__author__ = "Gudrun Lotze, Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"
__all__ = ["DspacingSin2chiGrouping"]


from enum import IntEnum

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_STRESS_STRAIN
from pydidas.plugins import ProcPlugin


LABELS_CHI = "chi"
LABELS_SIN2CHI = "sin^2(chi)"
LABELS_POSITION = "position"
LABELS_DIM0 = "0: d-, 1: d+, 2: d_mean"

UNITS_NANOMETER = "nm"
UNITS_ANGSTROM = "A"
UNITS_DEGREE = "deg"

S2C_TOLERANCE = 1e-6
NPT_AZIM_LIMIT = 3000


PARAMETER_KEEP_RESULTS = "keep_results"


# Define the Enum
# 1 is close to zero
# 2 is positive
# 0 is negative
class Category(IntEnum):
    NEGATIVE: int = 0
    ZERO: int = 1
    POSITIVE: int = 2


class DictViaAttrs:
    """
    Access a dict via attributes.

    This class will enhance the dict for self._config to support IDE functionalities.
    A (data)class offers comfort and reduction of errors due to the code-analysis
    feature of an IDE.
    """

    def __init__(self, d):
        self.__dict__["_dict"] = d
        self._chi_key: int | None = None
        self._pos_key: int | None = None
        self._pos_idx: int | None = None
        self._s2c_labels: np.ndarray | None = None
        self._n_components: int | None = None

    def __getattr__(self, attr):
        if attr == "_dict":
            # getattr before ._dict is set up
            raise AttributeError(attr)
        try:
            return self._dict[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self._dict[attr] = value


class DspacingSin2chiGrouping(ProcPlugin):
    """
    Grouping of d-spacing values according to the slopes in sin^2(chi)
    and similarity in sin^2(chi) values.

    chi is the azimuthal angle of one diffraction image.

    Note: Using chi instead of psi for the sin^2(psi) method is an approximation in the
    high-energy X-ray regime. Psi is the angle between the scattering vector q
    and the sample normal. The geometry of the experiment requires that the sample
    normal is parallel to the z-axis, i.e. the incoming beam is parallel to the
    sample surface.

    Results will be stored.

    Output: Both d-spacing branches (d(-), d(+)) and their mean vs. sin^2(chi)

    Steps:

    1. A clustering algorithm groups chi values based on similar sin^2(chi) values.
       The tolerance level for similarity between sin^2(chi) values is set to 1e-6.
       Chi values with similar sin^2(chi) values are grouped.

    2. The algorithm separates the d-spacing values into groups based on the
       similarity of sin^2(chi) values and their slope sign (positive or negative).

    3. After grouping, d-spacing values are categorized by their group labels
       and the slope sign.

    4. In each d-spacing branch, positive (d(+)) or negative (d(-)), multiple groups
       can be identified.

    5. Finally, the mean of positive and negative d-spacing values vs. sin^2(chi)
       is calculated for each group.


    NOTE: This plugin expects position (d-spacing) in [nm, A] and chi in [deg]
    as input data. The limit for azimuthal points is set to 3000.
    """

    plugin_name = "Group d-spacing according to sin^2(chi) method"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_STRESS_STRAIN
    input_data_dim = -1
    output_data_dim = 2
    output_data_label = (
        "0: position_neg; 1: position_pos; 2: Mean of (position_neg, position_pos)"
    )
    new_dataset = True

    # modification of the keep_results parameter to ensure results are always stored
    _generics = ProcPlugin.generic_params.copy()
    _generics[PARAMETER_KEEP_RESULTS].value = True
    _generics[PARAMETER_KEEP_RESULTS].choices = [True]
    generic_params = _generics

    @staticmethod
    def _ensure_dataset_instance(ds: Dataset) -> None:
        """
        Ensure the input is an instance of Dataset.

        Parameters
        ----------
        ds : Dataset
            The input to check.

        Raises
        ------
        UserConfigError
            If ds is not an instance of Dataset.
        """
        if not isinstance(ds, Dataset):
            raise UserConfigError("Input must be an instance of Dataset.")

    @staticmethod
    def _ensure_npt_azim_limit(chi: np.ndarray) -> None:
        """
        Ensure the number of azimuthal angles is below a certain limit.

        The limit is hardcoded in the value for the NPT_AZIM_LIMIT constant. The limit
        is defined to work with the default tolerance value for grouping similar
        chi positions.

        Parameters
        ----------
        chi : np.ndarray
            The array of azimuthal angles.

        Raises
        ------
        UserConfigError
            If the number of azimuthal angles exceeds the limit.
        """
        if chi.size > NPT_AZIM_LIMIT:
            raise UserConfigError(
                f"Number of azimuthal angles exceeds the limit of {NPT_AZIM_LIMIT}."
            )

    @staticmethod
    def _get_param_unit_at_index(
        ds_units: dict[int, tuple[str, str]], pos_idx: int
    ) -> tuple[str, str]:
        """
        Retrieve the parameter name and unit from the dictionary `ds_units`
        at a specified index `pos_idx`.

        This function is designed to extract the parameter name and its
        corresponding unit from a dictionary where each entry is keyed by an index.
        It specifically checks that the parameter name at the given index is
        'position', ensuring consistency for applications that require this
        specific parameter. If the parameter at `pos_idx` is not 'position', or
        if `pos_idx` is not a valid key in the dictionary, appropriate exceptions
        are raised.

        Parameters
        ----------
        ds_units : dict
            A dictionary with integer keys, where each key-value pair consists of
            an index (key) and a tuple (value) containing a parameter name and its unit.
        self._pos_idx : int
            The index for which the parameter name and unit are to be retrieved.

        Returns
        -------
        name : str
            The parameter name (str) at the specified index.
        unit : str
            The unit associated with the parameter name.

        Raises
        ------
        IndexError
            If `pos_idx` is not a valid key within `ds_units`, indicating that
            the index is out of range.
        ValueError
            If the parameter name at the specified `pos_idx` is not 'position',
            indicating a mismatch in expected parameter naming.

        Examples
        --------
        >>> ds_units = {0: ('time', 's'), 1: ('position', 'm'), 2: ('temperature', 'K')}
        >>> get_param_unit_at_index(ds_units, 1)
        ('position', 'm')

        Notes
        -----
        This function is particularly useful in contexts where specific parameters
        and their units are critical, such as in scientific experiments or data
        analysis tasks. It enforces the presence of a 'position' parameter at the
        specified index, aiding in data validation and consistency checks.
        """
        if pos_idx not in ds_units:
            raise IndexError(
                f"pos_idx {pos_idx} is out of range for the dictionary keys"
            )
        param_info = ds_units[pos_idx]
        param_name, unit = param_info

        if param_name != LABELS_POSITION:
            raise ValueError(
                f"The parameter name at pos_idx {pos_idx} is not 'position'"
            )
        return param_name, unit

    @staticmethod
    def _extract_and_verify_units(ds: Dataset) -> None:
        """
        Extract and verify the units for chi and position in the dataset.

        Note that this method modifies the input dataset in place.

        Parameters
        ----------
        ds : Dataset
            The dataset to extract and verify units from.
        """
        chi_units_allowed: list[str] = [UNITS_DEGREE]

        if (
            ds.axis_labels[0] not in [LABELS_CHI]
            or ds.axis_units[0] not in chi_units_allowed
        ):
            raise UserConfigError(
                "The input dataset does not contain chi values in the axis and/or "
                "the chi values are given in an unsupported unit. Supported units "
                f"are [{', '.join(chi_units_allowed)}]."
            )

        # position/pos contains the unit for d_spacing
        pos_units_allowed: list[str] = [UNITS_NANOMETER, UNITS_ANGSTROM]

        # Ensure 'position' is in the data_label
        if LABELS_POSITION not in ds.data_label:
            raise UserConfigError(f"Key '{LABELS_POSITION}' not found in data_label.")

        parts = ds.data_label.split("/")

        if len(parts) != 2:
            raise ValueError("Invalid data_label format. Expected 'position / unit'.")

        pos_unit = parts[1].strip()

        if pos_unit not in pos_units_allowed:
            raise UserConfigError(
                f"Unit '{pos_unit}' is not allowed for key '{LABELS_POSITION}."
            )

        # Update the dataset with the verified unit
        ds.data_label = parts[0].strip()
        ds.data_unit = pos_unit

    def __init__(self):
        super().__init__()
        self.config = DictViaAttrs(self._config)

    def execute(self, ds: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        if ds.ndim == 2:
            chi, d_spacing = self._ds_slicing(ds)
        elif ds.ndim == 1:
            chi, d_spacing = self._ds_slicing_1d(ds)
        else:
            raise UserConfigError("Dataset has to be 1D or 2D.")

        self._ensure_npt_azim_limit(chi)
        d_spacing_pos, d_spacing_neg = self._group_d_spacing_by_chi(d_spacing, chi)
        d_spacing_combined = self._combine_sort_d_spacing_pos_neg(
            d_spacing_pos, d_spacing_neg
        )

        d_output_sin2chi_method = self._create_final_result_sin2chi_method(
            d_spacing_combined
        )

        return d_output_sin2chi_method, kwargs

    def _chi_pos_verification(self, ds: Dataset) -> tuple[int, tuple[int, int]]:
        """
        Verify if the dataset `ds` contains 'chi' and 'position' for d-spacing.

        Parameters
        ----------
        ds : Dataset
            The dataset to be verified.

        Returns
        -------
        chi_key : int
            The index associated with 'chi'.
        position_key : tuple
            A tuple where the first element is the index in `axis_labels` where
            'position' descriptor is found, and the second element is the key in
             the structured string resembling a dict.

        Raises
        ------
        UserConfigError
            If the input is not of type Dataset.
        UserConfigError
            If multiple 'chi' entries are found in the dataset.
        UserConfigError
            If 'chi' or the key containing 'position' is missing in the dataset.

        Notes
        -----
        This function checks the `axis_labels` of the dataset for the presence of
        'chi' and 'position'. It ensures that there is exactly one 'chi' and at least
        one 'position' descriptor. The function raises errors if the conditions are
        not met, ensuring the dataset's structure is as expected for further processing.
        """

        self._ensure_dataset_instance(ds)

        axis_labels = ds.axis_labels

        # Collect indices where 'chi' is found
        chi_indices = [key for key, value in axis_labels.items() if value == LABELS_CHI]

        if len(chi_indices) > 1:
            raise UserConfigError('Multiple "chi" found. Check your dataset.')

        if not chi_indices:
            raise UserConfigError("chi is missing. Check your dataset.")

        # Assuming there's exactly one 'chi', get the index
        chi_key = chi_indices[0]

        reverse_axis_labels = dict(zip(axis_labels.values(), axis_labels.keys()))

        # Process to find 'position' in the complex structured string
        position_key = None
        for value, position_index in reverse_axis_labels.items():
            if isinstance(value, str) and "position" in value:
                parts = value.split(";")
                for part in parts:
                    if "position" in part:
                        # Assume the part is structured as 'key: description'
                        part_key, _ = part.split(":")
                        part_key = int(
                            part_key.strip()
                        )  # Convert the key part to integer
                        position_key = (position_index, part_key)
                        break
                if position_key is not None:
                    break

        # Check if 'position' is found
        if position_key is None:
            raise UserConfigError(
                'Key containing "position" is missing. Check your dataset.'
            )

        return chi_key, position_key

    def _extract_units(self, ds: Dataset) -> dict[int, list[str]]:
        """
        Extract units from `data_label` in a `Dataset`.

        The `data_label` corresponds to the written parameters in `fit_labels`.

        This function parses the `data_label` string of a `Dataset` to extract
        units associated with each parameter specified in the `fit_labels`. It
        constructs a dictionary where each key-value pair corresponds to a
        parameter and its unit. The function ensures that the dataset is a valid
        instance of `Dataset` and raises appropriate errors if units for specified
        fit labels are not found.

        Parameters
        ----------
        ds : Dataset
            The dataset from which units are to be extracted.
        Returns
        -------
        dict
            A dictionary mapping each parameter (specified by its index in `fit_labels`)
            to a list containing the parameter name and its extracted unit.

        Raises
        ------
        UserConfigError
            If `ds` is not an instance of `Dataset`.
        UserConfigError
            If a unit for any parameter specified in `fit_labels` is not found in
            `data_label`.

        Notes
        -----
        The function relies on the structure of `data_label` in the `Dataset`.
        `data_label` should be a semicolon-separated list of parameter descriptions,
        where each description is formatted as "index: name/unit".
        """
        self._ensure_dataset_instance(ds)

        chi_key, (pos_key, _) = self._chi_pos_verification(ds)

        data_label = ds.data_label
        fit_labels = ds.axis_labels[pos_key]

        # Step 1: Extract parameter names from fit_labels
        fit_labels_dict = {
            int(item.split(":")[0].strip()): item.split(":")[1].strip()
            for item in fit_labels.split(";")
        }

        # Step 2: Extract units from data_label
        data_label_dict = {}
        data_label_parts = data_label.split(";")
        for part in data_label_parts:
            if "/" in part:
                name, unit = part.split("/")
                name = name.split(":")[-1].strip()
                unit = unit.strip()
                data_label_dict[name] = unit

        # Step 3: Create a mapping of fit_labels (with their indices) to their
        # corresponding units
        result = {}
        for index, param in fit_labels_dict.items():
            try:
                unit = data_label_dict[param]
            except KeyError:
                raise UserConfigError(f"Unit not found for parameter: {param}")
            result[index] = [param, unit]

        # Step 4: Append chi and its unit to the result as the highest key
        chi_label = ds.axis_labels[chi_key]
        chi_unit = ds.axis_units[chi_key]
        if result:
            new_key = max(result.keys()) + 1
        else:
            new_key = 0
        result[new_key] = [chi_label, chi_unit]

        return result

    def _chi_pos_unit_verification(self, ds: Dataset):
        """
        Verifies that the units for 'chi' and 'position' in a dataset are correct.

        This function checks a Pydidas Dataset to ensure that the units for 'chi'
        and 'position' are within the allowed parameters. 'Position' is expected
        to contain d_spacing values. The function raises exceptions if the dataset is
        not a Pydidas Dataset or if the units for 'chi' or 'position' do not meet
        the specified criteria.

        Parameters
        ----------
        ds : Dataset
            A Pydidas Dataset object containing fitting results. It is expected
            that 'position' contains d_spacing values.

        Raises
        ------
        UserConfigError
            Raised if the input `ds` is not an instance of Dataset.
        UserConfigError
            Raised if the units for 'chi' or 'position' are not within the allowed
            parameters. The allowed units for 'position' are 'nm' (nanometers) and
            'A' (angstroms). For 'chi', the allowed unit is 'deg' (degrees).

        Notes
        -----
        The function currently only allows 'chi' to be in degrees ('deg').
        If there is a need to allow 'chi' in radians ('rad'), adjustments will
        be necessary in the calculation of sin^2(chi).
        """
        self._ensure_dataset_instance(ds)

        ds_units: dict[int, list[str]] = self._extract_units(ds)

        # position/pos contains the unit for d_spacing
        pos_units_allowed: list[str] = [UNITS_NANOMETER, UNITS_ANGSTROM]
        # Only chi in degree is allowed.
        chi_units_allowed: list[str] = [UNITS_DEGREE]

        params_to_check = [LABELS_POSITION, LABELS_CHI]

        for _, val in ds_units.items():
            label = val[
                0
            ]  # First item in the value list is the label (e.g., 'position', 'chi')
            unit = val[1]  # Second item is the unit (e.g., 'nm', 'deg')

            if label in params_to_check:
                if label == LABELS_POSITION and unit not in pos_units_allowed:
                    raise UserConfigError(f"Unit {unit} not allowed for {label}.")
                if label == LABELS_CHI and unit not in chi_units_allowed:
                    raise UserConfigError(f"Unit {unit} not allowed for {label}.")

    def _extract_d_spacing(self, ds: Dataset, pos_key: int, pos_idx: int) -> Dataset:
        """
        Extracts the d-spacing value from a ndim Dataset at a specified position.

        This function is designed to extract a specific d-spacing value from
        a Dataset, given the dimension (pos_key) and the index within that
        dimension (pos_idx) where 'position' information is stored. It utilizes
        slicing to isolate the desired d-spacing value and adjusts the metadata
        (data_label and data_unit) of the returned d-spacing to reflect the
        parameter name and unit at the specified index.

        Parameters
        ----------
        ds : Dataset
            A Dataset object representing a multidimensional array
        pos_key : int
            The key (dimension) within the dataset that contains 'position'
            information relevant to d-spacing.
        pos_idx : int
            The index within the dimension specified by self._pos_key that
            contains the specific 'position' information for which d-spacing
            is to be extracted.

        Returns
        -------
        Dataset
            A Dataset object containing the extracted d-spacing value. The
            data_label and data_unit of this object are set to the parameter name
            and unit at the specified index, respectively.

        Raises
        ------
        IndexError
            If `pos_key` or `pos_idx` are out of bounds for the dimensions of `ds`.
        ValueError
            If the parameter at `pos_idx` is not 'position', indicating a mismatch
            in expected parameter naming.

        Examples
        --------
        Assuming `ds` is a Dataset object with dimensions representing different
        parameters, including 'position':

        >>> ds = Dataset(...)
        >>> pos_key = 1  # Assuming 'position' information is in the second dimension
        >>> pos_idx = 5  # Index within the 'position' dimension
        >>> d_spacing = extract_d_spacing(ds, pos_key, pos_idx)
        >>> print(d_spacing.data_label, d_spacing.data_unit)
        'position', 'm'

        Notes
        -----
        - The function assumes that the input Dataset `ds` includes a method
          `extract_units` that returns a dictionary mapping dimension indices
          to (parameter name, unit) tuples.
        - The slicing operation is performed in a way that isolates the d-spacing
          value at the specified 'position', and the result is squeezed to remove
          any singleton dimensions.
        """
        ds_units = self._extract_units(ds)

        key_at_pos_idx, unit_at_pos_idx = self._get_param_unit_at_index(
            ds_units, pos_idx
        )

        # slice(None, None, None) is equivalent to "":"" in one dimension of the
        # array. Explicit representation of the slice object shows all three
        # parameters, even if the step parameter is not explicitly provided.
        _slices = []
        for _dim in range(ds.ndim):
            if _dim != pos_key:
                _slices.append(slice(None, None))
            elif _dim == pos_key:
                _slices.append(slice(pos_idx, pos_idx + 1))

        d_spacing = ds[*_slices]
        d_spacing = d_spacing.squeeze()

        # Slicing does not work on the data_label
        # This is a workaround
        d_spacing.data_label = key_at_pos_idx
        d_spacing.data_unit = unit_at_pos_idx

        return d_spacing

    def _ds_slicing_1d(self, ds: Dataset) -> tuple[np.ndarray, Dataset]:
        """
        Get the chi values and d-spacing values from a 1D dataset.

        Parameters
        ----------
        ds : Dataset
            The dataset to extract chi and d-spacing values from.

        Returns
        -------
        chi : np.ndarray
            The chi values (i.e. the x-axis values) from the dataset.
        d_spacing : Dataset
            The d-spacing values (i.e. the y data) from the dataset.
        """
        self._ensure_dataset_instance(ds)
        self._extract_and_verify_units(ds)

        # Assuming there's exactly one 'chi', get the index
        self.config._chi_key = 0
        chi = ds.axis_ranges[self.config._chi_key]

        return chi, ds

    def _ds_slicing(self, ds: Dataset) -> tuple[np.ndarray, Dataset]:
        """
        Extracts d-spacing values and associated chi values from a Dataset.

        The slicing targets chi and d-spacing values of input Dataset.

        This function is designed to work with a Dataset object that contains
        multidimensional data representing different physical parameters, including
        d-spacing and chi values. It identifies the relevant dimensions for chi and
        d-spacing based on predefined criteria, verifies the units of these
        dimensions, and then extracts the chi values and d-spacing values for a
        specific scan position. The function ensures that the extracted d-spacing
        values are one-dimensional, raising an error if this condition is not met.
        It also checks for and handles potential errors related to the input data
        type and the slicing of empty arrays.

        Parameters
        ----------
        ds : Dataset
            A Dataset object containing multidimensional data of one scan position
            from which d-spacing and chi values are to be extracted.

        Returns
        -------
        chi : array-like
            An array of chi values associated with the extracted d-spacing values.
        d_spacing : array-like
            An array of d-spacing values extracted from the Dataset object for a
            specific scan position.

        Raises
        ------
        UserConfigError
            If the input `ds` is not of type Dataset, indicating an incorrect
            data type was passed.
        ValueError
            If the dimension of the extracted d_spacing is not 1, indicating a
            mismatch in expected data structure. If the array of d_spacing values
            is empty, indicating slicing out of bounds or an empty dataset.

        Notes
        -----
        - The method relies on two other functions: `chi_pos_verification` to
          identify the relevant dimensions for chi and d-spacing, and
          `chi_pos_unit_verification` to verify the units of these dimensions.
        - It is essential that the Dataset object `ds` follows a specific
          structure where chi and d-spacing values can be identified and extracted
          based on their dimensions and units.
        """
        self._ensure_dataset_instance(ds)

        # Identification of chi and position
        if (
            self.config._chi_key is None
            or self.config._pos_key is None
            or self.config._pos_idx is None
        ):
            self.config._chi_key, (self.config._pos_key, self.config._pos_idx) = (
                self._chi_pos_verification(ds)
            )
        else:
            chi_key, (pos_key, pos_idx) = self._chi_pos_verification(ds)
            if (
                self.config._chi_key != chi_key
                or self.config._pos_key != pos_key
                or self.config._pos_idx != pos_idx
            ):
                raise ValueError(
                    "Chi and position keys do not match with previous dataset."
                )
        # Verification of units for chi and position. Checks currently for each dataset
        self._chi_pos_unit_verification(ds)

        # select the chi values
        chi = ds.axis_ranges[self.config._chi_key]

        # Extract d-spacing values
        d_spacing = self._extract_d_spacing(
            ds, self.config._pos_key, self.config._pos_idx
        )

        # Slicing out of indices/bounds returns an empty array. Check for empty array
        if d_spacing.size == 0:
            # Should check for empty arrays in case of slicing beyond bounds
            raise ValueError("Array is empty, slicing out of bounds.")

        if not d_spacing.ndim == 1:
            raise ValueError("Dimension mismatch.")

        return chi, d_spacing

    def _idx_s2c_grouping(
        self, chi: np.ndarray, tolerance: float = S2C_TOLERANCE
    ) -> tuple[int, np.ndarray]:
        """
        Groups chi angles based on the similarity of their sin^2(chi) values
        within a specified tolerance.

        This function takes an array of chi angles in degrees and groups them
        based on the similarity of their sin^2(chi) values.
        Two chi values belong to the same group if the absolute difference between
        their sin^2(chi) values is less than the specified tolerance.

        Parameters
        ----------
        chi : np.ndarray
            A 1D numpy array of chi angles in degrees.
        tolerance : float, optional
            The tolerance level for grouping sin^2(chi) values. Defaults to 2e-4.

        Returns
        -------
        n_components : int
            The number of unique groups formed based on the similarity of
            sin^2(chi) values.
        s2c_labels : np.ndarray
            An array of the same shape as `chi`, where each element is an
            integer label corresponding to the group of its sin^2(chi) value.

        Raises
        ------
        TypeError
            If the input `chi` is not a numpy ndarray.

        Examples
        --------
        >>> chi = np.array([0, 30, 60, 90])
        >>> n_components, s2c_labels = idx_s2c_grouping(chi)
        >>> print(n_components)
        4
        >>> print(s2c_labels)
        [0 1 2 3]

        Notes
        -----
        The function internally computes the sin^2(chi) for each angle in `chi`,
        then creates a similarity matrix to identify groups of angles with
        sin^2(chi) values within the specified tolerance. It uses sparse matrix
        techniques to efficiently handle large arrays of angles.
        """
        if not isinstance(chi, np.ndarray):
            raise TypeError("Chi needs to be an np.ndarray.")

        s2c = np.sin(np.deg2rad(chi)) ** 2

        # Create the similarity matrix
        similarity_matrix = np.abs(s2c[:, np.newaxis] - s2c[np.newaxis, :]) <= tolerance

        # Convert boolean matrix to sparse matrix
        sparse_matrix = csr_matrix(similarity_matrix.astype(int))

        # Find connected components
        n_components, s2c_labels = connected_components(
            csgraph=sparse_matrix, directed=False, return_labels=True
        )

        return n_components, s2c_labels

    def _group_d_spacing_by_chi(
        self, d_spacing: Dataset, chi: np.ndarray, tolerance: float = S2C_TOLERANCE
    ) -> tuple[Dataset, Dataset]:
        """
        Groups d-spacing values based on the chi angles and categorize them by
        the slope of their sin^2(chi) values.

        This function processes d-spacing values associated with different chi
        angles. It categorizes these values based on the slope
        (positive, negative, or near-zero) of their sin^2(chi) function.
        The function returns two datasets, one for positive slopes and another
        for negative slopes, each containing the mean d-spacing values for their
        respective categories.

        Parameters
        ----------
        d_spacing : Dataset
            A dataset of d-spacing values.
        chi : np.ndarray
            A 1D numpy array of chi angles in degrees.
        tolerance : float, optional
            The tolerance level for grouping sin^2(chi) values. Defaults to 1e-6.
            This parameter ensures that all different groups are accurately identified
            with this tight tolerance.

        Returns
        -------
        mean_pos : Dataset
            A dataset which contains the mean d-spacing values for groups with a
            positive slope in their sin^2(chi) values.
        mean_neg : Dataset
            A dataset contains the mean d-spacing values for groups with a negative
            slope in their sin^2(chi) values.

        Raises
        ------
        TypeError
            If `chi` is not a numpy ndarray or if `d_spacing` is not an instance
            of Dataset.

        Notes
        -----
        The function internally calculates the sin^2(chi) values and uses them to
        group the d-spacing values. It identifies the slope of the sin^2(chi)
        function for each group and categorizes them into positive, negative,
        or near-zero slopes based on a specified threshold. This categorization
        is crucial for analyzing the mechanical strain effects in materials
        science and engineering.

        Examples
        --------
        >>> import numpy as np
        >>> from pydidas.core import Dataset
        >>> chi = np.array([0, 30, 45, 60, 90])
        >>> d_spacing_values = np.array([1.0, 1.1, 1.2, 1.3, 1.4])
        >>> d_spacing = Dataset(
        ...     d_spacing_values,
        ...     axis_ranges={0: chi}, axis_labels={0: 'chi'},
        ...     data_label='position', data_unit='nm'
        ... )
        >>> d_spacing_pos, d_spacing_neg = group_d_spacing_by_chi(d_spacing, chi)
        >>> print(d_spacing_pos, d_spacing_neg)
        """

        if not isinstance(chi, np.ndarray):
            raise TypeError("Chi has to be of type np.ndarray")

        if not isinstance(d_spacing, Dataset):
            raise TypeError("d_spacing has to be of type Pydidas Dataset.")

        # n_components: number of groups after grouping
        # s2c_labels: sin2chi divided into different groups
        if self.config._s2c_labels is None or self.config._n_components is None:
            self.config._n_components, self.config._s2c_labels = self._idx_s2c_grouping(
                chi, tolerance=tolerance
            )
        else:
            n_components, s2c_labels = self._idx_s2c_grouping(chi, tolerance=tolerance)
            if self.config._n_components != n_components or not np.array_equal(
                self.config._s2c_labels, s2c_labels
            ):
                raise ValueError(
                    "Number of groups or s2c_labels do not match with previous dataset."
                )

        # Calculate sin2chi
        s2c = np.sin(np.deg2rad(chi)) ** 2

        # both are ordered in ascending order of increasing sin2chi
        s2c_unique_labels = np.unique(self.config._s2c_labels)

        # Calculate first derivative
        first_derivative = np.gradient(s2c, edge_order=2)

        # Define the threshold for being "close to zero", i.e. where is the slope=0
        zero_threshold = 1e-6

        # Categorize the values of the first_derivative
        categories = np.zeros_like(first_derivative, dtype=int)
        categories[first_derivative > zero_threshold] = Category.POSITIVE.value
        categories[first_derivative < -zero_threshold] = Category.NEGATIVE.value
        categories[
            (first_derivative >= -zero_threshold) & (first_derivative <= zero_threshold)
        ] = Category.ZERO.value

        # Filter
        # values close to zero (categories == 1) are added to both sides of the
        # maximum or minimum
        mask_pos = (categories == Category.POSITIVE.value) | (
            categories == Category.ZERO.value
        )
        mask_neg = (categories == Category.NEGATIVE.value) | (
            categories == Category.ZERO.value
        )

        # Advanced indexing
        # Here, s2c_labels specifies the row indices, and np.arange(s2c_num_elements)
        # specifies the column indices.
        s2c_advanced_idx = (self.config._s2c_labels, np.arange(s2c.size))
        # expected shape for future matrices
        s2c_groups_matrix_shape = s2c_unique_labels.size, s2c.size

        # s2c_label_matrix and d_spacing_matrix are useful for quality assurance
        # via visual inspection
        s2c_labels_matrix = np.full(s2c_groups_matrix_shape, np.nan)
        s2c_labels_matrix[*s2c_advanced_idx] = self.config._s2c_labels

        d_spacing_matrix = np.full(s2c_groups_matrix_shape, np.nan)
        d_spacing_matrix[*s2c_advanced_idx] = d_spacing

        s2c_matrix = np.full(s2c_groups_matrix_shape, np.nan)
        s2c_matrix[*s2c_advanced_idx] = s2c

        # Create pre-filled matrices for filtering based on the slopes and groups
        d_spacing_pos_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)
        d_spacing_neg_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)
        s2c_pos_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)
        s2c_neg_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)

        # Apply masks to create filtered matrices
        # Combination of advanced indexing and conditional assignment with np.where
        d_spacing_pos_slope_matrix[*s2c_advanced_idx] = np.where(
            mask_pos, d_spacing, np.nan
        )
        s2c_pos_slope_matrix[*s2c_advanced_idx] = np.where(mask_pos, s2c, np.nan)

        d_spacing_neg_slope_matrix[*s2c_advanced_idx] = np.where(
            mask_neg, d_spacing, np.nan
        )
        s2c_neg_slope_matrix[*s2c_advanced_idx] = np.where(mask_neg, s2c, np.nan)

        # Averaging, positive slope
        s2c_mean_pos = np.nanmean(s2c_pos_slope_matrix, axis=1)
        d_spacing_mean_pos = np.nanmean(d_spacing_pos_slope_matrix, axis=1)
        # Averaging, negative slope
        s2c_mean_neg = np.nanmean(s2c_neg_slope_matrix, axis=1)
        d_spacing_mean_neg = np.nanmean(d_spacing_neg_slope_matrix, axis=1)
        # Aim for a complete common s2c_mean_pos/neg without NaN values
        s2c_mean = np.nanmean(np.vstack((s2c_mean_pos, s2c_mean_neg)), axis=0)

        # create Datasets for output
        d_spacing_pos = Dataset(
            d_spacing_mean_pos,
            axis_ranges={0: s2c_mean},
            axis_labels={0: "sin^2(chi)"},
            data_label=f"{d_spacing.data_label}_pos",
            data_unit=d_spacing.data_unit,
        )
        d_spacing_neg = Dataset(
            d_spacing_mean_neg,
            axis_ranges={0: s2c_mean},
            axis_labels={0: "sin^2(chi)"},
            data_label=f"{d_spacing.data_label}_neg",
            data_unit=d_spacing.data_unit,
        )

        return d_spacing_pos, d_spacing_neg

    def _combine_sort_d_spacing_pos_neg(
        self, d_spacing_pos: Dataset, d_spacing_neg: Dataset
    ) -> Dataset:
        """
        Combines and sorts d-spacing datasets with positive and negative slopes
        based on sin^2(chi) values.

        This function takes two datasets, one representing d-spacing values with
        positive slopes and the other with negative slopes, with respect to their
        sin^2(chi) values. It combines these datasets and sorts the combined
        dataset in ascending order of sin^2(chi) values.

        Parameters
        ----------
        d_spacing_pos : Dataset
            A Dataset instance containing d-spacing values for positive slope
            values of sin^2(chi). The dataset must have 'sin^2(chi)' as one of
            its axis labels.
        d_spacing_neg : Dataset
            A Dataset instance containing d-spacing values for negative slope
            values of sin^2(chi). Must have the same axis labels and units as
            `d_spacing_pos`.

        Returns
        -------
        d_spacing_combined : Dataset
            A Dataset instance containing the combined and sorted d-spacing values
            from both input datasets. The combined dataset will have a new axis
            label distinguishing between positive and negative slopes
            ('0: d-, 1: d+') and will be sorted based on 'sin^2(chi)' values.

        Raises
        ------
        TypeError
            If either `d_spacing_pos` or `d_spacing_neg` is not an instance of Dataset.
        ValueError
            If the axis labels or axis ranges of the input datasets do not match.

        Notes
        -----
        The function ensures that the input datasets have matching axis labels and
        ranges for 'sin^2(chi)', which is crucial for the correct combination and
        sorting of the datasets. The sorting is stable, meaning that the relative
        order of records with equal values in 'sin^2(chi)' is preserved from the
        input datasets to the output dataset.

        Examples
        --------
        >>> d_spacing_pos = Dataset(
        ...     np.array([1.0, 1.1, 1.2]),
        ...     axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        ...     axis_labels={0: Labels.SIN2CHI}
        ... )
        >>> d_spacing_neg = Dataset(
        ...     np.array([0.9, 0.95, 1.05]),
        ...     axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        ...     axis_labels={0: Labels.SIN2CHI}
        ... )
        >>> d_spacing_combined = combine_sort_d_spacing_pos_neg(
        ...     d_spacing_pos, d_spacing_neg
        ... )
        """
        # Check if the input is of type Dataset
        if not isinstance(d_spacing_pos, Dataset) or not isinstance(
            d_spacing_neg, Dataset
        ):
            raise TypeError("Input has to be of type Dataset.")

        # Check if the axis labels are the same
        if d_spacing_pos.axis_labels != d_spacing_neg.axis_labels:
            raise ValueError("Axis labels do not match.")

        # Check if the axis ranges are the same,
        # Create a mask for non-nan values in both arrays
        s2c_axis_pos = d_spacing_pos.axis_ranges[0]
        s2c_axis_neg = d_spacing_neg.axis_ranges[0]

        if s2c_axis_pos.shape != s2c_axis_neg.shape:
            raise ValueError("Axis ranges do not have the same length.")

        comparison = np.allclose(s2c_axis_pos, s2c_axis_neg, atol=1e-15)
        if not comparison:
            raise ValueError("Axis ranges do not match.")

        # Get the indices that would sort s2c_mean_pos_copy in ascending order
        sorted_idx_pos = np.argsort(s2c_axis_pos, kind="stable")
        sorted_idx_neg = np.argsort(s2c_axis_neg, kind="stable")

        # Sorting the arrays
        s2c_axis_pos_sorted = s2c_axis_pos[sorted_idx_pos]
        d_spacing_pos_sorted = d_spacing_pos[sorted_idx_pos]
        s2c_axis_neg_sorted = s2c_axis_neg[sorted_idx_neg]
        d_spacing_neg_sorted = d_spacing_neg[sorted_idx_neg]

        d_spacing_combi_arr = np.vstack((d_spacing_neg_sorted, d_spacing_pos_sorted))

        if not np.allclose(s2c_axis_pos_sorted, s2c_axis_neg_sorted):
            diff = np.abs(s2c_axis_pos_sorted - s2c_axis_neg_sorted)
            raise ValueError(f"Arrays differ. Max absolute difference: {np.max(diff)}")

        d_spacing_combined = Dataset(
            d_spacing_combi_arr,
            axis_ranges={0: np.arange(2), 1: s2c_axis_pos_sorted},
            axis_labels={0: "0: d-, 1: d+", 1: "sin^2(chi)"},
            data_label=f"0: {d_spacing_neg.data_label}, 1: {d_spacing_pos.data_label}",
            data_unit=d_spacing_pos.data_unit,
        )

        return d_spacing_combined

    def _create_final_result_sin2chi_method(
        self, d_spacing_combined: Dataset
    ) -> Dataset:
        """
        Calculates the mean of d-spacing values and combines them into a single Dataset.

        This function takes a Dataset object containing combined d-spacing values
        (d-, d+), calculates the average d-spacing values, and combines them into a
        new Dataset object. The resulting Dataset includes updated axis ranges and
        labels.

        Parameters
        ----------
        d_spacing_combined : Dataset
            A Dataset object containing combined d-spacing values (d-, d+).

        Returns
        -------
        Dataset :
            A new Dataset object that combines the input dataset with the
            calculated mean of d-spacing values.

        Raises
        ------
        TypeError :
            If the input is not an instance of Dataset.
        ValueError :
            If the shape of d_spacing_combined is not (2, N).
        ValueError :
            If axis_labels[0] does not match '0: d-, 1: d+'.
        ValueError :
            If axis_labels[1] does not match 'sin^2(chi)'.
        """
        if not isinstance(d_spacing_combined, Dataset):
            raise TypeError("Input must be an instance of Dataset.")

        if not d_spacing_combined.shape[0] == 2:
            raise ValueError("Dataset d_spacing_combined must have a shape of (2, N).")

        if d_spacing_combined.axis_labels[0] != "0: d-, 1: d+":
            raise ValueError("axis_labels[0] does not match '0: d-, 1: d+'.")

        if d_spacing_combined.axis_labels[1] != LABELS_SIN2CHI:
            raise ValueError(f"axis_labels[1] does not match {LABELS_SIN2CHI}.")

        d_spacing_avg = d_spacing_combined.mean(axis=0).reshape(1, -1)
        arr = np.vstack((d_spacing_combined, d_spacing_avg))

        # Create the final result Dataset, when dynamic array allocation is implemented
        result = Dataset(
            arr,
            axis_ranges={
                0: np.arange(arr.shape[0]),
                1: d_spacing_combined.axis_ranges[1],
            },
            axis_labels={0: "0: d-, 1: d+, 2: d_mean", 1: LABELS_SIN2CHI},
            data_unit=d_spacing_combined.data_unit,
            data_label="d_spacing",
        )

        return result
