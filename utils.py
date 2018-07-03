# coding=UTF-8

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
    for arg in args:
        options.add_argument(arg)
    
    if CHROME_DRIVER is None:
        if is_local_dev_env():
            CHROME_DRIVER = webdriver.PhantomJS(executable_path="./chromedriver")
        else:
            CHROME_DRIVER = webdriver.PhantomJS(executable_path="./.chromedriver/bin/chromedriver")
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