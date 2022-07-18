import aiohttp
import aiofiles
import discord as dc
from discord.ext import tasks, commands
from discord.ui import Modal
import os
from dotenv import load_dotenv
import json
from dataclasses import dataclass

from plugins import Plugin, PluginArguments


@dataclass
class TaskHandlerConfig:
    """
    I want to store types of all attributes, so I chose a dataclass. Now it
    hasn't many attributes, but it will probably change in the future.
    """
    guild_id: int
    last_task_id: int


@dataclass
class TaskEntry:
    """
    All data about a task.
    """
    plugin_name: str
    period: int
    channel_name: str
    tag: str
    arguments: PluginArguments


class MessageSender:

    """
     A task returns a list of messages to send and it's passed to the guild's
     MessageSender. All these lists are stored in one bigger list.
     Only one smaller list is chosen at once and before moving to another,
     all its messages must be sent. This prevents overlapping
     of results from different tasks.
    """

    def __init__(self, guild: dc.Guild):
        self.guild = guild
        self.messages_lists = []
        self.send_messages.start()

    def put_messages(self, channel: dc.GuildChannel, messages: list[str]):
        self.messages_lists.append((channel, messages))

    @tasks.loop(seconds=1)
    async def send_messages(self):
        # may raise Forbidden if the bot doesn't have needed permissions
        # TODO: check what if you choose a voice channel
        while self.messages_lists:
            channel, messages = self.messages_lists.pop()
            for message in messages:
                await channel.send(message)


class Logger:

    """
    The TaskHandler's interface for accessing its files. It logs TaskHandler's
    attributes to the first file, its tasks' data to the second one (and
    in the future all debug logs to the third one). It can also load data
    from these files if the bot starts running.
    """

    # TODO: maybe I need something like "FileSaver" and "FileLoader"...?

    def __init__(self, guild: dc.Guild):
        self.guild_id = guild.id
        self.tasks_file = f"data/{guild.id}-tasks"
        self.config_file = f"data/{guild.id}-conf"
        self.log_all_tasks.start()
        self.log_configuration.start()

    @tasks.loop(hours=1)
    async def log_config(self):
        config = TaskHandlerConfig(guild_id, last_task_id)
        text = json.dumps(config, indent=2)
        async with aiofiles.open(self.configuration_file, mode="w") as f:
            await f.write(text)

    @tasks.loop(hours=1)
    async def log_all_tasks(self, tasks_data: dict[int, TaskEntry]):
        text = json.dumps(tasks_data, indent=2)
        async with aiofiles.open(self.tasks_file, mode="w") as f:
            await f.write(text)        

    def get_config(self) -> TaskHandlerConfig:
        with open(self.config_file, "r") as f:
            config = json.load(f)
        return config


class TaskHandler:

    """
    CRUD-like interface for handling tasks. A task has to return a list of
    messages and they have to be prepared for sending on Discord.
    """

    # TODO: if I want the bot to be pluggable, I need to raise some exceptions
    # if a plugin is not usable
    
    def __init__(self, guild):
        self.guild = guild
        self.last_task_id = 0
        self.tasks_data = {}
        self.tasks = {}
        self.plugin_instances = {}
        self.plugins = {}
        self.sender = MessageSender(guild)
        self.logger = Logger(guild)
        self.load_config(self.logger.get_config())

    def load_config(self, config: TaskHandlerConfig):
        # TODO: po co mi to?
        self.last_task_id = config.last_task_id

    def __find_plugin(self, name: str) -> callable:
        if name not in self.plugins:
            plugin = Plugin.get_children()[name]
            self.plugins[name] = plugin
        return plugin

    async def __create_plugin_instance(self, ctx: commands.Context,
                                                plugin_name: str):
        plugin_cls = self.__find_plugin(plugin_name)
        try:
            plugin = plugin_cls()
        except TypeError:
            modal = plugin_cls.modal()
            await ctx.send_modal(modal)
            arguments = modal.arguments()
            plugin = plugin_cls(arguments)
        return plugin

    async def __add_mentions(self):
        pass

    async def __register_task(self, task_id: int,
                                task_entry: TaskEntry, 
                                plugin_instance: Plugin,
                                task: tasks.Loop):
        self.tasks_data[task_id] = task_entry
        self.plugin_instances[task_id] = plugin_instance
        self.tasks[task_id] = new_task

    async def create_task(self, ctx, plugin_name, period, tag):

        @tasks.loop(seconds=period)
        async def new_task(plugin, channel):
            messages = await plugin.get_messages()
            self.sender.put_messages(channel, messages)

        task_id = self.last_task_id
        plugin = await self.__create_plugin_instance(ctx, plugin_name)
        new_task.start(plugin, ctx.channel)

        arguments = plugin.arguments
        entry = TaskEntry(plugin_name, period, ctx.channel.name, arguments)
        await self.__register_task(task_id, entry, plugin_instance, task)
        await self.logger.log_config()
        await self.logger.log_all_tasks(self.task_data)
        self.last_task_id += 1

    def edit_task(self):
        # TODO: load the task's data, end the task, delete it, then create
        # a new task with modified data
        pass

    async def delete_task(self, task_id):
        self.tasks[task_id].stop()
        del self.tasks[task_id]
        del self.tasks_data[task_id]
        del self.plugins[task_id]
        await self.logger.log_all_tasks()

    def list_tasks(self):
        return json.dumps(self.tasks_data, indent=2)

    async def run_task(self, task_id):
        # may be called if you are too impatient and don't want to wait
        plugin = self.plugins[task_id]
        channel_name = self.tasks_data[task_id]["channel"]
        # TODO: co z tym channel?
        channel = dc.utils.get(self.guild.channels, name=channel_name)
        await self.tasks[task_id](plugin, channel)


class TaskCommands(commands.Cog):

    """
    The bot's listeners to the task-related commands. They are grouped with
    a dict with TaskHandlers.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.task_handlers = {}

    def get_handler(self, guild: dc.Guild) -> TaskHandler:
        if guild.id not in self.task_handlers:
            self.task_handlers[guild.id] = TaskHandler(guild)
        return self.task_handlers[guild.id]


    @commands.slash_command()
    async def create_task(self, ctx: commands.Context, plugin: str,
                            period: int, channel: str, tag: str):
        handler = self.get_handler(ctx.guild)
        await handler.create_task(plugin, int(period), channel, tag)
        await ctx.respond("Task created")

    @commands.slash_command()
    async def delete_task(self, ctx: commands.Context, task_id: int):
        handler = self.get_handler(ctx.guild)
        try:
            await handler.delete_task(int(task_id))
            await ctx.respond("Task deleted")
        except IndexError:
            await ctx.respond("Index out of range!")

    @commands.slash_command()
    async def list_tasks(self, ctx: commands.Context):
        handler = self.get_handler(ctx.guild)
        bot_tasks = handler.list_tasks()
        await ctx.respond(bot_tasks)


class BotUtilities(commands.Cog):

    """
    Some other commands and events, useful for debugging.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def clean_up(self, ctx: commands.Context, limit: int):
        await ctx.respond("Messages will be cleaned")
        async for message in ctx.channel.history(limit=limit):
            await message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot connected - {bot.user}")
        print(bot.guilds)


if __name__ == "__main__":
    bot = commands.Bot(debug_guilds=[868754530639171594,])
    bot.add_cog(TaskCommands(bot))
    bot.add_cog(BotUtilities(bot))
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
