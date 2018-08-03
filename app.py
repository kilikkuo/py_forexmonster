# coding=UTF-8

from flask import Flask, request, current_app
from utils import is_local_dev_env, create_phantomjs, create_chromedriver
from main import get_corridor_lut
from datetime import datetime, timedelta
import pytz
import json
import threading
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()

IN_PROGRESS = []
DISPLAY_PAGE = ""
LAST_TRIGGER_TIME = None
NEXT_TRIGGER_TIME = None
RETRIGGER_DURATION = 300
PAGE_REFRESH_DURATION = 5

TABLE_SCRIPTS_BEGIN = "<table style=\"border: 5px double rgb(109, 2, 107); height: 100px;" +\
                    "background-color: rgb(255, 255, 255); width: 300px;" +\
                    "display: block flow;float: none\" align=\"left\" " +\
                    "cellpadding=\"5\" cellspacing=\"5\" frame=\"border\" rules=\"all\"><tbody>"
TABLE_SCRIPTS_END = "</tbody></table>"

INITIAL_PAGE_HEAD = "<html><head><meta http-equiv=\"refresh\" content=\"{}\"></head><body>".format(PAGE_REFRESH_DURATION)
INITIAL_PAGE_TAIL = "</body></html>"

def get_progress():
    global IN_PROGRESS
    global NEXT_TRIGGER_TIME, LAST_TRIGGER_TIME
    diff = NEXT_TRIGGER_TIME - datetime.now(pytz.timezone('Asia/Taipei'))
    if len(IN_PROGRESS):
        names = [t.name for t in IN_PROGRESS]
        progress = "<div id='pg'>" +\
                " {} tasks are being processed ... please wait <br>".format(len(IN_PROGRESS)) +\
                " The remaining tasks are {}.<br>".format(names) +\
                " Qeury time : {}.<br>".format(LAST_TRIGGER_TIME.strftime("%Y-%m-%d %H:%M:%S")) +\
                " Next FX refresh in {} seconds.</div>".format(diff.seconds)
    else:
        progress = "<div id='pg'>" +\
                " Qeury time : {}.<br>".format(LAST_TRIGGER_TIME.strftime("%Y-%m-%d %H:%M:%S")) +\
                " Next FX refresh in {} seconds.</div>".format(diff.seconds)
    return progress

def get_head_tail_exclude_div():
    global DISPLAY_PAGE
    if len(DISPLAY_PAGE.split("<div id='pg'>")) == 2 and\
        len(DISPLAY_PAGE.split("</div>")) == 2:
        head = DISPLAY_PAGE.split("<div id='pg'>")[0]
        tail = DISPLAY_PAGE.split("</div>")[1]
        return head, tail
    else:
        return None, None

@app.route('/')
def index():
    global DISPLAY_PAGE
    if DISPLAY_PAGE:
        head, tail = get_head_tail_exclude_div()
        DISPLAY_PAGE = head + get_progress() + tail
        return DISPLAY_PAGE

    create_workers()
    return DISPLAY_PAGE

def worker_callback(name, ret):
    global DISPLAY_PAGE, IN_PROGRESS
    assert DISPLAY_PAGE

    head = DISPLAY_PAGE.split("<div id='pg'>")[0]
    tail = DISPLAY_PAGE.split("</div>")[1]
    part = ret["results"]

    IN_PROGRESS = [t for t in IN_PROGRESS if t.name != name]
    DISPLAY_PAGE = head + get_progress() + tail + part

def remove(tag, id, html):
    builtStartingTag = "<{} id='{}'>".format(tag, id)
    builtClosingTag = "</{}>".format(tag)
    startIdx = html.find(builtStartingTag)
    EndIdx = html.find(builtClosingTag, startIdx)
    newHead = html[0:startIdx]
    newTail = html[EndIdx+len(builtClosingTag):]
    return newHead, newTail

def create_workers():
    global IN_PROGRESS, DISPLAY_PAGE
    global NEXT_TRIGGER_TIME, LAST_TRIGGER_TIME
    IN_PROGRESS = []
    LAST_TRIGGER_TIME = datetime.now(pytz.timezone('Asia/Taipei'))
    NEXT_TRIGGER_TIME = LAST_TRIGGER_TIME + timedelta(seconds=RETRIGGER_DURATION)

    lut = get_corridor_lut()
    for corridor, enabled in lut.items():
        if enabled:
            _from, _to = corridor.split("_")
            t = threading.Thread(target = from_to_worker, args=(_from, _to, worker_callback), name=corridor)
            IN_PROGRESS.append(t)

    DISPLAY_PAGE = INITIAL_PAGE_HEAD + get_progress() + INITIAL_PAGE_TAIL
    for t in IN_PROGRESS:
        t.start()

def from_to_worker(_from, _to, callback):
    moduleName = "{}_{}".format(_from, _to)
    module = __import__(moduleName)

    tz = pytz.timezone('Asia/Taipei')
    result = module.get_current_forex_price()

    table = ""
    table += "<p style=\"float: left\">{} <=> {}<br/>".format(_from.upper(), _to.upper())
    table += TABLE_SCRIPTS_BEGIN
    table += "<tr><th>{:>12}</th><th>{:>12}</th></tr>".format("Organization", "Exchange Rate")
    for bank, price in result.items():
        table += "<tr><td>{:>30}</td><td>{:>12}</td></tr>".format(bank, price)

    table += TABLE_SCRIPTS_END
    table += "</p>"

    callback(moduleName, {"results": table})

def start_app():
    job = scheduler.add_job(create_workers, 'interval', seconds=RETRIGGER_DURATION)
    scheduler.start()
    if is_local_dev_env():
        app.run(host="0.0.0.0", debug=True, use_reloader=False)
    else:
        from os import environ
        app.run(host="0.0.0.0", debug=False, port=environ.get("PORT", 5000))