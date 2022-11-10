import discord as dc


class Task:
    def __init__(self, tag: str, channel: dc.TextChannel, period: int,
                 first_run: datetime, counter: int, plugin: Plugin):
        self.tag = tag
        self.channel = channel
        self.period = period
        self.first_run = first_run
        self.counter = counter
        self.plugin = plugin