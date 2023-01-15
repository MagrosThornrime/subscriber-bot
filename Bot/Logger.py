import discord as dc

from Bot.GuildCommandHandler import GuildCommandHandler


class Logger:
    def __init__(self, guild: dc.Guild):
        self.guild = guild

    def init_handler(self, handler: GuildCommandHandler):
        pass
