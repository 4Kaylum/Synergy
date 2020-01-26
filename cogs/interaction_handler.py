import re as regex

import discord
from discord.ext import commands

from cogs import utils


class InteractionHandler(utils.Cog):

    ARGUMENT_REPLACEMENT_REGEX = regex.compile(r"%(author|user(\d+)?)")

    @utils.Cog.listener("on_command_error")
    async def custom_command_listener(self, ctx:utils.Context, error:commands.CommandError):
        """Catch command error, look to see if it's a custom, respond accordingly"""

        # Make sure we need to care
        if not isinstance(error, commands.CommandNotFound):
            return

        # Check responses
        command_name = ctx.invoked_with.lower()
        async with self.bot.database() as db:
            response = await db("SELECT command_names.command_name, command_responses.response FROM command_responses, command_names WHERE command_responses.guild_id=command_names.guild_id AND (command_responses.command_name=$1 OR $1=ANY(command_names.aliases)) AND command_responses.guild_id=$2 ORDER BY RANDOM() LIMIT 1", command_name, ctx.guild.id)
        if not response:
            return

        # Invoke command
        metacommand: utils.Command = self.bot.get_command('interaction_response_metacommand')
        ctx.command = metacommand
        ctx.response = response
        try:
            await ctx.command.invoke_ignoring_meta(ctx)  # This converts the args for me, which is nice
        except commands.CommandError as e:
            self.bot.dispatch("command_error", ctx, e)

    @commands.command(cls=utils.Command, hidden=True)
    @utils.checks.meta_command()
    @commands.guild_only()
    async def interaction_response_metacommand(self, ctx:utils.Context, users:commands.Greedy[discord.Member]):
        """Handles pinging out the responses for a given interaction. Users cannot call this."""

        # Get metadata
        command_name, text = ctx.response[0]['command_name'], ctx.response[0]['response']
        async with self.bot.database() as db:
            metadata = await db("SELECT * FROM command_names WHERE command_name=$1", command_name)

        # Get command enabled
        if metadata[0]['enabled'] is False:
            raise commands.DisabledCommand()

        # Get command nsfw
        if metadata[0]['nsfw'] and ctx.channel.is_nsfw is False:
            raise commands.NSFWChannelRequired()

        # Get user amount
        max_mentions = metadata[0]['max_mentions']
        min_mentions = metadata[0]['min_mentions']
        if len(users) > max_mentions:
            return await ctx.send("You've mentioned too many users for this command.")  # TODO raise custom error
        if len(users) < min_mentions:
            return await ctx.send("You've not mentioned enough users for this command.")  # TODO raise custom error

        # Build command response
        def argument_replacer(match):
            """Replaces the argument of the group with a user mention"""

            if match.group(2):
                return users[int(match.group(2))].mention
            return ctx.author.mention

        # Output
        await ctx.send(self.ARGUMENT_REPLACEMENT_REGEX.sub(argument_replacer, text))

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
