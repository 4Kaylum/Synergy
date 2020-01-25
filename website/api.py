from aiohttp.web import Request, RouteTableDef, json_response

routes = RouteTableDef()


@routes.get("/api/v1/interactions")
async def get_interactions_endpoint(request:Request):
    """Returns a list of interactions and responses from the server"""

    # Get params
    command_name = request.query.get('command_name', None)
    try:
        limit = int(request.query.get('limit', '10'))
    except ValueError:
        return json_response([], status=400)
    if limit > 50:
        limit = 50
    if limit <= 0:
        limit = 10

    # Get data
    async with request.app['database']() as db:
        if command_name:
            data = await db(
                "SELECT command_name, response FROM command_responses WHERE command_name=$1 ORDER BY RANDOM() LIMIT $2",
                command_name, limit,
            )
        else:
            data = await db(
                "SELECT command_name, response FROM command_responses ORDER BY RANDOM() LIMIT $1",
                limit,
            )

    # Return data
    return json_response([{'command_name': i['command_name'], 'response': i['response']} for i in data])
