import collections

import aiohttp_session
import asyncpg
import discord
from aiohttp.web import HTTPFound, Request, RouteTableDef
from aiohttp_jinja2 import template

from website import utils as webutils

routes = RouteTableDef()


@routes.get("/")
@template('index.j2')
@webutils.add_output_args()
async def index(request:Request):
    """Index of the website"""

    return {}


@routes.get("/marketplace")
@template('marketplace.j2')
@webutils.add_output_args()
async def marketplace(request:Request):
    """The marketplace for the bot - lists commands and responses"""

    return {}


@routes.get("/guilds")
@template('guild_picker.j2')
@webutils.add_output_args()
async def guild_picker(request:Request):
    """The guild picker page for the user"""

    # Check session age
    session = await aiohttp_session.get_session(request)
    if session.new:
        return HTTPFound(location='/discord_oauth_login')

    # Return information
    user_guilds = await webutils.get_user_guilds(request)
    return {
        'user_guilds': [i for i in user_guilds if discord.Permissions(i['permissions']).manage_messages],
    }


@routes.get("/guilds/{guild_id}")
@template('guild_settings.j2')
@webutils.add_output_args()
async def guild_settings(request:Request):
    """General guild settings page"""

    # Validate guild ID
    try:
        guild_id = int(request.match_info['guild_id'])
    except ValueError:
        return HTTPFound(location='/guilds')

    # Check session age
    session = await aiohttp_session.get_session(request)
    if session.new:
        return HTTPFound(location='/discord_oauth_login')

    # Check user permissions
    if session['user_id'] not in request.app['config']['owners']:
        user_guilds = await webutils.get_user_guilds(request)
        guild_info = [i for i in user_guilds if guild_id == i['id'] and discord.Permissions(i['permissions']).manage_messages],
        if not guild_info:
            return HTTPFound(location='/guilds')

    # Get guild object for in case I force my way in here
    try:
        guild_object = await request.app['bot'].fetch_guild(guild_id)
    except discord.Forbidden:
        return HTTPFound(location=request.app['bot'].get_invite_link(guild_id=guild_id, redirect_uri="https://synergy.voxelfox.co.uk/login_redirect/guilds", read_messages=True))

    return {
        'guild': guild_object
    }


@routes.get("/guilds/responses/{guild_id}")
@template('guild_responses.j2')
@webutils.add_output_args()
async def guild_responses(request:Request):
    """The guild picker page for the user"""

    # Validate guild ID
    try:
        guild_id = int(request.match_info['guild_id'])
    except ValueError:
        return HTTPFound(location='/guilds')

    # Check session age
    session = await aiohttp_session.get_session(request)
    if session.new:
        return HTTPFound(location='/discord_oauth_login')

    # Check user permissions
    if session['user_id'] not in request.app['config']['owners']:
        user_guilds = await webutils.get_user_guilds(request)
        guild_info = [i for i in user_guilds if guild_id == i['id'] and discord.Permissions(i['permissions']).manage_messages],
        if not guild_info:
            return HTTPFound(location='/guilds')

    # Get guild object for in case I force my way in here
    try:
        guild_object = await request.app['bot'].fetch_guild(guild_id)
    except discord.Forbidden:
        return HTTPFound(location=request.app['bot'].get_invite_link(guild_id=guild_id, redirect_uri="https://synergy.voxelfox.co.uk/login_redirect/guilds", read_messages=True))

    # Get interaction info
    interactions = collections.defaultdict(list)
    metadata = {}
    async with request.app['database']() as db:
        command_responses = await db('SELECT command_name, response FROM command_responses WHERE guild_id=$1 ORDER BY response ASC', guild_id)
        command_metadata = await db('SELECT * FROM command_names WHERE guild_id=$1', guild_id)
    for response in command_responses:
        interactions[response['command_name']].append(response['response'])
    for row in command_metadata:
        metadata[row['command_name']] = {
            'enabled': row['enabled'],
            'nsfw': row['nsfw'],
            'min_mentions': row['min_mentions'],
            'max_mentions': row['max_mentions'],
            'aliases': ','.join(row['aliases']),
        }

    # Send data back to page
    return {
        'guild': guild_object,
        'interactions': interactions,
        'metadata': metadata,
        'highlight': request.query.get('highlight'),
    }


@routes.get("/copy_to_guild")
@template('copy_to_guild.j2')
@webutils.add_output_args()
async def copy_to_guild(request:Request):
    """Copies data to a guild of yours"""

    # Check session age
    session = await aiohttp_session.get_session(request)
    if session.new:
        return HTTPFound(location='/discord_oauth_login')

    # Build data
    query_data = collections.defaultdict(list)
    for i, o in request.query.items():
        query_data[i].append(o)
    output_data = []
    for i, o in zip(query_data['command'], query_data['response']):
        output_data.append((i, o))

    # Return information
    user_guilds = await webutils.get_user_guilds(request)
    return {
        'user_guilds': [i for i in user_guilds if discord.Permissions(i['permissions']).manage_messages],
        'query_data': output_data,
    }


@routes.get("/copy_to_guild/{guild_id}")
async def copy_to_guild_redirect(request:Request):
    """Copies data to the guild and then redirects to its settings page"""

    # Validate guild ID
    try:
        guild_id = int(request.match_info['guild_id'])
    except ValueError:
        return HTTPFound(location='/guilds')

    # Check session age
    session = await aiohttp_session.get_session(request)
    if session.new:
        return HTTPFound(location='/discord_oauth_login')

    # Check user permissions
    if session['user_id'] not in request.app['config']['owners']:
        user_guilds = await webutils.get_user_guilds(request)
        guild_info = [i for i in user_guilds if guild_id == i['id'] and discord.Permissions(i['permissions']).manage_messages],
        if not guild_info:
            return HTTPFound(location='/guilds')

    # Build data
    query_data = collections.defaultdict(list)
    for i, o in request.query.items():
        query_data[i].append(o)
    output_data = []
    for i, o in zip(query_data['command'], query_data['response']):
        output_data.append((i, o))

    # Save data
    async with request.app['database']() as db:
        for command, response in output_data:
            try:
                await db('INSERT INTO command_names (guild_id, command_name) VALUES ($1, $2)', guild_id, command)
            except asyncpg.UniqueViolationError:
                pass
            try:
                await db('INSERT INTO command_responses (guild_id, command_name, response) VALUES ($1, $2, $3)', guild_id, command, response)
            except asyncpg.UniqueViolationError:
                pass

    # Redirect
    return HTTPFound(location=f"/marketplace")


@routes.get("/discord_oauth_login")
async def login(request:Request):
    """A redirect to the login page"""

    login_url = webutils.get_discord_login_url(
        request,
        redirect_uri="https://synergy.voxelfox.co.uk/login_redirect",
        oauth_scopes=['identify', 'guilds'],
    )
    return HTTPFound(location=login_url)


@routes.get("/logout")
async def logout(request:Request):
    """Index of the website"""

    session = await aiohttp_session.get_session(request)
    session.invalidate()
    return HTTPFound(location='/')
