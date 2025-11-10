from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src.utils.helpers import Utils

class customAgentPage :
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"

    def open(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 커스텀 에이전트 메인 페이지 접속 성공")