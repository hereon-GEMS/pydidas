# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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

"""
The unicode_letters module holds dictionaries to convert unicode
letters to their ASCII names and vice versa.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["UNI_TO_ASCII", "ASCII_TO_UNI"]


UNI_TO_ASCII = {
    "\u0391": "Alpha",
    "\u0392": "Beta",
    "\u0393": "Gamma",
    "\u0394": "Delta",
    "\u0395": "Epsilon",
    "\u0396": "Zeta",
    "\u0398": "Theta",
    "\u0399": "Iota",
    "\u039a": "Kappa",
    "\u039b": "Lamda",
    "\u039c": "Mu",
    "\u039d": "Nu",
    "\u039e": "Xi",
    "\u039f": "Omicron",
    "\u03a0": "Pi",
    "\u03a1": "Rho",
    "\u03a3": "Sigma",
    "\u03a4": "Tau",
    "\u03a5": "Upsilon",
    "\u03a6": "Phi",
    "\u03a7": "Chi",
    "\u03a8": "Psi",
    "\u03a9": "Omega",
    "\u0397": "Eta",
    "\u03b1": "alpha",
    "\u03b2": "beta",
    "\u03b3": "gamma",
    "\u03b4": "delta",
    "\u03b5": "epsilon",
    "\u03b6": "zeta",
    "\u03b8": "theta",
    "2\u03b8": "2theta",
    "\u03b9": "iota",
    "\u03ba": "kappa",
    "\u03bb": "lamda",
    "\u03bc": "mu",
    "\u03bd": "nu",
    "\u03be": "xi",
    "\u03bf": "omicron",
    "\u03c0": "pi",
    "\u03c1": "rho",
    "\u03c3": "sigma",
    "\u03c4": "tau",
    "\u03c5": "upsilon",
    "\u03c6": "phi",
    "\u03c7": "chi",
    "\u03c8": "psi",
    "\u03c9": "omega",
    "\u03b7": "eta",
    "\u00c5": "Angstrom",
}


ASCII_TO_UNI = dict(zip(UNI_TO_ASCII.values(), UNI_TO_ASCII.keys()))
