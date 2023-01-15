import discord as dc
from discord.ui import Button


class PluginInfoButton(Button):
    def __init__(self):
        super().__init__(
            style=dc.ButtonStyle.gray,
            label="send plugin info",
            disabled=True
        )

    async def callback(self, interaction: dc.Interaction):
        modal = PluginInfoModal()
        interaction.response.send_modal(modal)
        await modal.wait()
        self.view.add_plugin_info(modal.get_plugin_info())

    def unlock(self):
        self.disabled = False
        self.style = dc.ButtonStyle.blurple

    def lock(self):
        self.disabled = True
        self.style = dc.ButtonStyle.gray

    def is_locked(self) -> bool:
        return self.disabled
