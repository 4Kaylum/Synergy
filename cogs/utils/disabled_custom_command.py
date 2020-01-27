from discord.ext import commands


class DisabledCustomCommand(commands.DisabledCommand):
    """When a command has been disabled from the web interface"""
