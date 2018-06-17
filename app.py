# coding=UTF-8

from flask import Flask, request, current_app
from utils import is_local_dev_env
import json

app = Flask(__name__)

TABLE_SCRIPTS_BEGIN = "<table style=\"border: 5px double rgb(109, 2, 107); height: 100px;" +\
                    "background-color: rgb(255, 255, 255); width: 300px;\" align=\"left\"" +\
                    "cellpadding=\"5\" cellspacing=\"5\" frame=\"border\" rules=\"all\"><tbody>" +\
                    "<tr><td>{:>12}</td><td>{:>12}</td></tr>".format("外匯機構", "牌價")

TABLE_SCRIPTS_END = "</tbody></table>"

@app.route('/')
def index():
    html = "<p>Hello World!</p>"
    formUSD2NTD = "<form action=\'/usd_ntd\'><input type=\"submit\" value=\"Go to USD2NTD\" /></form>"
    formUSD2KHR = "<form action=\'/usd_khr\'><input type=\"submit\" value=\"Go to USD2KHR\" /></form>"
    html += formUSD2NTD
    html += formUSD2KHR
    return html

@app.route('/usd_ntd')
def usd_ntd():
    global TABLE_SCRIPTS_BEGIN, TABLE_SCRIPTS_END
    from usd_ntd import get_current_forex_price
    result = get_current_forex_price()

    html = "<p> USD <=> NTD </p>"

    html += TABLE_SCRIPTS_BEGIN
    for bank, price in result.items():
        html += "<tr><td>{:>30}</td><td>{:>12}</td></tr>".format(bank, price)
    
    html += TABLE_SCRIPTS_END
    return html

@app.route('/usd_khr')
def usd_khr():
    global TABLE_SCRIPTS_BEGIN, TABLE_SCRIPTS_END
    from usd_khr import get_current_forex_price
    result = get_current_forex_price()

    html = "<p> USD <=> KHR </p>"

    html += TABLE_SCRIPTS_BEGIN
    for bank, price in result.items():
        html += "<tr><td>{:>30}</td><td>{:>12}</td></tr>".format(bank, price)

    html += TABLE_SCRIPTS_END
    return html

def start_app():
    if is_local_dev_env():
        app.run(host="0.0.0.0", debug=True, use_reloader=True)
    else:
        from os import environ
        app.run(host="0.0.0.0", debug=False, port=environ.get("PORT", 5000))