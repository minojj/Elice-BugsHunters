from math import log
import pytest, os
from src.pages.login_page import LoginFunction
from dotenv import load_dotenv

load_dotenv()
@pytest.mark.usefixtures("driver")
def test_AC_001_login(driver):
    print("\n=== test_AC_001_login 테스트 시작 ===")
    login_page = LoginFunction(driver)

    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ 회원가입 버튼 클릭
    login_page.create_acc()
    # 3️⃣ 이름 입력 필드 표시 여부 확인
    assert login_page.check_name_field(), "❌ 이름 입력 필드가 표시되지 않았습니다."  

def test_AC_002_duplicate_email(driver):
    print("\n=== test_AC_002_duplicate_email 테스트 시작 ===")
    login_page = LoginFunction(driver)
    email = os.getenv("MAIN_EMAIL")
    
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ 회원가입 버튼 클릭
    login_page.create_acc()
    # 3️⃣ 중복된 이메일 입력
    login_page.fill_signup_form(email)
    # 4️⃣ 경고 문구 검증
    assert login_page.email_error() is not None, "❌ 중복 이메일 에러 메시지가 표시되지 않았습니다."
       
def test_AC_003_negative_login(driver):
    print("\n=== test_AC_003_negative_login 테스트 시작 ===")
    login_page = LoginFunction(driver)
    
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ negative 로그인 수행
    login_page.login("test_user@example.com", "test_password")
    # 3️⃣ 로그인 확인
    assert not login_page.is_logged_in(), "로그인에 성공하면 안 됩니다."
    
def test_AC_004_positive_login(logged_in_driver):
    login_page = LoginFunction(logged_in_driver)
    # 로그인 확인
    assert login_page.is_logged_in(), "로그인에 실패했습니다."

def test_AC_005_login_with_non_email_format(driver):
    print("\n=== test_AC_005_login_with_non_email_format 테스트 시작 ===")
    login_page = LoginFunction(driver)
    # 1️⃣ 브라우저 초기화(로그인 정보 없애기)
    login_page.clear_login_session()
    # 2️⃣ 이메일 형식이 아닌 로그인 수행
    login_page.login("test_user", "test_password")
    # 3️⃣ 로그인 확인
    assert not login_page.is_logged_in(), "로그인에 성공하면 안 됩니다."
    
def test_AC_006_login_with_spaces(driver):
    print("\n=== test_AC_006_login_with_spaces 테스트 시작 ===")
    login_page = LoginFunction(driver)
    # 1️⃣ 메인 페이지 접속
    login_page.open()
    # 2️⃣ 공백포함 로그인 수행
    login_page.login(" test@elice.com ", "testelice!@ ")
    # 3️⃣ 로그인 실패 확인 (예: 에러 메시지 또는 로그인 상태가 아님을 확인)
    assert not login_page.is_logged_in(), "공백이 포함된 이메일/비밀번호로 로그인이 성공하면 안 됩니다."
    
def test_AC_007_logout(logged_in_driver):
    login_page = LoginFunction(logged_in_driver)
    login_page.logout()
    # 로그아웃 검증
    assert login_page.logout_check(), "로그아웃 후 로그인 화면으로 돌아오지 않았습니다."
    
    
    
    
