# coding=UTF-8
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

PHANTONJS_DRIVER = None
CHROME_DRIVER = None
def create_phantomjs():
    global PHANTONJS_DRIVER
    if PHANTONJS_DRIVER is None:
        if is_local_dev_env():
            PHANTONJS_DRIVER = webdriver.PhantomJS(executable_path="./phantomjs211/bin/phantomjs")
        else:
            PHANTONJS_DRIVER = webdriver.PhantomJS(executable_path="./vendor/phantomjs/bin/phantomjs")
    PHANTONJS_DRIVER.implicitly_wait(5)
    return PHANTONJS_DRIVER

def create_chromedriver(args=[]):
    global CHROME_DRIVER
    options = webdriver.ChromeOptions()

    profile = {"plugins.plugins_list": [{"enabled": False,
                                         "name": "Chrome PDF Viewer"}],
               "download.default_directory": "./",
               "download.extensions_to_open": ""}
    options.add_experimental_option("prefs", profile)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # options.add_argument('headless')
    options.addArguments("--disable-extensions");
    options.addArguments("--disable-dev-shm-usage");
    options.add_argument('window-size=1200x600')
    for arg in args:
        options.add_argument(arg)

    if CHROME_DRIVER is None:
        if is_local_dev_env():
            CHROME_DRIVER = webdriver.Chrome(executable_path="./chromedriver",
                                             chrome_options=options)
        else:
            CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
            chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', "chromedriver")
            options.binary_location = chrome_bin
            CHROME_DRIVER = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                                             chrome_options=options)
    CHROME_DRIVER.implicitly_wait(5)
    return CHROME_DRIVER

def get_with_retry(driver, url, numRetry=2):
    for _ in range(numRetry):
        try:
            driver.get(url)
            return True
        except TimeoutException:
            continue
    return False

def find_element_by_xpath_safely(driver, xpath):
    is_ok = True
    elem = None
    try:
        elem = driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        is_ok = False
    return is_ok, elem

def is_local_dev_env():
    import getpass
    return getpass.getuser() == 'kilikkuo'