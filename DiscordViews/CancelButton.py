import discord as dc
from discord.ui import Button


class CancelButton(Button):
    def __init__(self):
        super().__init__(
            style=dc.ButtonStyle.red,
            label="Cancel"
        )

    async def callback(self, interaction: dc.Interaction):
        await self.view.cancel()
