import random

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
        guild_commands = self.bot.custom_commands[ctx.guild.id]
        if command_name not in guild_commands:
            return
        guild_respones = guild_commands[command_name]
        await ctx.send(random.choice(guild_respones))

    @commands.command(cls=utils.Command)
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

    @commands.command(cls=utils.Command)
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


def setup(bot:utils.CustomBot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
