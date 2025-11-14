import time
import pytest
from pathlib import Path
# from src.pages.login_page import LoginFunction
from src.pages.chat_expance_page import ChatExpancePage

TEST_FILES_DIR = Path(__file__).parent.parent /"resources" / "testdata"
TEST_FILENAME = TEST_FILES_DIR / "git.pdf"
TEST_EXENAME = TEST_FILES_DIR / "npp.8.8.7.Installer.x64.exe"


def test_ce_001_quiz(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send(wait_time=30)
    # 검증
    assert result, "❌ 퀴즈 생성 및 전송 프로세스 실패"
    print("✅ CE-001 테스트 통과!")

def test_ce_002_quiz_empty(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_empty(wait_time=10)
    # 검증
    assert result, "✅CE-002 : 빈칸 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-002 테스트 통과! (빈칸 퀴즈 생성 반응확인)")

def test_ce_003_quiz_special_chars(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_special_chars(wait_time=10)
    # 검증
    assert result, "✅CE-003 : 특수문자 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-003 테스트 통과! (특수문자 퀴즈 생성 확인)")

def test_ce_004_quiz_no_type(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_no_type(wait_time=10)
    # 검증
    assert result, "✅CE-004 : 난이도 혹은 주관식, 객관식을 명시하지 않은 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-004 테스트 통과! (난이도 혹은 주관식, 객관식을 명시하지 않은 퀴즈 생성 확인)")

def test_ce_005_ppt(logged_in_driver):
   
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # PPT 생성 및 전송 (전체 프로세스)
    result = page.create_ppt_and_send()
    # 검증
    assert result, "❌ PPT 생성 및 전송 프로세스 실패"
    print("✅ CE-005 테스트 통과!")
 
def test_ce_006_image_text(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 이미지 생성 및 전송 (전체 프로세스)
    result = page.create_image_and_send(wait_time=30)
    # 검증
    assert result, "❌ 이미지 생성 및 전송 프로세스 실패"
    print("✅ CE-006 테스트 통과!")

def test_ce_007_image_file(logged_in_driver):
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 이미지 생성 및 전송 (예외 케이스)
    result = page.create_image_and_send_file(str(TEST_FILENAME.absolute()), wait_time=30)
    # 검증
    assert result, "❌ 이미지 생성 및 전송 프로세스 실패"
    print("✅ CE-007 테스트 통과!")
    
def test_ce_008_google_search(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 구글 검색 및 전송 (전체 프로세스)
    result = page.google_search_and_send(wait_time=30)
    # 검증
    assert result, "❌ 구글 검색 및 전송 프로세스 실패"
    print("✅ CE-008 테스트 통과!")

def test_ce_009_deep_dive(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 심층 조사 및 전송 (전체 프로세스)
    result = page.deep_dive_and_send(wait_time=30)
    # 검증
    assert result, "❌ 심층 조사 및 전송 프로세스 실패"
    print("✅ CE-009 테스트 통과!")

def test_ce_010_file_upload(logged_in_driver):

    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_and_send(str(TEST_FILENAME.absolute()), wait_time=30)
    # 검증
    assert result, "❌ 파일 업로드 및 전송 프로세스 실패"
    print("✅ CE-010 테스트 통과!")  
     
def test_ce_011_file_upload_expect_failure(logged_in_driver):
  
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_expect_failure(str(TEST_EXENAME.absolute()), wait_time=10)

    # 검증: 위험 파일 업로드가 방지(실패)되었는지 확인 (result가 False일 때 통과)
    assert result is True, "❌ CE-011 실패: 위험 파일 업로드가 허용되었습니다!"
    print("✅ CE-011 테스트 통과!")

def test_ce_012_file_upload_new_chat(logged_in_driver):
    
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_and_send_new_chat(str(TEST_FILENAME.absolute()), wait_time=30)
    # 검증
    assert result, "❌ 파일 업로드 및 전송 프로세스 실패"
    print("✅ CE-012 테스트 통과!")

def test_ce_013_quiz_empty_new_chat(logged_in_driver):
    # Page Object 생성
    page = ChatExpancePage(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_empty_new_chat(wait_time=10)
    # 검증
    assert result, "✅CE-013 : 빈칸 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-013 테스트 통과! (빈칸 퀴즈 생성 반응확인)")
    