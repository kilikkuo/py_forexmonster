# coding=UTF-8

from datetime import datetime
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

    bankNames = [item["NAME"] for item in BANK_INFOS]
    driver = utils.create_chromedriver()

    result = {}
    utils.get_with_retry(driver, ALL_PRICE_URL)
    try:
        print(datetime.now())
        xpathTable = "//div[@id='right']/table[2]/tbody/tr"
        lstElem = driver.find_elements_by_xpath(xpathTable)
        for i in range(2, len(lstElem)+1):
            xpathRow = xpathTable + "[{}]/td".format(i)
            elem = driver.find_element_by_xpath(xpathRow)
            encodedBankName = elem.text.encode("utf-8")
            if encodedBankName in bankNames:
                xpathIBTB = xpathRow + "[4]"
                elem = driver.find_element_by_xpath(xpathIBTB)
                fxrate = elem.text.encode("utf-8")
                fxrate = fxrate.replace(",", "")
                print("Bank : {} / FxRate : {}".format(encodedBankName, locale.atof(fxrate)))
                result[encodedBankName] = locale.atof(fxrate)
    except:
        traceback.print_exc()
    return result

def get_impl2():
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
                result[c.text] = locale.atof(sbs[2].text)
                print("Bank : {} / FxRate : {}".format(c.text, locale.atof(sbs[2].text)))
    return result

def get_current_forex_price():
    return get_impl2()
