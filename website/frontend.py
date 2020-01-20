import collections

from aiohttp.web import RouteTableDef, Request, HTTPFound
from aiohttp_jinja2 import template
import aiohttp_session
import discord

from website import utils as webutils


routes = RouteTableDef()


@routes.get("/")
@template('index.j2')
@webutils.add_output_args()
async def index(request:Request):
    """Index of the website"""

    return {}


@routes.get("/guilds")
@template('guild_picker.j2')
@webutils.add_output_args()
async def guild_picker(request:Request):
    """The guild picker page for the user"""

    # Check session age
    session = await aiohttp_session.get_session(request)
    if session.new:
        return HTTPFound(location='/')

    # Return information
    user_guilds = await webutils.get_user_guilds(request)
    return {
        'user_guilds': [i for i in user_guilds if discord.Permissions(i['permissions']).manage_messages],
    }


@routes.get("/guilds/{guild_id}")
@template('guild_settings.j2')
@webutils.add_output_args()
async def guild_settings(request:Request):
    """The guild picker page for the user"""

    # Validate guild ID
    try:
        guild_id = int(request.match_info['guild_id'])
    except ValueError:
        return HTTPFound(location='/guilds')

    # Check session age
    session = await aiohttp_session.get_session(request)
    if session.new:
        return HTTPFound(location='/')

    # Check user permissions
    if session['user_id'] not in request.app['config']['owners']:
        user_guilds = await webutils.get_user_guilds(request)
        guild_info = [i for i in user_guilds if guild_id == i['id'] and discord.Permissions(i['permissions']).manage_messages],
        if not guild_info:
            return HTTPFound(location='/guilds')

    # Get guild object for in case I force my way in here
    guild_object = await request.app['bot'].fetch_guild(guild_id)

    # Get interaction info
    interactions = collections.defaultdict(list)
    async with request.app['database']() as db:
        command_info = await db('SELECT command_name FROM command_names WHERE guild_id=$1', guild_id)
        command_responses = await db('SELECT command_name, response FROM command_responses WHERE guild_id=$1', guild_id)
    for command in command_info:
        interactions[command['command_name']]
    for response in command_responses:
        interactions[response['command_name']].append(response['response'])

    # Send data back to page
    return {
        'guild': guild_object,
        'interactions': interactions
    }


@routes.get("/discord_oauth_login")
async def login(request:Request):
    """Index of the website"""

    login_url = webutils.get_discord_login_url(
        request,
        redirect_uri="http://127.0.0.1:8080/login_redirect",
        oauth_scopes=['identify', 'guilds'],
    )
    return HTTPFound(location=login_url)
