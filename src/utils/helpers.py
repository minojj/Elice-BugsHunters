from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Utils:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def wait_for(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    
    def perform_gui_action(self, x, y):
        # ✅ 'pyautogui' 임포트 시점을 함수 호출 순간으로 늦춥니다.
        # 이 함수가 호출될 때쯤이면, Xvfb 액션이 DISPLAY 변수 설정을 완료했을 것입니다.
        import pyautogui 
        pyautogui.click(x, y)
        print(f"Clicked at ({x}, {y}) using pyautogui.")