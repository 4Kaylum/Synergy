import functools

import aiohttp_session
from aiohttp.web import HTTPFound, Request


def add_output_args():
    """This function is a wrapper around all routes. It takes the output and
    adds the user info and request to the returning dictionary
    It must be applied before the template decorator"""

    def inner_wrapper(func):
        """An inner wrapper so I can get args at the outer level"""

        @functools.wraps(func)
        async def wrapper(request:Request):
            """This is the wrapper that does all the heavy lifting"""

            # Run function
            data = await func(request)

            # See if we return anything other than data (like redirects)
            if isinstance(data, HTTPFound):
                if data.location == "/discord_oauth_login":
                    session = await aiohttp_session.get_session(request)
                    if 'redirect_on_login' not in session:
                        session['redirect_on_login'] = str(request.url)
            if not isinstance(data, dict):
                return data

            # See if we need to get rid of them
            session = await aiohttp_session.get_session(request)
            login_redirect = session.pop('redirect_on_login', None)
            if login_redirect:
                return HTTPFound(location=login_redirect)

            # Update jinja params
            if data is None:
                data = dict()
            data.update({'session': session})
            if 'user_info' not in data:
                try:
                    data.update({'user_info': session['user_info']})
                except KeyError:
                    data.update({'user_info': None})
            if 'request' not in data:
                data.update({'request': request})

            # Get bot application image if we need to
            if not request.app.get('logo_url'):
                appinfo = await request.app['bot'].application_info()
                logo_url = str(appinfo.icon_url)
                request.app['logo_url'] = logo_url
            data.update({'logo_url': request.app['logo_url']})

            return data
        return wrapper
    return inner_wrapper
