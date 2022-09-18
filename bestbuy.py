from selenium import webdriver
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from helper_methods import find_values, get_cookies
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

BEST_BUY_PDP_URL = "https://api.bestbuy.com/click/5592e2b895800000/{sku}/pdp"
BEST_BUY_CART_URL = "https://api.bestbuy.com/click/5592e2b895800000/{sku}/cart"

BEST_BUY_ADD_TO_CART_API_URL = "https://www.bestbuy.com/cart/api/v1/addToCart"
BEST_BUY_CHECKOUT_URL = "https://www.bestbuy.com/checkout/c/orders/{order_id}/"

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "origin": "https://www.bestbuy.com",
}

options = Options()


class BestBuyHandler:
    def __init__(self, sku_id, num_to_buy, headless = False):
        self.sku_id = sku_id
        self.session = requests.Session()
        self.auto_buy = False
        self.num_to_buy = num_to_buy
        self.bought = 0
        self.account = {"username": "XXXXXX", "password": "XXXX"}
        self.webdriver = webdriver.Chrome(executable_path= r'C:\\Users\\Vincent\Documents\\ChromeDriver\\chromedriver.exe', options = options)
        self.webdriver.get('https://www.google.com')
        self.webdriver.get(BEST_BUY_PDP_URL.format(sku = self.sku_id))

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            )
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        response = self.session.get(
            BEST_BUY_PDP_URL.format(sku=self.sku_id), headers=DEFAULT_HEADERS
        )
        print(f"PDP Request: {response.status_code}")
        self.product_url = response.url
        print(f"Product URL: {self.product_url}")

        self.session.get(self.product_url)
        print(f"Product URL Request: {response.status_code}")
    
    def in_stock(self):
        print("Checking stock")
        url = "https://www.bestbuy.com/api/tcfb/model.json?paths=%5B%5B%22shop%22%2C%22scds%22%2C%22v2%22%2C%22page%22%2C%22tenants%22%2C%22bbypres%22%2C%22pages%22%2C%22globalnavigationv5sv%22%2C%22header%22%5D%2C%5B%22shop%22%2C%22buttonstate%22%2C%22v5%22%2C%22item%22%2C%22skus%22%2C{}%2C%22conditions%22%2C%22NONE%22%2C%22destinationZipCode%22%2C%22%2520%22%2C%22storeId%22%2C%22%2520%22%2C%22context%22%2C%22cyp%22%2C%22addAll%22%2C%22false%22%5D%5D&method=get".format(
            self.sku_id
        )
        response = self.session.get(url, headers=DEFAULT_HEADERS)
        print(f"Stock check response code: {response.status_code}")

        try:
            response_json = response.json()
            item_json = find_values(
                json.dumps(response_json), "buttonStateResponseInfos"
            )
            item_state = item_json[0][0]["buttonState"]
            print(f"Item state is: {item_state}")
            if item_state == "ADD_TO_CART":
                return 1
            else:
                return 0
        except Exception as e:
            print("Error parsing json. Using string search to determine state.")

            if "ADD_TO_CART" in response.text:
                print("Item is in stock!")
                return 1
            else:
                print("Item is out of stock")
                return 0

    def add_to_cart(self):
        flag = True
        while flag:
            try:
                self.webdriver.find_element_by_class_name("fulfillment-add-to-cart-button").click()
               
                flag = False
            except:
                flag = True
        
        
        self.webdriver.get("https://www.bestbuy.com/cart")
        try:
            self.webdriver.find_element_by_xpath('//*[@id="cartApp"]/div[2]/div[1]/div/div/span/div/div[2]/div[1]/section[2]/div/div/div[3]/div/a')
            self.add_to_cart()
        except:
            self.checkout()
            self.login()
            self.payment()
            self.buy()
            self.screenshot()
    '''
    def checkout(self):
        flag = True
        while flag:
            try:
                checkout = self.webdriver.find_element_by_xpath('//*[@id="cartApp"]/div[2]/div[1]/div/div/span/div/div[2]/div[1]/section[2]/div/div/div[3]/div/div[2]/button').click()
                flag = False
            except:
                flag = True

    def login(self):
        flag = True
        while flag:
            try:
                self.webdriver.find_element_by_xpath('//*[@id="email"]').send_keys(self.account['username'])
                self.webdriver.find_element_by_xpath('//*[@id="btnNext"]').click()
                flag = False
            except:
                flag = True
        
        flag2 = True
        while flag2:
            try:
                element = self.webdriver.find_element_by_xpath('//*[@id="password"]')
                action = ActionChains(self.webdriver)
                action.move_to_element(element).click()
                time.sleep(1)
                action.send_keys_to_element(element,"")
                action.send_keys_to_element(element, "XXXX")
                time.sleep(1)
                action.perform()
                time.sleep(1)
                self.webdriver.find_element_by_xpath('//*[@id="btnLogin"]').click()
                flag2 = False
            except:
                flag2 = True
        
        flag3 = True
        while flag3:
            try:
                self.webdriver.find_element_by_xpath('//*[@id="payment-submit-btn"]').click()
                flag3 = False
            except:
                flag3 = True

    def buy(self):
        flag = True
        while flag:
            try:
                self.webdriver.find_elements_by_xpath('//*[@id="checkoutApp"]/div[2]/div[1]/div[1]/main/div[2]/div[2]/div/div[3]/div[5]/div/button').click()
                time.sleep(1)
                flag = False
            except:
                flag = True
    
    def screenshot(self):
        self.bought += 1
        self.webdriver.get_screenshot_as_png()

    def repeat(self):
        if(self.bought < self.num_to_buy):
            self.add_to_cart()
            self.checkout()
            #self.payment()
            #self.screenshot()
    '''
    def checkout(self):
        flag = True
        while flag:
            try:
                self.webdriver.find_element_by_xpath('//*[@id="cartApp"]/div[2]/div[1]/div/div/span/div/div[2]/div[1]/section[2]/div/div/div[3]/div/div[1]/button').click()
                flag = False
            except:
                flag = True
        
    
    def login(self):
        flag = True
        while flag:
            try:
                self.webdriver.find_element_by_xpath('//*[@id="fld-e"]').send_keys(self.account['username'])
                self.webdriver.find_element_by_xpath('//*[@id="fld-p1"]').send_keys(self.account['password'])
                sign_in = self.webdriver.find_element_by_xpath('/html/body/div[1]/div/section/main/div[1]/div/div/div/div/form/div[3]/button').click()
                flag = False
            except:
                flag = True

    def payment(self):
        flag = True
        while flag:
            try:

                element = self.webdriver.find_element_by_xpath('//*[@id="credit-card-cvv"]')

                action = ActionChains(self.webdriver)
                action.move_to_element(element).click()
                time.sleep(1)
                action.send_keys_to_element(element,"")
                action.send_keys_to_element(element,000)
                time.sleep(1)
                action.perform()
                time.sleep(1)

                flag = False
            except:
                flag = True

    def buy(self):
        flag = True
        while flag:
            try:
                self.webdriver.find_elements_by_xpath('//*[@id="checkoutApp"]/div[2]/div[1]/div[1]/main/div[2]/div[2]/div/div[3]/div[5]/div/button').click()
                time.sleep(1)
                flag = False
            except:
                flag = True

    def screenshot(self):
        self.webdriver.save_screenshot(f'{self.sku_id}.png')
        self.webdriver.close()
    
        

        