import aiohttp
import aiofiles
import discord as dc
from discord.ext import tasks, commands
from discord.ui import Modal
import os
from dotenv import load_dotenv
from dataclasses import dataclass, asdict, fields
import json

from plugins import Plugin, PluginArguments


@dataclass
class TaskHandlerConfig:
    """
    I want to store types of all attributes, so I chose a dataclass. Now it
    hasn't many attributes, but it will probably change in the future.
    """
    guild_id: int


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

    def put_messages(self, channel: dc.TextChannel, messages: list[str]):
        self.messages_lists.append((channel, messages))

    @tasks.loop(seconds=1)
    async def send_messages(self):
        # may raise Forbidden if the bot doesn't have needed permissions
        while self.messages_lists:
            channel, messages = self.messages_lists.pop()
            for message in messages:
                await channel.send(message)


class Logger:

    """
    The TaskHandler's interface for accessing its log files. It logs TaskHandler's
    attributes to the first file, its tasks' data to the second one (and
    in the future all debug logs to the third one). It can also load logs.
    """

    def __init__(self, guild: dc.Guild):
        self.guild = guild
        self.tasks_file = f"data/{guild.id}-tasks"
        self.config_file = f"data/{guild.id}-conf"
        self.config = self.get_config()
        self.tasks_data = self.get_tasks_data()
        self.log_all_tasks.start()
        self.log_config.start()

    @tasks.loop(hours=1)
    async def log_config(self):
        text = json.dumps(asdict(self.config), indent=2)
        async with aiofiles.open(self.config_file, mode="w") as f:
            await f.write(text)

    @tasks.loop(hours=1)
    async def log_all_tasks(self):
        prepared = []
        for entry in self.tasks_data:
            entry_dict = {}
            for field in fields(entry):
                if field.name != "arguments":
                    entry_dict[field.name] = getattr(entry, field.name)
            arguments = asdict(entry.arguments)
            entry_dict["arguments"] = arguments
            prepared.append(entry_dict)
        text = json.dumps(prepared, indent=2)
        async with aiofiles.open(self.tasks_file, mode="w") as f:
            await f.write(text)        

    def get_config(self) -> TaskHandlerConfig:
        try:
            with open(self.config_file, "r") as f:
                config_dict = json.load(f)
                config = TaskHandlerConfig(**config_dict)
        except FileNotFoundError:
            config = TaskHandlerConfig(self.guild.id)
        return config

    def get_tasks_data(self) -> list[TaskEntry]:
        try:
            tasks_data = []
            with open(self.tasks_file, "r") as f:
                tasks_loaded = json.load(f)
            for task in tasks_loaded:
                plugin_name = task["plugin_name"]
                plugin_cls = Plugin.get_children()[plugin_name]
                arguments_dict = task["arguments"]
                arguments = plugin_cls.arguments_cls(**arguments_dict)
                task["arguments"] = arguments
                tasks_data.append(TaskEntry(**task))
        except FileNotFoundError:
            tasks_data = []
        return tasks_data

class TaskHandler:

    """
    CRUD-like interface for handling tasks. A task has to return a list of
    messages and they have to be prepared for sending on Discord.
    """

    # TODO: if I want the bot to be pluggable, I need to raise some exceptions
    # if a plugin is not usable
    
    def __init__(self, guild: dc.Guild):
        self.guild = guild
        self.sender = MessageSender(guild)
        self.logger = Logger(guild)
        self.config = self.logger.config
        self.tasks_data = self.logger.tasks_data
        self.tasks = []
        self.plugin_instances = []

    async def __plugin_with_modal(self, ctx: commands.Context,
                                plugin_name: str) -> Plugin:
        plugin_cls = Plugin.get_children()[plugin_name]
        try:
            plugin = plugin_cls()
        except TypeError:
            modal = plugin_cls.modal()
            await ctx.send_modal(modal)
            await modal.wait()
            arguments = modal.arguments
            plugin = plugin_cls(arguments)
        return plugin

    async def __plugin_with_logs(self, task_entry: TaskEntry) -> Plugin:
        plugin_cls = Plugin.get_children()[task_entry.plugin_name]
        try:
            plugin = plugin_cls()
        except TypeError:
            arguments = task_entry.arguments
            plugin = plugin_cls(arguments)
        return plugin

    async def __add_mentions(self):
        # TODO: add mentions to TaskEntry (and a title, but maybe in another
        # function)
        # They will be appended to the first message in messages list
        pass

    async def __register_task(self, plugin: Plugin, period: int, tag: str,
                            channel_name: str):
        arguments = plugin.arguments
        plugin_name = type(plugin).__name__
        entry = TaskEntry(plugin_name, period, channel_name, tag, arguments)
        self.tasks_data.append(entry)
        await self.logger.log_all_tasks()        

    async def __create_task(self, plugin: Plugin, period: int,
                            tag: str, channel: dc.TextChannel):

        @tasks.loop(seconds=period)
        async def new_task(plugin: Plugin, channel: dc.TextChannel):
            messages = await plugin.get_messages()
            self.sender.put_messages(channel, messages)

        new_task.start(plugin, channel)
        
        self.plugin_instances.append(plugin)
        self.tasks.append(new_task)

    async def __create_from_logs(self, entry: TaskEntry):
        plugin = await self.__plugin_with_logs(entry)
        channel = dc.utils.get(self.guild.channels, name=entry.channel_name)
        await self.__create_task(plugin, entry.period, entry.tag, channel)

    async def load_tasks(self):
        for task_entry in self.tasks_data:
            await self.__create_from_logs(task_entry)

    async def create_from_command(self, ctx: commands.Context,
                                plugin_name: str, period: int, tag: str):
        plugin = await self.__plugin_with_modal(ctx, plugin_name)
        await self.__create_task(plugin, period, tag, ctx.channel)
        await self.__register_task(plugin, period, tag, ctx.channel.name)

    def edit_task(self):
        # TODO: load the task's data, end the task, delete it, then create
        # a new task with modified data
        pass

    async def delete_task(self, task_id: int):
        self.tasks[task_id].stop()
        del self.tasks[task_id]
        del self.tasks_data[task_id]
        del self.plugin_instances[task_id]
        await self.logger.log_all_tasks()

    def list_tasks(self):
        # TODO: parse the dictionary (it's so ugly...)
        return self.logger.get_tasks_data()

    async def run_task(self, task_id: int):
        # may be called if you are too impatient and don't want to wait
        plugin = self.plugins[task_id]
        channel_name = self.tasks_data[task_id].channel_name
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

    async def get_handler(self, guild: dc.Guild) -> TaskHandler:
        if guild.id not in self.task_handlers:
            self.task_handlers[guild.id] = TaskHandler(guild)
            await self.task_handlers[guild.id].load_tasks()
        return self.task_handlers[guild.id]


    @commands.slash_command()
    async def create_task(self, ctx: commands.Context, plugin: str,
                                            period: int, tag: str):
        handler = await self.get_handler(ctx.guild)
        await handler.create_from_command(ctx, plugin, int(period), tag)
        await ctx.respond("Task created")

    @commands.slash_command()
    async def delete_task(self, ctx: commands.Context, task_id: int):
        handler = await self.get_handler(ctx.guild)
        try:
            await handler.delete_task(int(task_id))
            await ctx.respond("Task deleted")
        except IndexError:
            await ctx.respond("Index out of range!")

    @commands.slash_command()
    async def list_tasks(self, ctx: commands.Context):
        handler = await self.get_handler(ctx.guild)
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
        # rewrite it for speed and duplicate
        # for deleting only debugging messages
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