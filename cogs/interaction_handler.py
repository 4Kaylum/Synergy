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
            user = await commands.MemberConverter().convert(ctx, matches.group(1))
        except commands.CommandError as e:
            print(e)
            return

        # Output
        text = responses[0]['response']
        await ctx.send(text.replace(r"%author", ctx.author.mention).replace(r"%user", user.mention))

    @commands.command(cls=utils.Command, enabled=False)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def addcommand(self, ctx:utils.Context, name:str):
        """Adds a custom command to your guild, which you can then add responses to"""

        # Validate name
        if name.count(' ') > 0:
            return await ctx.send("Your custom command can only be one word.")
        if len(name) > 30:
            return await ctx.send("Your custom command can only be 30 characters long.")

        # Cache command
        guild_commands = self.bot.custom_commands[ctx.guild.id]
        if name.lower() in guild_commands:
            return await ctx.send("Your custom command already exists.")
        guild_commands[name.lower()]

        # Database command
        async with self.bot.database() as db:
            await db("INSERT INTO command_names (guild_id, command_name) VALUES ($1, $2)", ctx.guild.id, name.lower())

        # Done
        await ctx.send(f"Added `{name.lower()}` as a custom command to your guild.")

    @commands.command(cls=utils.Command, enabled=False)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def addresponse(self, ctx:utils.Context, name:str, *, response:str):
        """Adds a response to your custom command"""

        # Validate name
        guild_commands = self.bot.custom_commands[ctx.guild.id]
        if name not in guild_commands:
            return await ctx.send(f"The custom command `{name.lower()}` doesn't exist for your guild - make it with the `addcommand` command.")
        if name.count(' ') > 0:
            return await ctx.send("Your custom command can only be one word.")
        if len(name) > 30:
            return await ctx.send("Your custom command can only be 30 characters long.")

        # Add to cache
        self.bot.custom_commands[ctx.guild.id][name.lower()].append(response)

        # Database
        async with self.bot.database() as db:
            await db("INSERT INTO command_responses (guild_id, command_name, response) VALUES ($1, $2, $3)", ctx.guild.id, name.lower(), response)

        # Done
        await ctx.send(f"Added `{response}` to the response list for the `{name.lower()}` command.")

    @commands.command(cls=utils.Command, enabled=False)
    @commands.guild_only()
    async def interactions(self, ctx:utils.Context):
        """Lists all the interactions that are registered for your server"""

        guild_commands = self.bot.custom_commands[ctx.guild.id]
        await ctx.send('\n'.join([f"`{i}` command - `{len(o)}` responses" for i, o in guild_commands.items()]))

    @commands.command(cls=utils.Command, enabled=False)
    @commands.guild_only()
    async def responses(self, ctx:utils.Context, name:str):
        """Lists all the responses for a given interaction"""

        guild_commands = self.bot.custom_commands[ctx.guild.id]
        if name.lower() not in guild_commands:
            return await ctx.send(f"The custom command `{name.lower()}` doesn't exist for this guild.")
        await ctx.send('* ' + '\n* '.join([i for i in guild_commands[name.lower()]]))


def setup(bot:utils.CustomBot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
