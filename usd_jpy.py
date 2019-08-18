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
                "SWIFT": "BOJPJPJTXXX",
                "NAME": "Bank of Japan.",
                "URL": "https://www.boj.or.jp/en/statistics/market/forex/fxdaily/fxlist/",
                "ENABLED": True,
                "IMPLEMENTATION": "get_boj"
            },

            {
                "SWIFT": "BOTKJPJTXXX",
                "NAME": "MUFG Bank, LTD.",
                "URL": "http://www.bk.mufg.jp/gdocs/kinri/list_j/kinri/kawase.html",
                "ENABLED": True,
                "IMPLEMENTATION": "get_mufg"
            },

            {
                "SWIFT": "MHCBJPJTXXX",
                "NAME": "Mizuho Bank, Ltd.",
                "URL": "https://www.mizuhobank.co.jp/market/csv/BK01.csv",
                "ENABLED": True,
                "IMPLEMENTATION": "get_mizuho"
            },

            {
                "SWIFT": "SMTCJPJTXXX",
                "NAME": "SMBC Trust Bank Ltd.",
                "URL": "https://www.smbctb.co.jp/common/xml/FX_INT.xml",
                "ENABLED": True,
                "IMPLEMENTATION": "get_smbc"
            },
]

def get_boj(url, bankInfo=None):

    def get_latest_pdf_response():
        offset = 0
        while True and offset < 3:
            target = date.today() - timedelta(offset)
            fileName = "fx{}.pdf".format(target.strftime("%y%m%d"))
            r = requests.get(url+fileName, stream=True)
            if r.status_code == 200:
                return r
            else:
                offset += 1
        return None

    bankName = bankInfo["NAME"]
    try:
        downloadedName = "./boj.pdf"
        r = get_latest_pdf_response()
        if r is not None:
            with open(downloadedName, "wb") as fd:
                for chunk in r.iter_content(2048):
                    fd.write(chunk)

            rateJPYUSD = parse(downloadedName, "boj")
            os.remove(downloadedName)
            return [(bankName, rateJPYUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_mufg(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        tds = soup.find_all("td")
        for idx, td in enumerate(tds):
            text = td.text.strip().rstrip()
            if text.startswith("USD"):
                target_td = tds[idx + 4]
                rateJPYUSD = target_td.text
                rateJPYUSD = rateJPYUSD.replace(",", "")
                rateJPYUSD = locale.atof(rateJPYUSD)
                return [(bankName, rateJPYUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_mizuho(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        import csv
        r = requests.get(url)
        cr = csv.reader(r.text.splitlines(), delimiter=',')
        target_idx = -1
        for row in list(cr):
            if target_idx != -1:
                rateJPYUSD = row[target_idx]
                rateJPYUSD = rateJPYUSD.replace(",", "")
                rateJPYUSD = locale.atof(rateJPYUSD)
                return [(bankName, rateJPYUSD)]
            for idx, elem in enumerate(row):
                if elem.startswith("BUYING：TTB"):
                    target_idx = idx
                    break
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def get_smbc(url, bankInfo=None):
    bankName = bankInfo["NAME"]
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "xml")
        cols = soup.find_all("col")
        for idx, col in enumerate(cols):
            text = col.text.strip().rstrip()
            if text == "US Dollar (USD)":
                target = cols[idx + 3]
                rateJPYUSD = target.text
                rateJPYUSD = rateJPYUSD.replace(",", "")
                rateJPYUSD = locale.atof(rateJPYUSD)
                return [(bankName, rateJPYUSD)]
    except:
        traceback.print_exc()
    return [(bankName, 0)]

def parse(path, case):
    from pdfminer.pdfparser import PDFParser,PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import PDFPageAggregator
    from pdfminer.layout import LTTextBoxHorizontal,LAParams
    from pdfminer.pdfinterp import PDFTextExtractionNotAllowed


    def get_boj_rate(layout):
        expectated = ["US dollar", "円", "Yen"]
        obtained = []
        for x in layout:
            if (isinstance(x, LTTextBoxHorizontal)):
                results = x.get_text().strip()
                if len(obtained) >= 3 and obtained[-3:] == expectated:
                    rateJPYUSD = results
                    nJPY = rateJPYUSD.split(".")[0]
                    fJPYLow = rateJPYUSD.split(".")[1].split("-")[0]
                    fJPYHigh = rateJPYUSD.split(".")[1].split("-")[1]
                    rateJPYUSDL = "{}.{}".format(nJPY, fJPYLow)
                    rateJPYUSDH = "{}.{}".format(nJPY, fJPYHigh)
                    rateJPYUSD = round((locale.atof(rateJPYUSDL) + locale.atof(rateJPYUSDH)) / 2.0, 4)
                    return rateJPYUSD
                if results == "US dollar":
                    obtained.append(results)
                if results == "円":
                    obtained.append(results)
                if results == "Yen":
                    obtained.append(results)
        return 0

    with open(path, 'rb') as fd:
        # Create a new Document
        doc = PDFDocument()
        # Create a parser then set the file descriptor to it
        praser = PDFParser(fd)
        # Link parser and document
        praser.set_document(doc)
        doc.set_parser(praser)
        doc.initialize()

        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            # Create Layout Params/ Resource manager/ Interpreter to start
            # the pdf parsing procedure.
            laparams = LAParams()
            rsrcmgr = PDFResourceManager()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            foundUSD = False
            for page in doc.get_pages():
                interpreter.process_page(page)
                layout = device.get_result()
                if case == "boj":
                    return get_boj_rate(layout)
                break
    return 0

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