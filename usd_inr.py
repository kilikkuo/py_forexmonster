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
                "SWIFT": "RBISINBBXXX",
                "NAME": "Reserve Bank of India.",
                "URL": "https://rbi.org.in/SCRIPTS/BS_DisplayReferenceRate.aspx",
                "ENABLED": True,
                "IMPLEMENTATION": "get_rbi"
            },

            {
                "SWIFT": "KKBKINBBXXX",
                "NAME": "Kotak Mahindra Bank Ltd.",
                "URL": "https://www.kotak.com/j1001drup/phpapps/content/siteadmin/get_forex_rates_data2.php",
                "ENABLED": True,
                "IMPLEMENTATION": "get_kotak"
            },

            {
                "SWIFT": "HDFCINBBXXX",
                "NAME": "HDFC BANK LIMITED.",
                "URL": "https://www.hdfcbank.com/nri_banking/Foreign_Exchng_Rates/Foreign_Exchng_Rates.asp",
                "XPATH": "//tr[3]/td[3]",
                "ENABLED": True,
                "IMPLEMENTATION": "get_hdfcbank"
            },

            {
                "SWIFT": "ICICINBBXXX",
                "NAME": "ICICI Bank Limited",
                "URL": "https://www.icicibank.com/nri-banking/money_transfer/money-transfer-rates.page",
                "ENABLED": True,
                "IMPLEMENTATION": "get_icicibank"
            },

            {
                "SWIFT": "PUNBINBBXXX",
                "NAME": "Punjab National Bank",
                "URL": "https://www.pnbindia.in/downloadprocess.aspx?fid=A+rrvZeJc+PIaxfEqVTIQQ==",
                "ENABLED": True,
                "IMPLEMENTATION": "get_phbindia"
            },
]

def get_rbi(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", "tablebg")
        ps = table.find_all("p")
        for idx, p in enumerate(ps):
            if "₹" in p.text and "US Dollar" in p.text:
                words = p.text.split(" ")
                rateINRUSD = words[words.index("₹") + 1]
                rateINRUSD = rateINRUSD.replace(",", "")
                rateINRUSD = locale.atof(rateINRUSD)
                return [(bankName, rateINRUSD)]
    except:
        traceback.print_exc()
    return bankName, 0

def get_kotak(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if "USD" in td.text.strip():
                target_td = tds[idx+4]
                rateINRUSD = target_td.text
                rateINRUSD = rateINRUSD.replace(",", "")
                rateINRUSD = locale.atof(rateINRUSD)
                return [(bankName, rateINRUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_hdfcbank(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        driver = utils.create_phantomjs()
        xpath = bankInfo["XPATH"]
        name = bankInfo["NAME"]
        if not xpath:
            print("[WARNING] Cannot find FxRate from {}".format(name))
            return 0
        utils.get_with_retry(driver, url)
        def get_text(dr):
            elem = dr.find_element(By.XPATH, xpath)
            return elem.text != ""
        WebDriverWait(driver, 10, 0.5).until(get_text)
        elem = driver.find_element_by_xpath(xpath)
        rateINRUSD = elem.text
        rateINRUSD = rateINRUSD.replace(",", "")
        rateINRUSD = locale.atof(rateINRUSD)
        return [(bankName, rateINRUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_icicibank(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            if "USA" in td.text.strip():
                next_td = tds[idx+1]
                rateINRUSD = next_td.text.split(" ")[1]
                rateINRUSD = rateINRUSD.replace(",", "")
                rateINRUSD = locale.atof(rateINRUSD)
                return [(bankName, rateINRUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_phbindia(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        # driver = utils.create_chromedriver()
        # r = driver.get(url)
        import time
        time.sleep(4)
        # print(r)

        print("Status: Download Complete.")
        # driver.close()
        # for idx, td in enumerate(tds):
        #     if "USD" in td.text.strip():
        #         next_td = tds[idx+1]
        #         ratePHPUSD = next_td.text
        #         ratePHPUSD = ratePHPUSD.replace(",", "")
        #         ratePHPUSD = locale.atof(ratePHPUSD)
        #         return [(bankName, ratePHPUSD)]
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