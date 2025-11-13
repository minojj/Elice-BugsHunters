import time
import pytest
from pathlib import Path
# from src.pages.login_page import LoginFunction
from src.pages.chat_expance_page import ChatExpancePage

TEST_FILES_DIR = Path(__file__).parent.parent /"resources" / "testdata"
TEST_FILENAME = TEST_FILES_DIR / "git.pdf"
TEST_EXENAME = TEST_FILES_DIR / "npp.8.8.7.Installer.x64.exe"


def test_ce_001(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_and_send(str(TEST_FILENAME.absolute()), wait_time=30)
    # 검증
    assert result, "❌ 파일 업로드 및 전송 프로세스 실패"
    print("✅ CE-001 테스트 통과!")   


def test_ce_002(logged_in_driver):
  
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_and_send(str(TEST_EXENAME.absolute()), wait_time=10)

    # 검증: 위험 파일 업로드가 방지(실패)되었는지 확인 (result가 False일 때 통과)
    assert result is False, "❌ CE-002 실패: 위험 파일 업로드가 허용되었습니다!"
    error_message = page.get_error_message()
    assert "허용되지 않는" in error_message or "지원하지 않는" in error_message, "❌ CE-002 실패: 예상된 오류 메시지가 표시되지 않았습니다."
    print("✅ CE-002 테스트 통과! (위험 파일 업로드 방지 확인)")

def test_ce_003_000(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send(wait_time=30)
    # 검증
    assert result, "❌ 퀴즈 생성 및 전송 프로세스 실패"
    print("✅ CE-003 테스트 통과!")

def test_ce_003_001(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_empty(wait_time=10)
    # 검증
    assert result, "✅CE-003_001 : 빈칸 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-003_001 테스트 통과! (빈칸 퀴즈 생성 반응확인)")

def test_ce_003_002(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_special_chars(wait_time=10)
    # 검증
    assert result, "✅CE-003_002 : 특수문자 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-003_002 테스트 통과! (특수문자 퀴즈 생성 확인)")

def test_ce_003_003(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_no_type(wait_time=10)
    # 검증
    assert result, "✅CE-003_003 : 난이도 혹은 주관식, 객관식을 명시하지 않은 퀴즈 생성이 허용되었습니다!"
    print("✅ CE_003_003 테스트 통과! (난이도 혹은 주관식, 객관식을 명시하지 않은 퀴즈 생성 확인)")

def test_ce_004(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # PPT 생성 및 전송 (전체 프로세스)
    result = page.create_ppt_and_send(wait_time=60)
    # 검증
    assert result, "❌ PPT 생성 및 전송 프로세스 실패"
    print("✅ CE-004 테스트 통과!")

    ###문제 1 섹션부분 기입 안됨 수정 필요###
    ###문제 2 기존 입력값 지우기 필요###

def test_ce_005(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 이미지 생성 및 전송 (전체 프로세스)
    result = page.create_image_and_send(wait_time=30)
    # 검증
    assert result, "❌ 이미지 생성 및 전송 프로세스 실패"

def test_ce_006(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 구글 검색 및 전송 (전체 프로세스)
    result = page.google_search_and_send(wait_time=30)
    # 검증
    assert result, "❌ 구글 검색 및 전송 프로세스 실패"
    print("✅ CE-006 테스트 통과!")

def test_ce_007(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 심층 조사 및 전송 (전체 프로세스)
    result = page.deep_dive_and_send(wait_time=30)
    # 검증
    assert result, "❌ 심층 조사 및 전송 프로세스 실패"
    print("✅ CE-007 테스트 통과!")

####심층 조사 생성하기 버튼 오류 수정 필요#####
    