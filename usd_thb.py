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

BANK_INFOS = [{"SWIFT": "BOTHTHBK",
                 "NAME": "BANK OF THAILAND",
                 "URL": "https://www.bot.or.th/english/_layouts/application/exchangerate/exchangerate.aspx",
                 "XPATH": "//table[@id='ctl00_PlaceHolderMain_dgAvg']/tbody/tr[4]/td[5]",
                 "ENABLED": False,
                 "IMPLEMENTATION": "get_bot"},

                {"SWIFT": "BKKBTHBK",
                 "NAME": "BANGKOK BANK PUBLIC COMPANY LIMITED",
                 "URL": "https://www.bangkokbank.com/en/Personal/Other-Services/View-Rates/Foreign-Exchange-Rates",
                 "XPATH": "//table[@class='table-primary table-foreign-exchange-rates blue']",
                 "ENABLED": False,
                 "IMPLEMENTATION": "get_bkb"},

                {"SWIFT": "KASITHBK",
                 "NAME": "KASIKORNBANK PUBLIC COMPANY LIMITED",
                 "URL": "https://www.kasikornbank.com/en/rate/Pages/Foreign-Exchange.aspx",
                 "XPATH": "//table[@id='table-exchangerate']/tbody/tr[5]/td[4]",
                 "ENABLED": False,
                 "IMPLEMENTATION": "get_kasikorn"},

                {"SWIFT": "AYUDTHBK",
                 "NAME": "BANK OF AYUDHYA PUBLIC COMPANY LIMITED",
                 "URL": "https://www.krungsri.com/bank/en/Other/ExchangeRate/Todayrates.html",
                 "XPATH": "//div[@id='tab_content_1']/div/div[3]/table/tbody/tr/td[8]",
                 "ENABLED": False,
                 "IMPLEMENTATION": "get_krungsri"},

                {"SWIFT": "SICOTHBK",
                 "NAME": "SIAM COMMERCIAL BANK PCL., THE",
                 "URL": "http://www.scb.co.th/en/personal-banking/foreign-exchange-rates.html#fxrate",
                 "XPATH": "//*[@id='fxrate']/div/div[2]/div/table/tbody/tr[5]/td[4]",
                 "ENABLED": True,
                 "IMPLEMENTATION": "get_scb"}
]

def get_bot(url, bankInfo=None):
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", id='ctl00_PlaceHolderMain_dgAvg')
        tds = table.find_all("td")
        for idx, elem in enumerate(tds):
            if elem.text.startswith("USD"):
                target = tds[idx+2]
                rateUSDTHB = target.text
                return rateUSDTHB
    except:
        traceback.print_exc()
    return 0

def get_bkb(url, bankInfo=None):
    try:
        driver = utils.create_chromedriver()
        xpath = bankInfo["XPATH"]
        name = bankInfo["NAME"]
        if not xpath:
            print("[WARNING] Cannot find FxRate from {}".format(name))
            return 0
        utils.get_with_retry(driver, url)
        def get_text(dr):
            elem = dr.find_element(By.XPATH, xpath)
            return elem is not None
        WebDriverWait(driver, 10, 0.5).until(get_text)
        
        xpath2 = xpath + '/tbody/tr[3]/td[5]'
        elem = driver.find_element_by_xpath(xpath2)
        print(elem)
        fxrate = elem.text
        fxrate = fxrate.replace(",", "")
        driver.quit()
        return fxrate
    except:
        traceback.print_exc()
    return 0

def get_kasikorn(url, bankInfo=None):
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        divs = soup.find_all("div", {'class': 'itemsRate'})
        for div in divs:
            if div.attrs.get("data-sname", "") == "USD 50-100":
                fxrate = div.attrs.get("data-buytelex", "0")
                fxrate = fxrate.replace(",", "")
                return fxrate
    except:
        traceback.print_exc()
    return 0

def get_krungsri(url, bankInfo=None):
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        span = soup.find("span", id="p_lt_ctl19_ksP_p_lt_ctl05_ExchangeRate_tableCurrent")
        trs = span.find_all("tr")
        for tr in trs:
            tds = tr.find_all('td')
            for idx, td in enumerate(tds):
                if td.text.strip() == "USD":
                    next_td = tds[idx+1]
                    if int(next_td.text) == 1:
                        target_td = tds[idx+5]
                        fxrate = target_td.text
                        fxrate = fxrate.replace(",", "")
                        return fxrate
    except:
        traceback.print_exc()
    return 0

def get_scb(url, bankInfo=None):
    try:
        driver = utils.create_chromedriver()
        xpath = bankInfo["XPATH"]
        name = bankInfo["NAME"]
        if not xpath:
            print("[WARNING] Cannot find FxRate from {}".format(name))
            return 0
        utils.get_with_retry(driver, url)

        def get_text(dr):
            elem = dr.find_element(By.XPATH, xpath)
            return elem is not None
        WebDriverWait(driver, 10, 0.5).until(get_text)

        elem = driver.find_element_by_xpath(xpath)
        fxrate = elem.text
        fxrate = fxrate.replace(",", "")
        driver.quit()
        return fxrate
    except:
        traceback.print_exc()
    return 0

def get_impl():
    global BANK_INFOS
    result = {}
    for bankInfo in BANK_INFOS:
        if bankInfo.get("ENABLED"):
            implementation = bankInfo.get("IMPLEMENTATION")
            url = bankInfo.get("URL")
            name = bankInfo.get("NAME")
            fxrate = globals()[implementation](url, bankInfo)
            if not fxrate:
                fxrate = "0"
                print("Partner : {} => CANNOT get price now ... please check !".format(name))
            else:
                fxrate = locale.atof(fxrate.replace(",", ""))
                print("Partner : {} / FxRate : {}".format(name, fxrate))
            result[name] = fxrate
    return result
    pass

def get_current_forex_price():
    return get_impl()
