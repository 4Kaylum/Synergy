from aiohttp.web import RouteTableDef, Request, HTTPFound, Response
import aiohttp_session
import discord

from website import utils as webutils


routes = RouteTableDef()


@routes.get('/login_redirect')
async def login(request:Request):
    """Page the discord login redirects the user to when successfully logged in with Discord"""

    await aiohttp_session.new_session(request)
    await webutils.process_discord_login(request, ['identify', 'guilds'])
    return HTTPFound(location=f'/')


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
    post_data = await request.post()
    command_names = set([(guild_id, i.rstrip('[]')) for i in post_data.keys() if i])
    command_responses = set([(guild_id, i.rstrip('[]'), o) for i, o in post_data.items()])

    # Update database babey wew
    async with request.app['database']() as db:
        await db('DELETE FROM command_names WHERE guild_id=$1', guild_id)
        await db('DELETE FROM command_responses WHERE guild_id=$1', guild_id)
        await db.conn.copy_records_to_table('command_names', records=command_names, columns=('guild_id', 'command_name'))
        await db.conn.copy_records_to_table('command_responses', records=command_responses, columns=('guild_id', 'command_name', 'response'))

    # Wew nice
    return Response(text="Success", status=201)
