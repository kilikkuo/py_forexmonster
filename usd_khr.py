# coding=UTF-8

from datetime import datetime
import traceback
import locale
import requests
import utils
from bs4 import BeautifulSoup

BANK_INFOS = [
            {"SWIFT": "NCAMKHPP",
            "NAME": "NATIONAL BANK OF CAMBODIA",
            "URL": "https://www.nbc.org.kh/english/economic_research/exchange_rate.php",
            "XPATH": "//form[@id='fm-ex']/table/tbody/tr[2]/td/font",
            "ENABLED": True,
            "IMPLEMENTATION": "get_nbc"},

            {"SWIFT": "",
            "NAME": "AMK CAMBODIA",
            "URL": "https://www.amkcambodia.com/foreign-exchange.html",
            "XPATH": "//div[@id='content_body']/table/tbody/tr[2]/td[2]",
            "ENABLED": True,
            "IMPLEMENTATION": "get_amk"},

            {"SWIFT": "ACLBKHPP",
            "NAME": "ACLEDA BANK PLC.",
            "URL": "https://www.acledabank.com.kh/kh/eng/ps_cmforeignexchange",
            "XPATH": "//form[@name='frmdEx']/table/tbody/tr[2]/td[2]",
            "ENABLED": True,
            "IMPLEMENTATION": "get_acleda"},

            {"SWIFT": "CADIKHPP",
            "NAME": "CANADIA BANK PLC",
            "URL": "https://www.canadiabank.com.kh/en/exchange_rate.aspx",
            "XPATH": "//div[@id='menu']/table/tbody/tr/td[2]/div[2]/table/tbody/tr[2]/td[2]",
            "ENABLED": True,
            "IMPLEMENTATION": "get_canadia"},

            {"SWIFT": "IDBCKHPP",
            "NAME": "BANK FOR INVESTMENT AND DEVELOPMENT OF CAMBODIA PLC",
            "URL": "https://www.bidc.com.kh/#tygia",
            "XPATH": "//table[@id='tbl_100']/tbody/tr[8]/td[2]",
            "ENABLED": True,
            "IMPLEMENTATION": "get_idbc"}
]

def get_impl():
    global BANK_INFOS
    driver = create_headless_chromedriver()
    try:
        for item in BankInfo:
            url = item["URL"]
            xpath = item["XPATH"]
            name = item["NAME"]
            if not xpath:
                print("[WARNING] Cannot find FxRate from {}".format(name))
                continue
            get_with_retry(driver, url)
            result, elem = find_element_by_xpath_safely(driver, xpath)
            if not result:
                print("[WARNING] Cannot find FxRate from {} - No such element !!".format(name))
                continue
            fxrate = elem.text.encode("utf-8")
            if "khr" in fxrate.lower():
                fxrate = fxrate.split(" ")[1]
            fxrate = fxrate.replace(",", "")
            print("Partner : {} / FxRate : {}".format(name, locale.atof(fxrate)))
    except:
        traceback.print_exc()

def get_nbc(url):
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find(id="fm-ex")
        
        rateKHRUSD = table.find_all("td")[1].text.split(":")[1].strip()
        return rateKHRUSD.split(" ")[0]
    except:
        traceback.print_exc()
    return None

def get_amk(url):
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.table
        rateKHRUSD = table.find_all("tr")[1].find_all("td")[1].text
        return rateKHRUSD.split(" ")[1]
    except:
        traceback.print_exc()
    return None

def get_acleda(url):
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.table
        tds = table.find_all("td")
        for idx, elem in enumerate(tds):
            if elem.text == "US Dollar (USD)":
                next_elem = tds[idx+1]
                if "KHR" in next_elem.text:
                    rateKHRUSD = next_elem.text.split(" ")[1]
                    return rateKHRUSD
    except:
        traceback.print_exc()
    return None

def get_canadia(url):
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        span = soup.find_all("span", id="lblKH_Buy")[0]
        rateKHRUSD = span.text
        return rateKHRUSD
    except:
        traceback.print_exc()
    return None

def get_idbc(url):
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find_all("table", id="tbl_100")[0]
        tds = table.find_all("td")
        for idx, td in enumerate(tds):
            if td.text == "KHR/USD":
                next_td = tds[idx+1]
                rateKHRUSD = next_td.text
                return rateKHRUSD
    except:
        traceback.print_exc()
    return None

def get_impl2():
    global BANK_INFOS
    result = {}
    for bankInfo in BANK_INFOS:
        if bankInfo.get("ENABLED"):
            implementation = bankInfo.get("IMPLEMENTATION")
            url = bankInfo.get("URL")
            name = bankInfo.get("NAME")
            fxrate = globals()[implementation](url)
            if fxrate is None:
                fxrate = "0"
                print("Partner : {} => CANNOT get price now ... please check !".format(name))
            else:
                fxrate = locale.atof(fxrate.replace(",", ""))
                print("Partner : {} / FxRate : {}".format(name, fxrate))
            result[name] = fxrate
    return result
    pass

def get_current_forex_price():
    print(datetime.now())
    return get_impl2()
