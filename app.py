# coding=UTF-8

from flask import Flask, request, current_app
from utils import is_local_dev_env
import json

app = Flask(__name__)

@app.route('/')
def index():

    html = "<p>Hello World!</p>"
    formUSD2NTD = "<form action=\'/usd_ntd\'><input type=\"submit\" value=\"Go to USD2NTD\" /></form>"
    html += formUSD2NTD
    return html

@app.route('/usd_ntd')
def usd_ntd():
    from usd_ntd import get_current_forex_price
    result = get_current_forex_price()

    html = "<p> USD <=> NTD </p>"
    table = "<table style=\"border: 5px double rgb(109, 2, 107); height: 100px;\
     background-color: rgb(255, 255, 255); width: 300px;\" align=\"left\"\
      cellpadding=\"5\" cellspacing=\"5\" frame=\"border\" rules=\"all\"><tbody>"

    html += table + "<tr><td>{:>12}</td><td>{:>12}</td></tr>".format("外匯機構", "牌價")
    for bank, price in result.items():
        html += "<tr><td>{:>12}</td><td>{:>12}</td></tr>".format(bank, price)
    
    table_end = "</tbody></table>"
    return html

def start_app():
    if is_local_dev_env():
        app.run(host="0.0.0.0", debug=True, use_reloader=True)
    else:
        from os import environ
        app.run(host="0.0.0.0", debug=False, port=environ.get("PORT", 5000))