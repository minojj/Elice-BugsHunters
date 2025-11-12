import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# pyautogui 조건부 import (CI 환경에서는 PYAUTOGUI_OFF=1 설정)
if os.environ.get("PYAUTOGUI_OFF") != "1":
    import pyautogui
else:
    pyautogui = None

class Utils:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def wait_for(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )