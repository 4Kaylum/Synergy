import re as regex
import collections

import aiohttp_session
import discord
from aiohttp.web import HTTPFound, Request, RouteTableDef, Response

from website import utils as webutils


routes = RouteTableDef()


def user_argument_fixer(string):
    """Fixes the arguments that the user gave for a response"""

    if r"%user" not in string:
        return string, 0
    found_indexes = sorted([int(i) if i else -1 for i in regex.findall(r"%user((?:\d+)?)", string)])
    if not found_indexes:
        return string.replace(r"%user", r"%user1"), 1
    replacements = {}
    last_used = 1
    for index in found_indexes:
        replacements[index] = last_used
        last_used += 1
    return regex.sub(r"%user((?:\d+)?)", lambda m: f"%user{replacements[int(m.group(1)) if m.group(1) else -1]}", string), max(replacements.values())


@routes.get('/login_redirect')
async def login(request:Request):
    """Page the discord login redirects the user to when successfully logged in with Discord"""

    await webutils.process_discord_login(request, ['identify', 'guilds'])
    session = await aiohttp_session.get_session(request)
    return HTTPFound(location=session.pop('redirect_on_login', '/'))


@routes.get('/login_redirect/guilds')
async def guild_login(request:Request):
    """Page the discord login redirects the user to when successfully logged in with Discord"""

    guild_id = request.query.get('guild_id')
    return HTTPFound(location=f'/guilds/{guild_id}')


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
    post_data = await request.json()

    # Fix metadata
    command_data = set([(guild_id, key, i['enabled'], i['nsfw'], int(i['minMentions'] or '1'), int(i['maxMentions'] or '1'), tuple(o.strip() for o in i['aliases'].split(',') if o.strip())) for key, i in post_data['metadata'].items()])
    command_responses = []
    for key, response_list in post_data['responses'].items():
        for text in response_list:
            if not text.strip():
                continue
            text, mention_count = user_argument_fixer(text.strip())
            command_responses.append((guild_id, key, text, mention_count))
    command_responses = set(command_responses)

    # Update database babey wew
    async with request.app['database']() as db:
        await db('DELETE FROM command_names WHERE guild_id=$1', guild_id)
        await db('DELETE FROM command_responses WHERE guild_id=$1', guild_id)
        await db.conn.copy_records_to_table('command_names', records=command_data, columns=('guild_id', 'command_name', 'enabled', 'nsfw', 'min_mentions', 'max_mentions', 'aliases'))
        await db.conn.copy_records_to_table('command_responses', records=command_responses, columns=('guild_id', 'command_name', 'response', 'user_mention_count'))

    # Wew nice
    return Response(text="Success", status=201)
