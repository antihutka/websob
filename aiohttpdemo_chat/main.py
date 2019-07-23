import logging

import jinja2

import aiohttp_jinja2
from aiohttp import web
from aiohttpdemo_chat.views import index
import sys
from configparser import ConfigParser
from aiohttpdemo_chat.db import WebsobDB
from aiohttpdemo_chat.httpnn import HTTPNN
import concurrent.futures
import asyncio

async def bgtask(app):
  def dbrun(func, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(app['dbexec'], lambda: func(*args, **kwargs))
  while True:
    if not app['bot_responded']:
      try:
        resp = await app['nn'].get('default')
        logging.info('sending response: %s', resp)
        await dbrun(app['db'].log_message, 0, resp)
        for ws in app['websockets'].values():
          await ws.send_json({'action': 'sent', 'name': app['botname'], 'text': resp, 'is_bot': True})
        app['bot_responded'] = True
      except:
        logging.exception('Error sending response')
    await asyncio.sleep(5)

async def init_app(cfg):

    db = WebsobDB(cfg['Database'])
    nn = HTTPNN(cfg.get('Backend', 'Url'), cfg.get('Backend', 'Keyprefix'))
    await nn.initialize()

    app = web.Application()

    app['bot_responded'] = True
    app['websockets'] = {}
    app['db'] = db
    app['dbexec'] = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    app['nn'] = nn
    app['botname'] = cfg.get('Bot', 'Name')
    app['bgtask'] = asyncio.ensure_future(bgtask(app))

    app.on_shutdown.append(shutdown)

    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('aiohttpdemo_chat', 'templates'))

    app.router.add_get('/', index)

    return app


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()
    app['bgtask'].cancel()


def main():
    logging.basicConfig(level=logging.DEBUG)

    Config = ConfigParser()
    Config.read(sys.argv[1])

    app = init_app(Config)
    web.run_app(app)


if __name__ == '__main__':
    main()
