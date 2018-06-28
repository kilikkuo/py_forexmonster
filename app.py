# coding=UTF-8

from flask import Flask, request, current_app
from utils import is_local_dev_env, create_phantomjs
from datetime import datetime, timedelta
import pytz
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
NEXT_TRIGGER_TIME = None

CLEAR_PAGE = "<html><head><meta http-equiv=\"refresh\" content=\"10\"></head><body>" +\
             "</body></html>"

def get_progress():
    global IN_PROGRESS
    progress = "<div id='pg'> {} tasks are being processed ... please wait <br>".format(len(IN_PROGRESS)) +\
               " They are {} </div>".format(IN_PROGRESS)
    return progress

@app.route('/')
def index():
    global DISPLAY_PAGE
    # global NEXT_TRIGGER_TIME
    # if NEXT_TRIGGER_TIME:
    #     diff = NEXT_TRIGGER_TIME - datetime.now(pytz.timezone('Asia/Taipei'))
    #     before_div = DISPLAY_PAGE.partition("<div>")[0] if len(DISPLAY_PAGE.partition("<div>")) == 3 else None
    #     after_div = DISPLAY_PAGE.partition("</div>")[2] if len(DISPLAY_PAGE.partition("</div>")) == 3 else None
    #     if before_div and after_div:
    #         newContent = "<div>網頁每 5 秒更新 ... FX 重新擷取 in {} seconds </div>".format(diff.seconds)
    #         DISPLAY_PAGE = before_div + newContent + after_div
    if DISPLAY_PAGE:
        return DISPLAY_PAGE

    create_phantomjs()

    DISPLAY_PAGE = CLEAR_PAGE
    create_workers()
    return DISPLAY_PAGE

def worker_callback(name, ret):
    global DISPLAY_PAGE, IN_PROGRESS
    assert DISPLAY_PAGE

    head = DISPLAY_PAGE.split("<div id='pg'>")[0]
    print(DISPLAY_PAGE.split("</div>"))
    tail = DISPLAY_PAGE.split("</div>")[1]

    startTime = ret["start"]
    results = ret["results"]

    part = results

    # html = head + part + "</body></html>"
    # DISPLAY_PAGE = html
    if name in IN_PROGRESS:
        IN_PROGRESS.remove(name)
        # progress = "<div id='pg'> {} tasks are being processed ... please wait </div>".format(len(IN_PROGRESS))
        DISPLAY_PAGE = head + get_progress() + part + tail

def remove(tag, id, html):
    builtStartingTag = "<{} id='{}'>".format(tag, id)
    builtClosingTag = "</{}>".format(tag)
    startIdx = html.find(builtStartingTag)
    EndIdx = html.find(builtClosingTag, startIdx)
    newHead = html[0:startIdx]
    newTail = html[EndIdx+len(builtClosingTag):]
    return newHead, newTail

def create_workers():
    global IN_PROGRESS, DISPLAY_PAGE, CLEAR_PAGE
    # global NEXT_TRIGGER_TIME, 
    IN_PROGRESS = []
    # NEXT_TRIGGER_TIME = datetime.now(pytz.timezone('Asia/Taipei')) + timedelta(seconds=300)
    t1 = threading.Thread(target = usd_to_something_worker, args=("ntd", worker_callback)).start()
    IN_PROGRESS.append("ntd")
    t2 = threading.Thread(target = usd_to_something_worker, args=("khr", worker_callback)).start()
    IN_PROGRESS.append("khr")
    t3 = threading.Thread(target = usd_to_something_worker, args=("thb", worker_callback)).start()
    IN_PROGRESS.append("thb")
    t4 = threading.Thread(target = usd_to_something_worker, args=("cny", worker_callback)).start()
    IN_PROGRESS.append("cny")

    head = CLEAR_PAGE.partition("</head><body>")[0]
    tail = CLEAR_PAGE.partition("</body></html>")[0]

    # progress = "<div id='pg'> {} tasks are being processed ... please wait </div>".format(len(IN_PROGRESS))
    DISPLAY_PAGE = head + get_progress() + tail

def usd_to_something_worker(something, callback):
    moduleName = "usd_" + something
    module = __import__(moduleName)

    tz = pytz.timezone('Asia/Taipei')
    startTime = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
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

def start_app():
    job = scheduler.add_job(create_workers, 'interval', seconds=300)
    scheduler.start()
    if is_local_dev_env():
        app.run(host="0.0.0.0", debug=True, use_reloader=True)
    else:
        from os import environ
        app.run(host="0.0.0.0", debug=False, port=environ.get("PORT", 5000))