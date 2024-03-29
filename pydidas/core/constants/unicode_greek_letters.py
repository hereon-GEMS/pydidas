# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The unicode_greek_letters module holds dictionaries to convert unicode Greek
letters to their ASCII names and vice versa.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GREEK_UNI_TO_ASCII", "GREEK_ASCII_TO_UNI"]


GREEK_UNI_TO_ASCII = {
    "\u0391": "Alpha",
    "\u0392": "Beta",
    "\u0393": "Gamma",
    "\u0394": "Delta",
    "\u0395": "Epsilon",
    "\u0396": "Zeta",
    "\u0398": "Theta",
    "\u0399": "Iota",
    "\u039A": "Kappa",
    "\u039B": "Lamda",
    "\u039C": "Mu",
    "\u039D": "Nu",
    "\u039E": "Xi",
    "\u039F": "Omicron",
    "\u03A0": "Pi",
    "\u03A1": "Rho",
    "\u03A3": "Sigma",
    "\u03A4": "Tau",
    "\u03A5": "Upsilon",
    "\u03A6": "Phi",
    "\u03A7": "Chi",
    "\u03A8": "Psi",
    "\u03A9": "Omega",
    "\u0397": "Eta",
    "\u03B1": "alpha",
    "\u03B2": "beta",
    "\u03B3": "gamma",
    "\u03B4": "delta",
    "\u03B5": "epsilon",
    "\u03B6": "zeta",
    "\u03B8": "theta",
    "2\u03B8": "2theta",
    "\u03B9": "iota",
    "\u03BA": "kappa",
    "\u03BB": "lamda",
    "\u03BC": "mu",
    "\u03BD": "nu",
    "\u03BE": "xi",
    "\u03BF": "omicron",
    "\u03C0": "pi",
    "\u03C1": "rho",
    "\u03C3": "sigma",
    "\u03C4": "tau",
    "\u03C5": "upsilon",
    "\u03C6": "phi",
    "\u03C7": "chi",
    "\u03C8": "psi",
    "\u03C9": "omega",
    "\u03B7": "eta",
}


GREEK_ASCII_TO_UNI = dict(zip(GREEK_UNI_TO_ASCII.values(), GREEK_UNI_TO_ASCII.keys()))
