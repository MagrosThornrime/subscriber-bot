import discord as dc
from discord.ui import View

from Bot.CommonInfo import CommonInfo
from DiscordViews.CancelButton import CancelButton
from DiscordViews.CommonInfoButton import CommonInfoButton
from DiscordViews.PluginInfoButton import PluginInfoButton
from DiscordViews.TaskCreationError import TaskCreationError


class CreationView(View):
    def _add_buttons(self):
        self.add_item(self.cancel_button)
        self.add_item(self.common_info_button)
        self.add_item(self.plugin_info_button)
        self.add_item(self.confirm_button)

    def __init__(self, user: dc.User, tasks: list[Task]):
        super().__init__()
        self.user = user
        self.tasks = tasks
        self.common_info = None
        self.plugin_info = None
        self.cancel_button = CancelButton()
        self.common_info_button = CommonInfoButton()
        self.plugin_info_button = PluginInfoButton()
        self.confirm_button = ConfirmButton()
        self._add_buttons()

    async def interaction_check(self, interaction: dc.Interaction) -> bool:
        return interaction.user == self.user

    def _new_embed(self, message: dc.Message) -> dc.Embed:
        embed = message.embeds[0]
        return embed.copy()

    def _set_common_info(self, common_info: CommonInfo):
        # TODO: complete
        # 1. count >= 1
        # 2. periods' values >= 0
        # 3. channel exists and the bot can send messages there
        # if all are true, update common info, else raise exception
        pass

    async def cancel(self):
        message = self.message
        await message.edit(content="Cancelled", embed=None)
        self.clear_items()
        self.stop()

    async def add_common_info(self, common_info: CommonInfo):
        message = self.message
        new_embed = self._new_embed(message)
        try:
            self._set_common_info(common_info)
            new_embed.set_field_at(0, value=str(common_info))
            self.plugin_info_button.unlock()
        except TaskCreationError as exception:
            new_embed.set_field_at(0, value=str(exception))
            self.plugin_info_button.lock()
            self.confirm_button.lock()
        finally:
            await message.edit(embed=new_embed)

    def add_plugin_info(self):
        # TODO: complete
        # 1. lock the confirm button if unlocked
        # 2. edit plugin_info
        # 3. edit the embed to show the plugin_info
        # 4. configure the confirm button
        # 5. unlock the confirm button
        pass

    def confirm(self):
        # TODO: complete
        # 1. create and run the new task
        # 2. add the task to tasks collection
        # 3. edit the embed to inform that task was added
        # 4. remove all the buttons
        pass
