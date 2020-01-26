import re as regex
import collections

import aiohttp_session
import discord
from aiohttp.web import HTTPFound, Request, RouteTableDef, Response

from website import utils as webutils

routes = RouteTableDef()


@routes.get('/login_redirect')
async def login(request:Request):
    """Page the discord login redirects the user to when successfully logged in with Discord"""

    await webutils.process_discord_login(request, ['identify', 'guilds'])
    return HTTPFound(location=f'/')


@routes.get('/login_redirect/guilds')
async def guild_login(request:Request):
    """Page the discord login redirects the user to when successfully logged in with Discord"""

    guild_id = request.query.get('guild_id')
    return HTTPFound(location=f'/guilds/{guild_id}')


@routes.get('/logout')
async def logout(request:Request):
    """Clears your session cookies"""

    session = await aiohttp_session.get_session(request)
    session.invalidate()
    return HTTPFound(location=f'/')


@routes.post('/guilds/{guild_id}/update_custom_commands')
async def update_custom_commands(request:Request):
    """Copy the given data into the database as necessary"""

    # Validate guild ID
    try:
        guild_id = int(request.match_info['guild_id'])
    except ValueError:
        return Response(text="Failure", status=401)

    # Make sure we're logged in
    session = await aiohttp_session.get_session(request)
    if session.new:
        return Response(text="Failure", status=401)

    # Make sure we can be here
    if session['user_id'] not in request.app['config']['owners']:
        user_guilds = await webutils.get_user_guilds(request)
        guild_info = [i for i in user_guilds if guild_id == i['id'] and discord.Permissions(i['permissions']).manage_messages],
        if not guild_info:
            return Response(text="Failure", status=401)

    # Get and fix up data
    post_data = await request.post()

    # Fix metadata
    working_command_data = collections.defaultdict(dict)
    for key, value in post_data.items():
        if not key.startswith('metadata'):
            continue
        match = regex.search(r"(.+?)(\[(.*?)\])(\[(.*)\])", key)
        working_command_data[match.group(3)][match.group(5)] = value
    command_data = set([(guild_id, key, i['enabled'] == 'true', i['nsfw'] == 'true', int(i['minMentions']), int(i['maxMentions']), tuple(o.strip() for o in i['aliases'].split(','))) for key, i in working_command_data.items()])

    # Fix commands
    working_response_data = collections.defaultdict(list)
    for key, value in post_data.items():
        if not key.startswith('responses'):
            continue
        match = regex.search(r"(.+?)(\[(.*?)\])\[\]", key)
        working_response_data[match.group(3)].append(value)
    command_responses = []
    for key, value in working_response_data.items():
        for line in value:
            command_responses.append((guild_id, key, line))
    command_responses = set(command_responses)

    # Update database babey wew
    async with request.app['database']() as db:
        await db('DELETE FROM command_names WHERE guild_id=$1', guild_id)
        await db('DELETE FROM command_responses WHERE guild_id=$1', guild_id)
        await db.conn.copy_records_to_table('command_names', records=command_data, columns=('guild_id', 'command_name', 'enabled', 'nsfw', 'min_mentions', 'max_mentions', 'aliases'))
        await db.conn.copy_records_to_table('command_responses', records=command_responses, columns=('guild_id', 'command_name', 'response'))

    # Wew nice
    return Response(text="Success", status=201)
