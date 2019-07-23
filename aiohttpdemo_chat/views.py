import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web
import asyncio
from json import loads

log = logging.getLogger(__name__)

trusted = ['192.168.16.5', '127.0.0.1']

def get_true_remote(request):
  log.info("rem %s", repr(request.remote))
  if request.remote in trusted and 'X-Forwarded-For' in request.headers:
    fw = request.headers['X-Forwarded-For']
    log.info("fwd %s", repr(fw))
    fw = [x.strip() for x in fw.split(',')]
    while len(fw) > 1 and fw[-1] in trusted:
      del fw[-1]
    return fw[-1]
  else:
    return request.remote

async def index(request):
    #print(request.__dict__)
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
    rmt = get_true_remote(request)
    log.info('%s joined from %s.', name, rmt)

    await dbrun(db.log_login, nameid, rmt)

    await ws_current.send_json({'action': 'connect', 'name': name, 'num_users': len(request.app['websockets'])+1})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name, 'num_users': len(request.app['websockets'])+1})
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            jmsg = loads(msg.data)
            msgid = jmsg['msgid']
            msgtext = jmsg['text']
            log.info('Message %d from %s: %s', msgid, name, msgtext)
            await dbrun(db.log_message, nameid, msgtext)
            await nn.put('default', msgtext)
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': name, 'text': msgtext, 'is_bot': False})
            await ws_current.send_json({'action': 'send_confirm', 'id': msgid})
            request.app['bot_responded'] = False
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name, 'num_users': len(request.app['websockets'])})

    return ws_current
