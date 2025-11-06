from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from Test_collection import login
import time

BASE_URL = "https://qaproject.elice.io/ai-helpy-chat"

# 일반 로그인 정보
USERNAME = "aloe9426@gmail.com"
PASSWORD = "test_password"

# TEST 로그인 정보
testID = "test_user@example.com"
testPW = "test!9054"
NAME = "김준서"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def TEST_AC_001_login():
    """로그인 테스트"""
    print("=== AC_001: 로그인 테스트 시작 ===")
    try:
        login(driver, USERNAME, PASSWORD)
        print("✅ 로그인 테스트 성공")
    except Exception as e:
        print("❌ 로그인 테스트 실패:", e)
    finally:
        input("테스트 완료 후 엔터를 누르면 브라우저가 닫힙니다.")
        driver.quit()
        
def TEST_AC_001():
    print("=== AC_TC_001: 사이트 접속 확인 ===")
    try:
        # 사이트 접속
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 사이트 접속 성공")
        
        # 가입 버튼 클릭
        create_account_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "a.MuiLink-root[href*='/accounts/signup']"
            ))
        )
        create_account_btn.click()
        
        # 이메일로 가입 버튼 클릭
        email_signup_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.MuiButton-containedPrimary.css-114i87w"))
        )
        email_signup_btn.click()
        
        # 이메일 입력란 확인
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginId']")
                )
            )
        assert email_field.is_displayed()

        # 비밀번호 입력란 확인
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        assert password_field.is_displayed()
        
        print("✅ 테스트 통과: 회원가입 페이지 진입 및 필드 확인 완료")
    
    except Exception as e:
        print("❌ 테스트 실패:", e)
        
def TEST_AC_002():
    print("=== TC_002: 중복 이메일 회원가입 확인 ===")
    try:
        # 사이트 접속
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 사이트 접속 성공")
        
        # 회원가입 / Create account 버튼 클릭 (언어 무관)
        create_account_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "a.MuiLink-root[href*='/accounts/signup']"
            ))
        )
        create_account_btn.click()
        print("✅ 회원가입 버튼 클릭")

        # 이메일로 가입 버튼 클릭 (언어 무관)
        email_signup_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.MuiButton-containedPrimary.css-114i87w"))
        )
        email_signup_btn.click()
        print("✅ 이메일 가입 버튼 클릭")

        # 이메일 입력란 찾기 (name 속성 기반)
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginId']")
                )
            )
        
        email_field.send_keys(testID)

        # 비밀번호 입력란 찾기
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        
        password_field.send_keys(testPW)

        # 이름 입력란 (보통 name 또는 placeholder 활용)
        name_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='fullname']"))
        )
        name_field.clear()
        name_field.send_keys(NAME)

        print("✅ 회원가입 입력란 입력 완료")

        # 7️⃣ 중복 이메일 경고문 확인 (언어 무관 — 클래스 기반)
        email_error = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "p.MuiFormHelperText-root.Mui-error"
            ))
        )

        assert email_error.is_displayed(), "❌ 중복 이메일 에러 메시지가 표시되지 않음"
        print("✅ 테스트 통과: 중복된 이메일 에러 메시지 확인 완료")


        
    except Exception as e:
        print("❌ 테스트 실패:", e) 
    
if __name__ == "__main__":
    TEST_AC_001_login()
    TEST_AC_001()
    TEST_AC_002()
    
