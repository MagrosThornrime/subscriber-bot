import discord as dc
from discord.ui import Button

from DiscordViews.CommonInfoModal import CommonInfoModal


class CommonInfoButton(Button):
    def __init__(self):
        super().__init__(
            style=dc.ButtonStyle.blurple,
            label="send common info"
        )

    async def callback(self, interaction: dc.Interaction):
        modal = CommonInfoModal()
        interaction.response.send_modal(modal)
        await modal.wait()
        await self.view.add_common_info(modal.get_common_info())
