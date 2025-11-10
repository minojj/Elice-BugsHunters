import pytest
from pages.chat_expance_page import Chat_Expance


# 테스트 상수
TEST_FILENAME = r"C:\Users\josun\Downloads\git.pdf"
TEST_USERNAME = "team3@elice.com"
TEST_PASSWORD = "team3elice!@"


def test_ce_001(driver):
    """
    CE-001: 파일 업로드 및 AI 응답 테스트
    테스트 시나리오:
    1. 로그인
    2. 플러스 버튼 클릭
    3. 파일 업로드 메뉴 선택
    4. PDF 파일 업로드
    5. 엔터키로 전송
    6. AI 응답 대기
    """
    # Page Object 생성
    page = Chat_Expance(driver)
    
    # 로그인
    page.login(TEST_USERNAME, TEST_PASSWORD)
    
    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_and_send(TEST_FILENAME, wait_time=30)
    
    # 검증
    assert result, "❌ 파일 업로드 및 전송 프로세스 실패"
    print("✅ CE-001 테스트 통과!")