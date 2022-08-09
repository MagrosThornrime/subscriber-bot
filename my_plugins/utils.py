from copy import copy
from importlib import import_module
from pathlib import Path

import aiofiles
import discord as dc
from discord.ui import Modal, InputText


def _prepare_params(params: dict[str]) -> dict:
    prepared = params.copy()
    if "style" in params:
        if params["style"] == "long":
            prepared["style"] = dc.InputTextStyle.long
        else:
            prepared["style"] = dc.InputTextStyle.short
    if "min_length" in params:
        prepared["min_length"] = int(params["min_length"])
    if "max_length" in params:
        prepared["max_length"] = int(params["max_length"])
    if "required" in params:
        prepared["required"] = True if params["required"] == "true" else False
    if "row" in params:
        prepared["row"] = int(params["row"])
    return prepared


def _create_input_text(params: dict[str]) -> InputText:
    prepared = _prepare_params(params)
    return InputText(**prepared)


def create_modal(name: str, modal_specs: list[dict[str]],
                attribute_names: list[str]) -> Modal:

    class CustomModal(Modal):
        def __init__(self, specs: list[str], 
                    attribute_names: list[str], *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attribute_names = attribute_names
            self.arguments = {}
            for spec in specs:
                self.add_item(_create_input_text(spec))

        async def callback(self, interaction: dc.Interaction):
            for index, attribute in enumerate(self.attribute_names):
                self.arguments[attribute] = self.children[index].value
            await interaction.response.send_message("Arguments passed")
            self.stop()

    title = f"Plugin '{name}' is asking for arguments"
    return CustomModal(modal_specs, attribute_names, title=title)
