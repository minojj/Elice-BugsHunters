from time import sleep
import pytest
from src.utils.helpers import Utils
from src.pages.login_page import LoginFunction
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.usefixtures("driver")

def test_AC_001_login(driver):
    print("=== test_AC_001_login 테스트 시작 ===")
    login_page = LoginFunction(driver)

    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ 회원가입 버튼 클릭
    login_page.create_acc()
    # 3️⃣ 이름 입력 필드 표시 여부 확인
    assert login_page.check_name_field(), "❌ 이름 입력 필드가 표시되지 않았습니다."

    print("✅ 테스트 통과: 회원가입 페이지 진입 및 필드 확인 완료")   

def test_AC_002_duplicate_email(driver):
    print("=== test_AC_002_duplicate_email 테스트 시작 ===")
    login_page = LoginFunction(driver)
    
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ 회원가입 버튼 클릭
    login_page.create_acc()
    sleep(1)
    # 3️⃣ 중복된 이메일 입력
    login_page.fill_signup_form("team3@elice.com")
    sleep(1)
    
    # 4️⃣ 경고 문구 검증
    assert login_page.email_error().is_displayed(), "중복 이메일 에러 메시지 표시 x"
    print("✅ 테스트 통과: 중복 이메일 검증 완료")
       
def test_AC_003_negative_login(driver):
    print("=== test_AC_003_negative_login 테스트 시작 ===")
    login_page = LoginFunction(driver)
    
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ negative 로그인 수행
    login_page.login("test_user@example.com", "test_password")
    # 3️⃣ 로그인 확인
    login_page.is_logged_in()
    
def test_AC_004_positive_login(driver):
    print("=== test_AC_004_positive_login 테스트 시작 ===")
   
    login_page = LoginFunction(driver)
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ positive 로그인 수행
    login_page.login("team3@elice.com", "team3elice!@")
    # 3️⃣ 로그인 확인
    login_page.is_logged_in()
    
    

def test_AC_005_login_with_non_email_format(driver):
    print("=== test_AC_005_login_with_non_email_format 테스트 시작 ===")
    login_page = LoginFunction(driver)
    # 1️⃣ 브라우저 초기화(로그인 정보 없애기)
    login_page.clear_login_session()
    sleep(1)
    login_page.remove_history()
    # 2️⃣ 이메일 형식이 아닌 로그인 수행
    login_page.login("test_user", "test_password")
    # 3️⃣ 로그인 확인
    login_page.is_logged_in()
    
    
def test_AC_006_login_with_spaces(driver):
    print("=== test_AC_006_login_with_spaces 테스트 시작 ===")
    login_page = LoginFunction(driver)
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ 이메일 형식이 아닌 로그인 수행
    login_page.login(" team3@elice.com ", " team3elice!@ ")
    # 3️⃣ 로그인 확인
    login_page.is_logged_in()
    
def test_AC_007_logout(driver, logged_in_driver):
    print("=== test_AC_007_logout 테스트 시작 ===")
    login_page = LoginFunction(driver)
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ 로그인
    login_page.login("team3@elice.com", "team3elice!@")
    # 3️⃣ 로그인 검증 
    login_page.is_logged_in()
    # 4️⃣ 프로필 -> 로그아웃 버튼 클릭 
    login_page.logout()
    # 5️⃣ 로그아웃 검증
    assert login_page.logout_check(), "로그아웃 후 로그인 화면으로 돌아오지 않았습니다."
    
    
    
    