"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from ..dialog_button import GwDialogButton
from ...shared.mincut_manager import GwMincutManager


class GwMincutManagerButton(GwDialogButton):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.mincut_manager = GwMincutManager(self)


    def clicked_event(self):
        self.mincut_manager.manage_mincuts()
