import discord as dc
from discord.ext.commands import Cog, Bot, slash_command

from Bot.Logger import Logger
from Bot.Sender import Sender
from Bot.GuildCommandHandler import GuildCommandHandler


class TaskCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.handlers = {}
        self.loggers = {}
        self.senders = {}

    def _initialize_guild(self, guild: dc.Guild):
        if guild.id not in self.handlers:
            handler = GuildCommandHandler(guild)
            logger = Logger(guild)
            self.senders[guild.id] = Sender(guild)
            self.handlers[guild.id] = handler
            self.loggers[guild.id] = logger
            logger.init_handler(handler)

    @slash_command(description="Create a task")
    async def create_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        await self.handlers[ctx.guild.id].create_task(ctx)
        await ctx.respond("done")

    @slash_command(description="Delete a task")
    async def delete_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.handlers[ctx.guild.id].delete_task(ctx)
        await ctx.respond("done")

    @slash_command(description="List all tasks")
    async def list_tasks(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.handlers[ctx.guild.id].list_tasks(ctx)
        await ctx.respond("done")

    @slash_command(description="Edit a task")
    async def edit_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.handlers[ctx.guild.id].edit_task(ctx)
        await ctx.respond("done")

    @slash_command(description="Run a task")
    async def run_task(self, ctx: dc.ApplicationContext):
        self._initialize_guild(ctx.guild)
        self.handlers[ctx.guild.id].run_task(ctx)
        await ctx.respond("done")

    @slash_command(description="test")
    async def strtest(self, ctx: dc.ApplicationContext):
        # TODO: delete this
        await ctx.respond(ctx.channel)

        # await ctx.respond(dc.utils.format_dt(dc.utils.utcnow(), "t"))
    # @slash_command(description="Help")
    # async def help(self):
    #     TODO: /help command
    #     pass
