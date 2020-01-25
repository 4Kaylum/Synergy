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
        metacommand: utils.Command = self.bot.get_command('interaction_response_metacommand')
        ctx.command = metacommand
        ctx.responses = responses
        await self.bot.invoke(ctx)

    @commands.command(cls=utils.Command, hidden=True)
    @commands.guild_only()
    async def interaction_response_metacommand(self, ctx:utils.Context):
        """Handles pinging out the responses for a given interaction. Users cannot call this."""

        # Make sure that my users aren't bein fuckin dumb
        if ctx.invoked_with.lower() == 'interaction_response_metacommand':
            return  # :/

        # Find the user mentioned in the message
        matches = regex.search(f"(?:{ctx.invoked_with} )(.*)", ctx.message.content)
        if not matches:
            raise utils.errors.MissingRequiredArgumentString('user')
        user = await commands.MemberConverter().convert(ctx, matches.group(1).split(' ')[0])

        # Output
        text = ctx.responses[0]['response']
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
