from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

BASE_URL = "https://qatrack.elice.io/ai-helpy-chat"

USERNAME = "aloe9426@gmail.com"
PASSWORD = "test_password"


def login(driver, username, password):
    """로그인 공통 함수"""
    driver.get(BASE_URL)

    # 이메일 입력 필드 대기 후 입력
    Email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginId']"))
    )
    Email_input.send_keys(username)

    # 비밀번호 입력 필드 대기 후 입력
    Password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
    )
    Password_input.send_keys(password)

    # 로그인 버튼 클릭
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_btn.click()

    print(" 로그인 시도 완료")