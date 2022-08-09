import os

import discord as dc
from discord.commands import slash_command, Option
from discord.ext.commands import Cog, Bot
from discord.ui import Modal
from dotenv import load_dotenv

from handler import TaskHandler, TaskError


class TaskCommands(Cog):

    """
    The bot's listeners to the task-related commands. They are grouped with
    a dict with TaskHandlers.
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.task_handlers = {}

    async def __init_handler(self, guild: dc.Guild) -> TaskHandler:
        handler = TaskHandler(guild)
        await handler.logger.get_config()
        await handler.logger.get_tasks_data()
        await handler.load_tasks()
        handler.logger.log_config.start()
        handler.logger.log_all_tasks.start()
        return handler

    async def __get_handler(self, guild: dc.Guild) -> TaskHandler:
        try:
            handler = self.task_handlers[guild.id]
        except KeyError:
            self.task_handlers[guild.id] = await self.__init_handler(guild)
            handler = self.task_handlers[guild.id]
        return handler

    @slash_command(description="Create a task to subscribe a plugin")
    async def create_task(self, ctx: dc.ApplicationContext,
                          plugin: Option(str, "Enter plugin's name"),
                          period: Option(int,
                                         "The period of creating messages (in seconds)",
                                         min_value=1),
                          tag: Option(str, "Tag (name) of your task"),
                          channel: Option(str, "Where the messages will be sent?", default="")
                          ):
        handler = await self.__get_handler(ctx.guild)
        try:
            await handler.create_from_command(ctx, plugin, period, tag, channel)
        except TaskError as exception:
            await ctx.respond(exception.message)
        else:
            await ctx.respond("Task created")

    @slash_command(description="Delete a task")
    async def delete_task(self, ctx: dc.ApplicationContext,
                          task_id: Option(int, "Id of your task")
                          ):
        handler = await self.__get_handler(ctx.guild)
        try:
            await handler.delete_task(int(task_id))
            await ctx.respond("Task deleted")
        except IndexError:
            await ctx.respond("Task doesn't exist")

    @slash_command(description="List all tasks")
    async def list_tasks(self, ctx: dc.ApplicationContext):
        handler = await self.__get_handler(ctx.guild)
        handler.list_tasks(ctx)
        await ctx.respond("Here you are")

    @slash_command(description="Choose a task and edit it")
    async def edit_task(self, ctx: dc.ApplicationContext,
                        task_id: Option(int, "Id of your task"),
                        change_arguments: Option(bool, "Change plugin arguments (True/False)"),
                        plugin: Option(str, "Name of new plugin", default=""),
                        period: Option(int, "New period value", min_value=1, default=0),
                        tag: Option(str, "New tag (name) of the task", default=""),
                        channel: Option(str, "New channel name", default=""),
                        ):
        handler = await self.__get_handler(ctx.guild)
        await handler.edit_task(ctx, task_id, plugin, period,
                                tag, channel, change_arguments)
        await ctx.respond("Task edited")

    @slash_command(description="Run a task if you are impatient")
    async def run_task(self, ctx: dc.ApplicationContext,
                       task_id: Option(int, "Id of your task")
                       ):
        handler = await self.__get_handler(ctx.guild)
        await handler.run_task(task_id)
        await ctx.respond("Here you are")
    
    @Cog.listener()
    async def on_ready(self):
        print(f"Bot connected - {bot.user}")
        print(bot.guilds)
        for guild in bot.guilds:
            await self.__get_handler(guild)


class BotUtilities(Cog):

    """
    Some other commands and events, useful for debugging.
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(description="Delete all messages in channel")
    async def clean_up(self, ctx: dc.ApplicationContext,
                       limit: Option(int, "Max number of deleted messages",
                                     default=100)):
        await ctx.respond("Messages will be cleaned")
        bot_id = self.bot.user.id
        history = await ctx.channel.history(limit=limit).flatten()
        for i in range(0, len(history), 100):
            try:
                await ctx.channel.delete_messages(history[i:i + 100])
            except dc.HTTPException:
                for message in history[i:]:
                    await message.delete()
                return



if __name__ == "__main__":
    bot = Bot(debug_guilds=[868754530639171594, ])
    bot.add_cog(TaskCommands(bot))
    bot.add_cog(BotUtilities(bot))
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
