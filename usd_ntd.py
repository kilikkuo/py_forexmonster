# coding=UTF-8

import traceback
import locale
import requests
import utils
from bs4 import BeautifulSoup

ALL_PRICE_URL = "http://www.findrate.tw/USD/#.WxyVbzP-jBI"
BANK_INFOS  = [{"SWIFT": "BKTWTWTP",
                "URL": "http://www.findrate.tw/bank/29/#.WxYHD0iFOUk",
                "INTERBANK_TRANS_CODE": "004",
                "NAME": u"臺灣銀行"},

                {"SWIFT": "UWCBTWTP",
                "URL": "http://www.findrate.tw/bank/11/#.WxyRHDP-jBJ",
                "INTERBANK_TRANS_CODE": "013",
                "NAME": u"國泰世華"},

                {"SWIFT": "TPBKTWTP",
                "URL": "http://www.findrate.tw/bank/8/#.WxyRKzP-jBJ",
                "INTERBANK_TRANS_CODE": "012",
                "NAME": u"富邦銀行"},

                {"SWIFT": "LBOTTWTP",
                "URL": "http://www.findrate.tw/bank/12/#.WxyRMjP-jBJ",
                "INTERBANK_TRANS_CODE": "005",
                "NAME": u"土地銀行"},

                {"SWIFT": "CTCBTWTP",
                "URL": "http://www.findrate.tw/bank/2/#.WxyROTP-jBJ",
                "INTERBANK_TRANS_CODE": "822",
                "NAME": u"中國信託"}
    ]

def get_impl():
    global BANK_INFOS
    global ALL_PRICE_URL

    r = requests.get(ALL_PRICE_URL)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, "html.parser")

    bankNames = [item["NAME"] for item in BANK_INFOS]
    rows = soup.find_all('tr')
    result = {}
    for r in rows:
        children = r.findChildren()
        for c in children:
            if c.text in bankNames:
                cp = c.parent
                sbs = cp.find_next_siblings('td')
                fxrate = sbs[2].text
                fxrate = fxrate.replace(",", "")
                result[c.text] = fxrate
                print("Bank : {} / FxRate : {}".format(c.text, result[c.text]))

    return result

def get_current_forex_price():
    return get_impl()
