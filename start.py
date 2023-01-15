import os

from discord.ext.commands import Bot
from dotenv import load_dotenv

from Bot.TaskCommands import TaskCommands
from ViewTests.ButtonRoleCog import ButtonRoleCog
from ViewTests.ColourCog import ColourCog
from ViewTests.TicTacToe import TicTacToeCog

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    bot = Bot(debug_guilds=[868754530639171594])
    bot.add_cog(TaskCommands(bot))

    # TODO: delete test Cogs
    bot.add_cog(ButtonRoleCog(bot))
    bot.add_cog(ColourCog(bot))
    bot.add_cog(TicTacToeCog(bot))

    bot.run(token)
