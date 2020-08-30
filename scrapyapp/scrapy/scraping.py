import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from register.models import User


class Scrapy:

    def __init__(self):
        self.driver = webdriver.Chrome()

    @classmethod
    def selenium_get(self, url):
        self.driver.get(url)

    @classmethod
    def get_dom(self, query):
        dom = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, query)))
        return dom

    def selenium_close(self):
        self.driver.close()


class Register:

    def start_login(self, url, pk):
        url = url
        scrapy = Scrapy()
        scrapy.selenium_get(url)
        user_dom = scrapy.get_dom('#user')
        user = User.objects.get(pk=pk)
        user_dom.send_keys(user.name)
        pw = scrapy.get_dom('#pass')
        pw.send_keys(os.getenv("PASSWORD"))
        btn = Scrapy.get_dom('#loginForm input[type=submit]')
        btn.click()

    def start_regist(self, url):
        url = url
        scrapy = Scrapy()
        scrapy.selenium_get(url)
        user_dom = scrapy.get_dom('#user')
        user_dom.send_keys(os.getenv("USER"))
        pw = scrapy.get_dom('#email')
        pw.send_keys(os.getenv("Email"))
        btn = scrapy.get_dom('#loginForm input[type=submit]')
        btn.click()
