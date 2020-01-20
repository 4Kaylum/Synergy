import collections
import random

from discord.ext import commands

from cogs import utils


class InteractionHandler(utils.Cog):
    """ Each entry in _custom_commands will look like this:
    {
        "command_name": {
            guild_id: "This guild's output",
            guild_id2: "This other guild's output",
        }
    }
    """

    custom_commands = collections.defaultdict(lambda: collections.defaultdict(list))  # CommandName: {GuildID: [Reponses]}

    def __init__(self, bot:utils.CustomBot):
        super().__init__(bot)
        self.custom_commands['hug']
        self.custom_commands['kiss']

    @utils.Cog.listener("on_command_error")
    async def custom_command_listener(self, ctx:utils.Context, error:commands.CommandError):
        """Catch command error, look to see if it's a custom, respond accordingly"""

        # Make sure we need to care
        if not isinstance(error, commands.CommandNotFound):
            return

        # Check responses
        command_name = ctx.invoked_with.lower()
        if command_name not in self.custom_commands:
            return
        guild_respones = self.custom_commands[command_name]
        if ctx.guild.id not in guild_respones:
            return
        responses = guild_respones[ctx.guild.id]
        await ctx.send(random.choice(responses))

    @commands.command(cls=utils.Command)
    async def addcommandresponse(self, ctx:utils.Context, name:str, *, output:str):
        """Adds a response to your custom command"""

        # TODO check the command exists
        if name not in self.custom_commands:
            return await ctx.send("Oop that's not a custom command you can add to.")
        self.custom_commands[name.lower()][ctx.guild.id].append(output)
        await ctx.send(f"Added `{output}` to the response list for the `{name.lower()}` command.")


def setup(bot:utils.CustomBot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
