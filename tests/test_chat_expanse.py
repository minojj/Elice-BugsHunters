import time
import pytest
from pathlib import Path
from src.pages.chat_expanse_page import ChatExpansePage

TEST_FILES_DIR = Path(__file__).parent.parent /"resources" / "testdata"
TEST_FILENAME = TEST_FILES_DIR / "git.pdf"
TEST_EXENAME = TEST_FILES_DIR / "npp.8.8.7.Installer.x64.exe"


def test_ce_001_quiz(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_quiz_and_send()
    assert result, "❌ 퀴즈 생성 및 전송 프로세스 실패"

def test_ce_002_quiz_empty(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_quiz_and_send_empty()
    assert result, "✅CE-002 : 빈칸 퀴즈 생성이 허용되었습니다!"

def test_ce_003_quiz_special_chars(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_quiz_and_send_special_chars()
    assert result, "✅CE-003 : 특수문자 퀴즈 생성이 허용되었습니다!"

def test_ce_004_quiz_no_type(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_quiz_and_send_no_type()
    assert result, "✅CE-004 : 난이도 혹은 주관식, 객관식을 명시하지 않은 퀴즈 생성이 허용되었습니다!"

def test_ce_005_ppt(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_ppt_and_send()
    assert result, "❌ PPT 생성 및 전송 프로세스 실패"
 
def test_ce_006_image_text(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_image_and_send()
    assert result, "❌ 이미지 생성 및 전송 프로세스 실패"

def test_ce_007_image_file(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_image_and_send_file(str(TEST_FILENAME.absolute()),)
    assert result, "❌ 이미지 생성 및 전송 프로세스 실패"
    
def test_ce_008_google_search(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.google_search_and_send()
    assert result, "❌ 구글 검색 및 전송 프로세스 실패"

def test_ce_009_deep_dive(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.deep_dive_and_send()
    assert result, "❌ 심층 조사 및 전송 프로세스 실패"

def test_ce_010_file_upload(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.upload_file_and_send(str(TEST_FILENAME.absolute()),)
    assert result, "❌ 파일 업로드 및 전송 프로세스 실패"
     
def test_ce_011_file_upload_expect_failure(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.upload_file_expect_failure(str(TEST_EXENAME.absolute()),)
    assert result is True, "❌ CE-011 실패: 위험 파일 업로드가 허용되었습니다!"

def test_ce_012_file_upload_new_chat(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.upload_file_and_send_new_chat(str(TEST_FILENAME.absolute()),)
    assert result, "❌ 파일 업로드 및 전송 프로세스 실패"

def test_ce_013_quiz_empty_new_chat(logged_in_driver):
    page = ChatExpansePage(logged_in_driver)
    result = page.create_quiz_and_send_empty_new_chat()
    assert result, "✅CE-013 : 빈칸 퀴즈 생성이 허용되었습니다!"
