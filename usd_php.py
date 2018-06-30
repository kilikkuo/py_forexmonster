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
            {
                "SWIFT": "PHCBPHMM",
                "NAME": "BANGKO SENTRAL NG PILIPINAS",
                "URL": "http://www.bsp.gov.ph",
                "ENABLED": True,
                "IMPLEMENTATION": "get_bsp"
            },

            {
                "SWIFT": "BNORPHMM",
                "NAME": "BDO UNIBANK, INC.",
                "URL": "https://www.bdo.com.ph/sites/default/files/forex/forex.htm",
                "ENABLED": True,
                "IMPLEMENTATION": "get_bdo"
            },

            {
                "SWIFT": "MCCEPHM1",
                "NAME": "METROBANK CARD CORPORATION (A FINANCE CO.)",
                "URL": "https://www.metrobank.com.ph/personal_product.asp",
                "ENABLED": True,
                "IMPLEMENTATION": "get_metro"
            },

            {
                "SWIFT": "BOPIPHMM",
                "NAME": "BANK OF THE PHILIPPINE ISLANDS",
                "URL": "https://www.bpiexpressonline.com/p/1/872/forex-rates",
                "ENABLED": True,
                "IMPLEMENTATION": "get_bpi"
            },
]

def get_bsp(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        ps = soup.find_all("p")
        for idx, p in enumerate(ps):
            if p.text == "US$ 1.00":
                next_p = ps[idx+1]
                ratePHPUSD = next_p.text.split(" ")[1]
                ratePHPUSD = ratePHPUSD.replace(",", "")
                ratePHPUSD = locale.atof(ratePHPUSD)
                return [(bankName, ratePHPUSD)]
    except:
        traceback.print_exc()
    return bankName, 0

def get_bdo(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if "US$" in td.text.strip():
                next_td = tds[idx+1]
                ratePHPUSD = next_td.text
                ratePHPUSD = ratePHPUSD.replace(",", "")
                ratePHPUSD = locale.atof(ratePHPUSD)
                return [(bankName, ratePHPUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_metro(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if td.text == "USD":
                next_td = tds[idx+1]
                ratePHPUSD = next_td.text
                ratePHPUSD = ratePHPUSD.replace(",", "")
                ratePHPUSD = locale.atof(ratePHPUSD)
                return [(bankName, ratePHPUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_bpi(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if "USD" in td.text.strip():
                next_td = tds[idx+1]
                ratePHPUSD = next_td.text
                ratePHPUSD = ratePHPUSD.replace(",", "")
                ratePHPUSD = locale.atof(ratePHPUSD)
                return [(bankName, ratePHPUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]
    

def get_impl2():
    global BANK_INFOS
    result = {}
    for bankInfo in BANK_INFOS:
        if bankInfo.get("ENABLED"):
            implementation = bankInfo.get("IMPLEMENTATION")
            url = bankInfo.get("URL")
            rateInfo = globals()[implementation](url, bankInfo)
            print(rateInfo)
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