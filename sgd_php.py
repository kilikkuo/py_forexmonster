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
                "SWIFT": "DBSSSGSGXXX",
                "NAME": "DBS Bank Ltd.",
                "URL": "https://www.dbs.com.sg/personal/rates-online/foreign-currency-foreign-exchange.page",
                "ENABLED": True,
                "IMPLEMENTATION": "get_dbs"
            },

            {
                "SWIFT": "PNBMPHMMXXX",
                "NAME": "Philippine National Bank.",
                "URL": "http://www.pnb.com.ph/singapore/Rates/ExchangeRates.html",
                "ENABLED": True,
                "IMPLEMENTATION": "get_pnb"
            },

            {
                "SWIFT": "UOVBSGSGXXX",
                "NAME": "United Overseas Bank Limited.",
                "URL": "https://uniservices1.uobgroup.com/secure/online_rates/foreign_exchange_rates_against_singapore_dollar.jsp?s_pid=HOME201205_eg_quicklnk_ql7",
                "ENABLED": True,
                "IMPLEMENTATION": "get_uob"
            },
]

def get_dbs(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        php_tr = soup.find("tr", attrs={"name": "philippinepeso"})
        target = php_tr.find("td", attrs={"class": "column3"})
        rateSGDPHP = target.text
        rateSGDPHP = rateSGDPHP.replace(",", "")
        rateSGDPHP = locale.atof(rateSGDPHP)
        return [("{}, unit(100)".format(bankName), rateSGDPHP)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_pnb(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        driver = utils.create_chromedriver()
        utils.get_with_retry(driver, url)
        def get_text(dr):
            elem = dr.find_element(By.TAG_NAME, "table")
            return elem != None
        WebDriverWait(driver, 10, 0.5).until(get_text)
        content = driver.page_source
        rateSGDPHP = content.partition("P1,000 = S$")[2].partition("\n</pre>")[0]
        rateSGDPHP = rateSGDPHP.replace(",", "")
        rateSGDPHP = locale.atof(rateSGDPHP)
        driver.quit()
        return [("{}, unit(1000)".format(bankName), rateSGDPHP)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_uob(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        driver = utils.create_chromedriver()
        utils.get_with_retry(driver, url)
        def get_text(dr):
            elem = dr.find_element(By.XPATH, "//tr[2]/td[2]")
            return elem != None
        WebDriverWait(driver, 10, 0.5).until(get_text)
        content = driver.page_source
        driver.quit()
        soup = BeautifulSoup(content, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if td.text == "PHILIPPINES PESO":
                target_td = tds[idx + 2]
                rateSGDPHP = target_td.text
                rateSGDPHP = rateSGDPHP.replace(",", "")
                rateSGDPHP = locale.atof(rateSGDPHP)
                return [("{}, unit(100)".format(bankName), rateSGDPHP)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]    

def get_impl():
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
    return get_impl()