# coding=UTF-8

from flask import Flask, render_template
from utils import is_local_dev_env
import asyncio
import websockets
from main import get_corridor_lut
import json
import threading

import logging
logging.basicConfig(level=logging.DEBUG)
fx_logger = logging.getLogger('fxrate')
fx_logger.setLevel(logging.INFO)

'''
Logging for websockets
'''
# logger = logging.getLogger('websockets')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/home')
def home():
    return render_template("home.html")


def message_parser(ws, message):
    result = {}
    if message == 'gettable':
        result['type'] = 'gettable'
        result['data'] = []
        lut = get_corridor_lut()
        for corridorName, enabled in lut.items():
            if enabled:
                corridor = __import__(corridorName)
                bankInfo = corridor.BANK_INFOS
                _from, _to = corridorName.split("_")
                result['data'].append((_from, _to, bankInfo))
    elif message.startswith('get_fxrate_'):
        splits = message.split('_')
        src = splits[2]
        dest = splits[3]
        threading.Thread(target=trigger_crawler, name="Crawler", args=(ws, src, dest)).start()

    return json.dumps(result)

def get_fxrate(_from, _to):
    fx_logger.info(" >>>>>> get_fxrate : {} to {}".format(_from, _to))
    moduleName = "{}_{}".format(_from, _to)
    module = __import__(moduleName)
    result = module.get_current_forex_price()
    return result

async def async_get_fx_rate(websocket, src, dest):
    rates = get_fxrate(src, dest)
    result = {}
    result['type'] = 'fxrate'
    result['src'] = src
    result['dest'] = dest
    result['data'] = rates
    fx_logger.info('{}->{}: {}'.format(src, dest, rates))
    await websocket.send(json.dumps(result))
    fx_logger.info("bye")

def trigger_crawler(websocket, src, dest):
    asyncio.run(async_get_fx_rate(websocket, src, dest))

async def message_handler(websocket, path):
    fx_logger.info("entering ... : {}".format(path))
    try:
        async for message in websocket:
            print(message)
            response = message_parser(websocket, message)
            await websocket.send(response)
    except Exception as e:
        if e.code == 1005:
            pass
        else:
            fx_logger.error(e)
    finally:
        pass
    fx_logger.info(" done ...")

def start_websocket_server():
    # Create a event loop for websocket usage
    ws_event_loop = asyncio.new_event_loop()
    # Debug mode for asyncio
    ws_event_loop.set_debug(True)

    def stop_ws_event_loop(evt_loop):
        input('<<< Press <enter> to stop >>>\n')
        fx_logger.info('Stopping websocket server ...')
        evt_loop.call_soon_threadsafe(evt_loop.stop)

    def run_ws_event_loop(evt_loop):
        # Set the websocket event loop to asyncio
        asyncio.set_event_loop(evt_loop)
        start_ws_server = websockets.serve(message_handler, 'localhost', 9487)
        try:
            evt_loop.run_until_complete(start_ws_server)
            # Run the event loop until stop() is called.
            evt_loop.run_forever()
        finally:
            evt_loop.run_until_complete(evt_loop.shutdown_asyncgens())
            evt_loop.close()
        fx_logger.info("Web socket server stopped!")

    threading.Thread(target=run_ws_event_loop, args=(ws_event_loop,), name="ws_loop").start()
    threading.Thread(target=stop_ws_event_loop, args=(ws_event_loop,)).start()

def start_app():
    if is_local_dev_env():
        start_websocket_server()
        app.run(host="0.0.0.0", debug=True, use_reloader=False)
    else:
        # For Heroku, not going to maintain for now.
        # from os import environ
        # app.run(host="0.0.0.0", debug=False, port=environ.get("PORT", 5000))
        pass