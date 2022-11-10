import os

from dotenv import load_dotenv
import discord as dc
from discord.ext.commands import Bot

from Bot.Logger import Logger
from Bot.Sender import Sender
from Bot.TaskCollection import TaskCollection


class CustomBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collections = {}
        self.loggers = {}
        self.senders = {}

    def _load_token(self) -> str:
        load_dotenv()
        return os.getenv("DISCORD_TOKEN")

    def run(self):
        super().run(self._load_token())

    def _initialize_guild(self, guild: dc.Guild):
        if guild.id not in self.collections:
            self.senders[guild.id] = Sender(guild)
            self.loggers[guild.id] = Logger()
            self.collections[guild.id] = self.loggers[guild.id].init_collection()

    @slash_command(description="Create a task")
    async def create_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.collections[ctx.guild.id].create_task(ctx)

    @slash_command(description="Delete a task")
    async def delete_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.collections[ctx.guild.id].delete_task(ctx)

    @slash_command(description="List all tasks")
    async def list_tasks(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.collections[ctx.guild.id].list_tasks(ctx)

    @slash_command(description="Edit a task")
    async def edit_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.collections[ctx.guild.id].edit_task(ctx)

    @slash_command(description="Run a task")
    async def run_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.collections[ctx.guild.id].run_task(ctx)

    # @slash_command(description="Help")
    # async def help(self):
    #     TODO: /help command
    #     pass

    @self.listen
    async def on_ready(self):
        print(f"Bot connected - {self.user}")
        print(self.guilds)