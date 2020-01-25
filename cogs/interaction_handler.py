import re as regex

from discord.ext import commands

from cogs import utils


class InteractionHandler(utils.Cog):

    @utils.Cog.listener("on_command_error")
    async def custom_command_listener(self, ctx:utils.Context, error:commands.CommandError):
        """Catch command error, look to see if it's a custom, respond accordingly"""

        # Make sure we need to care
        if not isinstance(error, commands.CommandNotFound):
            return

        # Check responses
        command_name = ctx.invoked_with.lower()
        async with self.bot.database() as db:
            responses = await db("SELECT command_responses.response FROM command_responses, command_names WHERE command_responses.guild_id=command_names.guild_id AND command_responses.command_name=$1 and command_responses.guild_id=$2 ORDER BY RANDOM()", command_name, ctx.guild.id)
        if not responses:
            return

        # Check if another user was mentioned
        matches = regex.search(f"(?:{command_name} )(.*)", ctx.message.content)
        if not matches:
            return
        try:
            user = await commands.MemberConverter().convert(ctx, matches.group(1).split(' ')[0])
        except commands.CommandError as e:
            return self.bot.dispatch("command_error", ctx, e)
            raise e  # Couldn't convert member

        # Output
        text = responses[0]['response']
        await ctx.send(text.replace(r"%author", ctx.author.mention).replace(r"%user", user.mention))

    @commands.command(cls=utils.Command)
    @commands.guild_only()
    async def interactions(self, ctx:utils.Context):
        """Lists all the interactions that are registered for your server"""

        async with self.bot.database() as db:
            guild_commands = await db("SELECT command_name, count(response) FROM command_responses WHERE guild_id=$1 GROUP BY command_name", ctx.guild.id)
        await ctx.send('\n'.join([f"`{row['command_name']}` command - `{row['count']}` responses" for row in guild_commands]))


def setup(bot:utils.Bot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
