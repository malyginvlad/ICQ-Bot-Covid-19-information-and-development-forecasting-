from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import xml.etree.ElementTree as ET
from newspaper import Article
import pandas as pd
import re
import time
from selenium.webdriver.chrome.options import Options as chr_opt
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

def load_data():
    chrome_options = chr_opt()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/home/morozov/icq_top/chromedriver', chrome_options=chrome_options)
    # ссылка из своего репозитория на dataset COVID-19 
    url = 'https://datalens.yandex.ru/dashboards/qd5k7h666xbsm?tab=XV'
    driver.get(url)
    account = driver.find_element_by_xpath('//div[@class="passp-form-field__input"]/input')
    login = '' # вводим свой логин от yandex
    account.send_keys(login)
    button = driver.find_element_by_xpath('//div[@class="passp-button passp-sign-in-button"]/button')
    button.click()
    time.sleep(2)
    password = driver.find_element_by_xpath('//div[@class="passp-form-field__input"]/input')
    password = '' # вводим свой пароль от yandex
    password.send_keys(password)
    button = driver.find_element_by_xpath('//div[@class="passp-button passp-sign-in-button"]/button')
    button.click()
    time.sleep(30)
    button = driver.find_element_by_xpath('//div[@class="dropdown2 chartkit-menu__button"]/button')
    button.click()
    button = driver.find_element_by_xpath('//li[@class="menu__list-item"]/div')
    button.click()
    button = driver.find_element_by_xpath('//label[@class="control radiobox__radio radio-button__radio"]/input')
    button.click()
    button = driver.find_element_by_xpath('//button[@class="control button2 button2_view_default button2_tone_default button2_size_m button2_theme_action button2_width_max"]')
    button.click()
    time.sleep(10)
    driver.quit()