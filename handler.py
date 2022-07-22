import discord as dc
from discord.ext import tasks
import aiofiles
from dataclasses import dataclass, asdict, fields
import json
from collections import deque

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
        self.messages_queue = deque()
        self.__send_messages.start()

    async def __title_message(self):
        # create a message with task's tag and a list of mentions
        # append it to the start of the list of messages
        pass

    def put_messages(self, channel: dc.TextChannel, messages: list[str]):
        self.messages_queue.appendleft((channel, messages))

    @tasks.loop(seconds=1)
    async def __send_messages(self):
        # may raise Forbidden if the bot doesn't have needed permissions
        while self.messages_queue:
            channel, messages = self.messages_queue.pop()
            for message in messages:
                await channel.send(message)


class Logger:

    """
    The TaskHandler's interface for accessing its log files. It logs TaskHandler's
    attributes to the first file, its tasks' data to the second one (and
    in the future all debug logs to the third one). It can also load logs.
    """

    def __init__(self, guild: dc.Guild, tasks_data: list[TaskEntry],
                 config: TaskHandlerConfig):
        self.guild = guild
        self.tasks_file = f"data/{guild.id}-tasks"
        self.config_file = f"data/{guild.id}-conf"
        self.tasks_data = tasks_data
        self.config = config

    @tasks.loop(hours=1)
    async def log_config(self):
        text = json.dumps(asdict(self.config), indent=2)
        async with aiofiles.open(self.config_file, mode="w") as f:
            await f.write(text)

    @tasks.loop(hours=1)
    async def log_all_tasks(self):
        prepared = []
        for entry in self.tasks_data:
            entry_as_dict = {}
            for field in fields(entry):
                if field.name != "arguments":
                    entry_as_dict[field.name] = getattr(entry, field.name)
            arguments = asdict(entry.arguments)
            entry_as_dict["arguments"] = arguments
            prepared.append(entry_as_dict)
        text = json.dumps(prepared, indent=2)
        async with aiofiles.open(self.tasks_file, mode="w") as f:
            await f.write(text)

    async def get_config(self):
        try:
            async with aiofiles.open(self.config_file, "r") as f:
                text = await f.read()
            config = TaskHandlerConfig(**(json.loads(text)))
        except FileNotFoundError:
            config = TaskHandlerConfig(self.guild.id)
        self.config = config

    async def get_tasks_data(self):
        try:
            async with aiofiles.open(self.tasks_file, "r") as f:
                text = await f.read()
            tasks_loaded = json.loads(text)
            for task in tasks_loaded:
                plugin_name = task["plugin_name"]
                plugin_cls = Plugin.get_children()[plugin_name]
                arguments = plugin_cls.arguments_cls(**(task["arguments"]))
                task["arguments"] = arguments
                self.tasks_data.append(TaskEntry(**task))
        except FileNotFoundError:
            pass


class TaskHandler:
    """
    CRUD-like interface for handling tasks. A task has to return a list of
    messages and they have to be prepared for sending on Discord.
    """

    def __init__(self, guild: dc.Guild):
        self.guild = guild
        self.tasks_data = []
        self.tasks = []
        self.plugin_instances = []
        self.config = None
        self.sender = MessageSender(guild)
        self.logger = Logger(guild, self.tasks_data, self.config)

    async def __plugin_with_modal(self, ctx: dc.ApplicationContext,
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

    async def create_from_command(self, ctx: dc.ApplicationContext,
                                  plugin_name: str, period: int, tag: str,
                                  channel_name: str):
        if channel_name:
            channel = dc.utils.get(
                self.guild.channels,
                name=channel_name)
        else:
            channel = ctx.channel
        plugin = await self.__plugin_with_modal(ctx, plugin_name)
        await self.__create_task(plugin, period, tag, channel)
        await self.__register_task(plugin, period, tag, channel.name)

    async def edit_task(self, ctx: dc.ApplicationContext, id_: int,
                        plugin_name: str, period: int, tag: str,
                        channel_name: str, change_args: bool):
        entry = self.tasks_data[id_]
        plugin = self.plugin_instances[id_]
        await self.delete_task(id_)
        if plugin_name:
            entry.plugin_name = plugin_name
            change_args = True
        if period:
            entry.period = period
        if tag:
            entry.tag = tag
        if channel_name:
            entry.channel_name = channel_name
        if change_args:
            plugin = await self.__plugin_with_modal(ctx, entry.plugin_name)
        channel = dc.utils.get(self.guild.channels, name=entry.channel_name)
        await self.__create_task(plugin, entry.period, entry.tag, channel)
        await self.__register_task(plugin, entry.period, entry.tag,
                                   entry.channel_name)

    async def delete_task(self, task_id: int):
        self.tasks[task_id].stop()
        del self.tasks[task_id]
        del self.tasks_data[task_id]
        del self.plugin_instances[task_id]
        await self.logger.log_all_tasks()

    def list_tasks(self, ctx: dc.ApplicationContext):
        self.sender.put_messages(ctx.channel, [self.tasks_data, ])

    async def run_task(self, task_id: int):
        plugin = self.plugin_instances[task_id]
        channel_name = self.tasks_data[task_id].channel_name
        channel = dc.utils.get(self.guild.channels, name=channel_name)
        await self.tasks[task_id](plugin, channel)
