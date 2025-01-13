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
The main_menu_actions module defines the actions for the main menu taskbar.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MAIN_MENU_MENU_ACTIONS"]


MAIN_MENU_MENU_ACTIONS = {
    "store_state": {
        "label": "&Store GUI state",
        "status_tip": (
            "Store the current state of the graphical user interface including"
            " all frame Parameters and App configurations. This action allows "
            "users to store their state in the machines configuration for "
            "loading it again at a later date."
        ),
        "icon": "mdi::content-save-check-outline",
    },
    "export_state": {
        "label": "&Export GUI state",
        "status_tip": (
            "Export the current state of the graphical user interface "
            "to a user-defined file. This includes all frame Parameters and "
            "App configurations."
        ),
        "icon": "qt-std::SP_DialogSaveButton",
    },
    "restore_state": {
        "label": "&Restore GUI state",
        "status_tip": (
            "Restore the state of the graphical user interface from a "
            "previously created snapshot."
        ),
        "icon": "mdi::backup-restore",
    },
    "restore_exit_state": {
        "label": "Restore exit state",
        "status_tip": (
            "Restore the state of the graphical user interface from the stored "
            "information at the (correct) exit."
        ),
        "icon": "mdi::history",
    },
    "import_state": {
        "label": "&Import GUI state",
        "status_tip": (
            "Import the state of the graphical user interface from a user-defined file."
        ),
        "icon": "qt-std::SP_DialogOpenButton",
    },
    "exit": {
        "label": "E&xit",
        "status_tip": "Exit the application.",
        "icon": "qt-std::SP_DialogCloseButton",
    },
    "open_settings": {
        "label": "&Settings",
        "status_tip": "Open the application settings.",
        "icon": "mdi::wrench-cog",
    },
    "open_user_config": {
        "label": "&User config",
        "status_tip": "Open the user configuration.",
        "icon": "mdi::account-cog",
    },
    "tools_export_eiger_pixel_mask": {
        "label": "Export Eiger pixel mask",
        "status_tip": "Export the Eiger pixel mask to a user-defined file.",
        "icon": "mdi::image-sync-outline",
    },
    "tools_image_series_ops": {
        "label": "Image series processing",
        "status_tip": (
            "Open the image series processing tool to convert a series of images "
            "into a single image."
        ),
        "icon": "mdi::image-multiple-outline",
    },
    "tools_mask_editor": {
        "label": "Edit detector mask",
        "status_tip": "Open the mask editor to edit the detector mask.",
        "icon": "mdi::image-lock-outline",
    },
    "tools_clear_local_logs": {
        "label": "&Clear local log files",
        "status_tip": "Clear all local log files for this pydidas version.",
        "icon": "mdi::delete-outline",
    },
    "open_documentation_browser": {
        "label": "Open documentation in default web browser",
        "status_tip": "Open the pydidas documentation in the default browser.",
        "icon": "mdi::book-open-outline",
    },
    "open_about": {
        "label": "&About pydidas",
        "status_tip": "Open the about dialog.",
        "icon": "mdi::information-outline",
    },
    "open_paths": {
        "label": "Pydidas Paths",
        "status_tip": "Show the default paths for pydidas configuration files.",
        "icon": "mdi::folder-outline",
    },
    "check_for_update": {
        "label": "Check for software updates",
        "status_tip": "Check for a new version of pydidas.",
        "icon": "mdi::update",
    },
    "open_feedback": {
        "label": "Open feedback form",
        "status_tip": "Open the feedback dialog.",
        "icon": "mdi::comment-quote-outline",
    },
    "toggle_logging_dockable": {
        "label": "Hide logging widget",
        "status_tip": "Hide the 'logging and information' status widget.",
        "icon": "mdi::eye-remove-outline",
    },
}
