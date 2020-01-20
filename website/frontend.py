from aiohttp.web import RouteTableDef, Request, HTTPFound
from aiohttp_jinja2 import template
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

    try:
        user_guilds = await webutils.get_user_guilds(request)
    except KeyError:
        return HTTPFound(location="/")
    return {
        'user_guilds': [i for i in user_guilds if discord.Permissions(i['permissions']).manage_messages],
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
