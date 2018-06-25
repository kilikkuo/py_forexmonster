# coding=UTF-8

from flask import Flask, request, current_app
from utils import is_local_dev_env, create_phantomjs
from datetime import datetime
import json
import threading
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()

IN_PROGRESS = []

TABLE_SCRIPTS_BEGIN = "<table style=\"border: 5px double rgb(109, 2, 107); height: 100px;" +\
                    "background-color: rgb(255, 255, 255); width: 300px;" +\
                    "display: block flow;float: none\" align=\"left\" " +\
                    "cellpadding=\"5\" cellspacing=\"5\" frame=\"border\" rules=\"all\"><tbody>"

TABLE_SCRIPTS_END = "</tbody></table>"

DISPLAY_PAGE = ""

@app.route('/')
def index():
    global DISPLAY_PAGE
    if DISPLAY_PAGE:
        return DISPLAY_PAGE

    create_phantomjs()

    html = "<html><head><meta http-equiv=\"refresh\" content=\"5\"></head><body><p>Hello World!</p>"

    create_workers()
    html += "</body></html>"
    DISPLAY_PAGE = html
    return html

def worker_callback(name, ret):
    global DISPLAY_PAGE
    assert DISPLAY_PAGE

    head = DISPLAY_PAGE.split("</body></html>")[0]

    startTime = ret["start"]
    results = ret["results"]

    part = results

    html = head + part + "</body></html>"
    DISPLAY_PAGE = html

def create_workers():
    t1 = threading.Thread(target = usd_to_something_worker, args=("ntd", worker_callback)).start()
    IN_PROGRESS.append("ntd")
    t2 = threading.Thread(target = usd_to_something_worker, args=("khr", worker_callback)).start()
    IN_PROGRESS.append("khr")
    t3 = threading.Thread(target = usd_to_something_worker, args=("thb", worker_callback)).start()
    IN_PROGRESS.append("thb")
    t4 = threading.Thread(target = usd_to_something_worker, args=("cny", worker_callback)).start()
    IN_PROGRESS.append("cny")

def usd_to_something_worker(something, callback):
    moduleName = "usd_" + something
    module = __import__(moduleName)

    startTime = datetime.now()
    result = module.get_current_forex_price()

    table = ""
    table += "<p>USD <=> {} / Last updated: {}<br/>".format(something.upper(), startTime)
    table += TABLE_SCRIPTS_BEGIN
    table += "<tr><th>{:>12}</th><th>{:>12}</th></tr>".format("外匯機構", "牌價")
    for bank, price in result.items():
        table += "<tr><td>{:>30}</td><td>{:>12}</td></tr>".format(bank, price)

    table += TABLE_SCRIPTS_END
    table += "</p>"

    callback(something, {"start": startTime, "results": table})
    IN_PROGRESS.remove(something)

def start_app():
    job = scheduler.add_job(create_workers, 'interval',  minutes=5)
    if is_local_dev_env():
        app.run(host="0.0.0.0", debug=True, use_reloader=True)
    else:
        from os import environ
        app.run(host="0.0.0.0", debug=False, port=environ.get("PORT", 5000))