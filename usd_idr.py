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
                "SWIFT": "INDOIDJAXXX",
                "NAME": "Bank Indonesia",
                "URL": "https://www.bi.go.id/en/moneter/informasi-kurs/transaksi-bi/Default.aspx",
                "ENABLED": False,
                "IMPLEMENTATION": "get_bi"
            },

            {
                "SWIFT": "PINBIDJAXXX",
                "NAME": "Panin Bank",
                "URL": "https://www.panin.co.id/ajax/callmycurrency/idr*10*1*usd*undefined",
                "URL_XPATH": "http://www.panin.co.id/",
                "XPATH": "//*[@id='first']/tr[1]/td[2]",
                "ENABLED": True,
                "IMPLEMENTATION": "get_panin"
            },

            {
                "SWIFT": "CENAIDJAXXX",
                "NAME": "BCA (PT Bank Central Asia Tbk)",
                "URL": "https://www.bca.co.id/Individu/Sarana/Kurs-dan-Suku-Bunga/Kurs-dan-Kalkulator",
                "ENABLED": False,
                "IMPLEMENTATION": "get_bca"
            },

            {
                "SWIFT": "BMRIKYKYXXX",
                "NAME": "PT Bank Mandiri (Persero) Tbk",
                "URL": "https://www.bankmandiri.co.id/en/home?row=2",
                "ENABLED": False,
                "IMPLEMENTATION": "get_bankmandiri"
            },

            {
                "SWIFT": "MAYAIDJAXXX",
                "NAME": "PT Bank Mayapada International Tbk",
                "URL": "https://myapps.bankmayapada.com/webbmi/infokursfull.aspx",
                "ENABLED": False,
                "IMPLEMENTATION": "get_bankmayapada"
            },
]

def get_bi(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", id="ctl00_PlaceHolderMain_biWebKursTransaksiBI_GridView2")
        tds = table.find_all("td")
        for idx, td in enumerate(tds):
            if "USD" in td.text.strip():
                target_td = tds[idx + 3]
                rateIDRUSD = target_td.text
                rateIDRUSD = rateIDRUSD.replace(",", "")
                rateIDRUSD = locale.atof(rateIDRUSD)
                return [(bankName, rateIDRUSD)]
    except:
        traceback.print_exc()
    return bankName, 0

def get_panin(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    case = "!GO_XPATH"
    try:
        if case == "GO_XPATH":
            url = bankInfo["URL_XPATH"]
            xpath = '//*[@id="first"]/tr[1]/td[2]'
            driver = utils.create_chromedriver()
            if not xpath:
                print("[WARNING] Cannot find FxRate from {}".format(name))
                return 0
            utils.get_with_retry(driver, url)
            elem = None
            def get_text(dr):
                return dr.find_element(By.XPATH, xpath) is not None
            WebDriverWait(driver, 10, 0.5).until(get_text)

            elem = driver.find_element(By.XPATH, xpath)
            fxrate = elem.text
            fxrate = fxrate.split(",")[0].replace(".", "")
            driver.quit()
            return [("{}, unit(1)".format(bankName), fxrate)]
        else:
            # 撿到槍, 但 SSL Certification Failed
            r = requests.get(url, verify=False)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, "html.parser")
            tds = soup.find_all("td")
            content = ''.join([td.text for td in tds])
            rateIDRUSD = content.split(":")[1]
            rateIDRUSD = rateIDRUSD.replace(",", "")
            rateIDRUSD = locale.atof(rateIDRUSD)
            return [("{}, unit(10)".format(bankName), rateIDRUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_bca(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", "table table-bordered")
        tds = table.find_all("td")
        for idx, td in enumerate(tds):
            if td.text == "USD":
                target_td = tds[idx+4]
                rateIDRUSD = target_td.text
                # Weird conversion
                rateIDRUSD = rateIDRUSD.replace(".", "")
                rateIDRUSD = rateIDRUSD.replace(",", ".")
                rateIDRUSD = locale.atof(rateIDRUSD)
                return [(bankName, rateIDRUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_bankmandiri(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        
        span = soup.find("span", id="20143USDBUY")    
        rateIDRUSD = span.text.strip()
        rateIDRUSD = rateIDRUSD.replace(",", "")
        rateIDRUSD = locale.atof(rateIDRUSD)
        return [(bankName, rateIDRUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_bankmayapada(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", id="GridView2")
        tds = table.find_all("td")
        for idx, td in enumerate(tds):
            if "USD" in td.text.strip():
                next_td = tds[idx+1]
                rateIDRUSD = next_td.text
                rateIDRUSD = rateIDRUSD.replace(".", "")
                rateIDRUSD = rateIDRUSD.replace(",", ".")
                rateIDRUSD = locale.atof(rateIDRUSD)
                return [(bankName, rateIDRUSD)]
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