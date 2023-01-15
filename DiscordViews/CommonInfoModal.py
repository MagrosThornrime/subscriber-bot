import discord as dc
from discord import InputTextStyle
from discord.ui import Modal, InputText

from Bot.CommonInfo import CommonInfo


class CommonInfoModal(Modal):
    def _add_all_items(self):
        items = [InputText(label="Tag", style=InputTextStyle.short,
                           placeholder="task tag"),
                 InputText(label="Channel", style=InputTextStyle.short,
                           placeholder="channel's name",
                           required=False),
                 InputText(label="When to start", style=InputTextStyle.short,
                           placeholder="days:hours:minutes:seconds",
                           required=False),
                 InputText(label="Period", style=InputTextStyle.short,
                           placeholder="days:hours:minutes:seconds"),
                 InputText(label="Count", style=InputTextStyle.short,
                           placeholder="How many times to run the task?",
                           required=False)
                 ]
        for item in items:
            self.add_item(item)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_all_items()

    def get_common_info(self) -> CommonInfo:
        return CommonInfo(
            tag=self.children[0].value,
            channel=self.children[1].value,
            when_to_start=self.children[2].value,
            period=self.children[3].value,
            count=self.children[4].value
        )

    async def callback(self, interaction: dc.Interaction):
        self.stop()
