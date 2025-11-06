from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

BASE_URL = "https://qatrack.elice.io/ai-helpy-chat"

# 일반 로그인 정보
USERNAME = "test_user@example.com"
PASSWORD = "test_password"
NAME = "김준서"

#앞 뒤 공백 로그인 정보
spaceID = "test_user@example.com"
spacePW = "test!9054"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def tc_001_signup():
    print("=== TC_001: 사이트 접속 확인 ===")
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 사이트 접속 성공")
        
       
        create_account_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Create account"))
        )
        create_account_link.click()

        email_signup_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create account with email')]")))
        email_signup_btn.click()
        
        
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email']"))
        )
        assert email_field.is_displayed(), "이메일 입력란 없음"

        # 6️⃣ 비밀번호 입력란 확인
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
        )
        assert password_field.is_displayed(), "비밀번호 입력란 없음"
        
        print("✅ 테스트 통과: 회원가입 페이지 진입 및 필드 확인 완료")
    
    except Exception as e:
        print("❌ 테스트 실패:", e)
        
        
def tc_002_signup02():
    print("=== TC_002: 사이트 접속 확인 ===")
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 사이트 접속 성공")
        
        create_account_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Create account"))
        )
        create_account_link.click()

        email_signup_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create account with email')]")))
        email_signup_btn.click()
        
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email']"))
        )
        email_field.send_keys(spaceID)
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
        )
    
        password_field.send_keys(spacePW)
        
        name_field = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Name']"))
        )
        name_field.send_keys(NAME)
        
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")

        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
        
        signup_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create account')]")))
        signup_btn.click()
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Name']"))
        )

        current_url = driver.current_url
        if "verification/identification" in current_url:
            print("✅ 이메일 인증 페이지로 이동됨 — 테스트 종료")
            input("테스트 완료! 브라우저를 닫으려면 엔터를 누르세요.")
            driver.quit()

        
    except Exception as e:
        print("❌ 테스트 실패:", e) 
    
if __name__ == "__main__":
    tc_001_signup()
    tc_002_signup02()
    
