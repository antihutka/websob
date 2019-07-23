import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web
import asyncio

log = logging.getLogger(__name__)

async def index(request):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)

    db = request.app['db']
    dbexec = request.app['dbexec']
    nn = request.app['nn']

    def dbrun(func, *args, **kwargs):
      return asyncio.get_event_loop().run_in_executor(dbexec, lambda: func(*args, **kwargs))

    nameid, name = await dbrun(db.get_name)
    log.info('%s joined from %s.', name, request.remote)

    await dbrun(db.log_login, nameid, request.remote)

    await ws_current.send_json({'action': 'connect', 'name': name})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name})
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()
        log.info('Message from %s: %s', name, msg.data)

        if msg.type == aiohttp.WSMsgType.text:
            await dbrun(db.log_message, nameid, msg.data)
            await nn.put('default', msg.data)
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': name, 'text': msg.data, 'is_bot': False})
            request.app['bot_responded'] = False
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current
