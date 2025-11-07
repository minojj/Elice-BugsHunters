import pytest
from src.utils.helpers import Utils
from src.pages.login_page import LoginFunction
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.usefixtures("driver")

def test_AC_001_login(driver):
    
    print("=== AC_001: 로그인 테스트 시작 ===")
    # 초기화
    helper = Utils(driver)
    login_page = LoginFunction(driver)

    # 1️⃣ 메인 페이지 접속
    login_page.open()

    # 2️⃣ 회원가입 버튼 클릭
    login_page.create_acc()

    # 3️⃣ 이름 입력 필드 표시 여부 확인
    assert login_page.check_name_field(), "❌ 이름 입력 필드가 표시되지 않았습니다."

    print("✅ 테스트 통과: 회원가입 페이지 진입 및 필드 확인 완료")   
        
    

