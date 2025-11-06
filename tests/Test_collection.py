from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL
BASE_URL = "https://qatrack.elice.io/ai-helpy-chat"

# 카카오 로그인 정보
USERNAME = "aloe9426@gmail.com"
PASSWORD = "test_password"

# 이메일 로그인 정보
testID = "test_user@example.com"
testPW = "test!9054"
NAME = "김준서"

# 이메일 입력
Email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginId']")
                )
            )
# 비밀번호 입력
Password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )

def login(driver, username, password):
    """로그인 공통 함수"""
    driver.get(BASE_URL)
    
    # 아이디 입력 필드 찾고 입력
    Email_input.send_keys(USERNAME)

    # 비밀번호 입력 필드 찾고 입력
    Password_input.send_keys(PASSWORD)

    # 로그인 버튼 클릭
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    