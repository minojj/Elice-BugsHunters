from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#추가 import 파일업로드 창 입력 (pip install pyautogui)


class Utils:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def wait_for(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )