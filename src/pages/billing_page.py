import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from .base_page import BasePage




class CreditPage(BasePage):

    locators = {}
    
    def __init__(self, driver):
        super().__init__(driver)





class UsagePage(BasePage):

    locators = {}
    
    def __init__(self, driver):
        super().__init__(driver)