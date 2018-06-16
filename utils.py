# coding=UTF-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

def create_chromedriver(args=[]):
    options = webdriver.ChromeOptions()
    for arg in args:
        options.add_argument(arg)
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=options)
    return driver

def get_with_retry(driver, url, numRetry=3):
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