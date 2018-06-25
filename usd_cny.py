# coding=UTF-8

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pprint import pprint
import traceback
import locale
import requests
import utils
from bs4 import BeautifulSoup

BANK_INFOS = [
                {"SWIFT": "",
                 "NAME": "China Foreign Exchange Trade System & National Interbank Funding Center.",
                 "URL": "http://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/rfx-sp-quot.json?",
                 "XPATH": "",
                 "ENABLED": True,
                 "IMPLEMENTATION": "get_chinamoney"},

                {"SWIFT": "",
                 "NAME": "REAL TIME CNY",
                 "URL": "http://www.real-time-cny.com/unionpay/",
                 "XPATH": "//div[@id='data']//span[@id='icbc']/table/tbody/tr/td[2]",
                 "ENABLED": True,
                 "IMPLEMENTATION": "get_realtimecny",
                 "SUBURLS": {"ICBC": "http://www.real-time-cny.com/php/icbc.php",
                            "BOC": "http://www.real-time-cny.com/php/boc.php",
                            "CCB": "http://www.real-time-cny.com/php/ccb.php",
                            "ABC": "http://www.real-time-cny.com/php/abc.php"}},

                {"SWIFT": "BOSHCNSHXXX",
                 "NAME": "BANK OF SHANGHAI",
                 "URL": "http://www.bosc.cn/WebServlet?go=bank_sellfund_pg_Banking&code=whpj",
                 "XPATH": "//form[@id='workForm']/table/tbody/tr[10]/td[5]/font/font",
                 "ENABLED": True,
                 "IMPLEMENTATION": "get_bosc"},

                {"SWIFT": "SCBKHKHH",
                 "NAME": "SHANGHAI COMMERCIAL BANK LTD.(Hong Kong)",
                 "URL": "https://www.shacombank.com.hk/tch/rate/foreign-currency-tt-exchange-rate.jsp",
                 "XPATH": "//div[@id='main']/div[2]/div[2]/div/table/tbody/tr/td[3]",
                 "ENABLED": True,
                 "IMPLEMENTATION": "get_shacombank"}
]

def get_chinamoney(url, bankInfo=None):
    name = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        content = eval(r.text)
        records = content.get("records", [])
        for record in records:
            if record.get("ccyPair", "") == "USD/CNY":
                rateCNYUSD = record["askPrc"]
                rateCNYUSD = locale.atof(rateCNYUSD.replace(",", ""))
                return [(name, rateCNYUSD)]
    except:
        traceback.print_exc()
    return [(name, None)]

def get_realtimecny(url, bankInfo=None):
    rateInfo = []
    try:
        subURLs = bankInfo.get("SUBURLS", {})
        for bank, subURL in subURLs.items():
            r = requests.get(subURL)
            r.encoding = "utf-8"
            soup = BeautifulSoup(r.text, "html.parser")
            tds = soup.find_all("td")
            rateCNYUSD = tds[0].text
            rateCNYUSD = locale.atof(rateCNYUSD.replace(",", ""))
            rateInfo.append((bank, round(rateCNYUSD / 100.0, 4)))
        return rateInfo
    except:
        traceback.print_exc()
    return (bankInfo["NAME"], None)

def get_bosc(url, bankInfo=None):
    name = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        tds = table.find_all("td")
        for idx, td in enumerate(tds):
            if td.text == "USD":
                unit = locale.atof(tds[idx+1].text.replace(",", ""))
                buyRate = locale.atof(tds[idx+3].text.replace(",", ""))
                rateCNYUSD = round(buyRate / unit, 4)
                return [(name, rateCNYUSD)]
    except:
        traceback.print_exc()
    return [(name, None)]

def get_shacombank(url, bankInfo=None):
    name = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        tds = table.find_all("td")
        for idx, td in enumerate(tds):
            if td.text == "美元":
                buyRate = locale.atof(tds[idx+2].text.replace(",", ""))
                rateCNYUSD = buyRate
                return [(name, rateCNYUSD)]
    except:
        traceback.print_exc()
    return [(name, None)]

def get_impl2():
    global BANK_INFOS
    result = {}
    for bankInfo in BANK_INFOS:
        if bankInfo.get("ENABLED"):
            implementation = bankInfo.get("IMPLEMENTATION")
            url = bankInfo.get("URL")
            rateInfo = globals()[implementation](url, bankInfo)
            for data in rateInfo:
                name, fxrate = data
                if fxrate == 0:
                    print("Partner : {} => CANNOT get price now ... please check !".format(name))
                else:
                    print("Partner : {} / FxRate : {}".format(name, fxrate))
                result[name] = fxrate
    return result
    pass

def get_current_forex_price():
    return get_impl2()