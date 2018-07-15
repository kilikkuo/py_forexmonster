# coding=UTF-8

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pprint import pprint
from datetime import date, timedelta
from bs4 import BeautifulSoup
import os
import traceback
import locale
import requests
import utils

BANK_INFOS = [
            {
                "SWIFT": "STBVVNVXXXX",
                "NAME": "State Bank of Viet Nam.",
                "URL": "https://www.sbv.gov.vn/webcenter/portal/en/home/rm/er?centerWidth=80%25&leftWidth=20%25&rightWidth=0%25&showFooter=false&showHeader=false&_adf.ctrl-state=19izpkwweh_4&_afrLoop=8111483055743432#%40%3F_afrLoop%3D8111483055743432%26centerWidth%3D80%2525%26leftWidth%3D20%2525%26rightWidth%3D0%2525%26showFooter%3Dfalse%26showHeader%3Dfalse%26_adf.ctrl-state%3Dw3nxezlou_4",
                "ENABLED": True,
                "IMPLEMENTATION": "get_sbv"
            },

            {
                "SWIFT": "HDBCVNVXXXX",
                "NAME": "HO CHI MINH CITY DEVELOPMENT JOINT STOCK COMMERCIAL BANK.",
                "URL": "https://www.hdbank.com.vn/?ArticleId=f7fb576a-fe3e-40ea-9a67-4b00a3f06742",
                "ENABLED": True,
                "IMPLEMENTATION": "get_hdb"
            },

            {
                "SWIFT": "IDBCKHPPXXX",
                "NAME": "BANK FOR INVESTMENT AND DEVELOPMENT OF CAMBODIA PLC.",
                "URL": "https://www.bidc.com.kh/Default.aspx?po=2&p=85&nid=291#tygia",
                "ENABLED": True,
                "IMPLEMENTATION": "get_bidc"
            },

            {
                "SWIFT": "ICBVVNVXXXX",
                "NAME": "Vietnam Joint Stock Commercial Bank For Industry and Trade.",
                "URL": "https://www.vietinbank.vn/web/home/en/doc/saving/exrate.html",
                "ENABLED": True,
                "IMPLEMENTATION": "get_vietin"
            },

            {
                "SWIFT": "VBAAVNVX380",
                "NAME": "Vietnam Bank for Agriculture and Rural Development.",
                "URL": "http://agribank.com.vn/Layout/Pages/GetTyGia.aspx?date=13/7/2018&lang=2",
                "ENABLED": False,
                "IMPLEMENTATION": "get_agribank"
            },

            {
                "SWIFT": "BFTVVNVXXXX",
                "NAME": "JOINT STOCK COMMERCIAL BANK FOR FOREIGN TRADE OF VIETNAM.",
                "URL": "https://www.vietcombank.com.vn/ExchangeRates/?lang=en",
                "ENABLED": True,
                "IMPLEMENTATION": "get_vietcom"
            },
]

def get_sbv(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if td.text.strip().rstrip() == "United States Dollar":
                print("yes")
                next_td = tds[idx + 1]
                rateVNDUSD = next_td.text
                rateVNDUSD = locale.atof(rateVNDUSD.replace(",", ""))
                return [(bankName, rateVNDUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_hdb(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        driver = utils.create_phantomjs()
        utils.get_with_retry(driver, url)
        def get_text(dr):
            elem = dr.find_element(By.CLASS_NAME, "borderBottomLeft")
            return elem != None
        WebDriverWait(driver, 10, 0.5).until(get_text)
        content = driver.page_source
        driver.quit()
        soup = BeautifulSoup(content, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if td.text.strip().rstrip() == "USD(50,100)":
                target_td = tds[idx + 2]
                rateVNDUSD = target_td.text
                rateVNDUSD = locale.atof(rateVNDUSD.replace(",", ""))
                return [(bankName, rateVNDUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_bidc(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if td.text.strip().rstrip() == "VND/USD":
                target_td = tds[idx + 1]
                rateVNDUSD = target_td.text
                rateVNDUSD = locale.atof(rateVNDUSD.replace(",", ""))
                return [(bankName, rateVNDUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_vietin(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if td.text.strip().rstrip() == "USD":
                target_td = tds[idx + 3]
                rateVNDUSD = target_td.text
                rateVNDUSD = locale.atof(rateVNDUSD.replace(",", ""))
                return [(bankName, rateVNDUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_agribank(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:        
        # driver = utils.create_chromedriver()
        # utils.get_with_retry(driver, url)
        # def get_text(dr):
        #     elem = dr.find_element(By.ID, "tblTG")
        #     return elem != None
        # WebDriverWait(driver, 10, 0.5).until(get_text)
        # content = driver.page_source
        # print(content)
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_vietcom(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if td.text.strip().rstrip() == "US DOLLAR":
                target_td = tds[idx + 2]
                rateVNDUSD = target_td.text
                rateVNDUSD = locale.atof(rateVNDUSD.replace(",", ""))
                return [(bankName, rateVNDUSD)]
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