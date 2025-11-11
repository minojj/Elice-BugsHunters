# test_ce.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from pages.chat_expance_page import Chat_Expance
import time

# 테스트 상수
TEST_FILENAME = r"C:\Users\josun\Downloads\git.pdf"
TEST_EXENAME = r"C:\Users\josun\Downloads\Docker Desktop Installer.exe"
TEST_USERNAME = "team3@elice.com"
TEST_PASSWORD = "team3elice!@"


def test_ce_001(logged_in_driver):
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
    page = Chat_Expance(logged_in_driver)
    
    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_and_send(TEST_FILENAME, wait_time=30)
    # 검증
    assert result, "❌ 파일 업로드 및 전송 프로세스 실패"
    print("✅ CE-001 테스트 통과!")   
    
def test_ce_002(logged_in_driver):
    """
    CE-002: 위험 파일 업로드 차단 테스트
    
    테스트 시나리오:
    1. 로그인 (logged_in_driver가 자동 처리)
    2. 플러스 버튼 클릭
    3. 파일 업로드 메뉴 선택
    4. .exe 파일 업로드 시도
    5. 업로드 차단 확인
    """
    # Page Object 생성
    page = Chat_Expance(logged_in_driver)

    # 파일 업로드 및 전송 (전체 프로세스)
    result = page.upload_file_and_send(TEST_EXENAME, wait_time=10)

    # 검증: 위험 파일 업로드가 방지(실패)되었는지 확인 (result가 False일 때 통과)
    assert result is False, "❌ CE-002 실패: 위험 파일 업로드가 허용되었습니다!"
    print("✅ CE-002 테스트 통과! (위험 파일 업로드 방지 확인)")

def test_ce_003_000(logged_in_driver):
    """
    CE-003: 퀴즈생성 테스트
    테스트 시나리오
    1.로그인
    2.플러스 버튼 클릭
    3.퀴즈 생성 메뉴 선택
    4.퀴즈내용입력
    5.엔터키로 전송
    6.AI 응답 대기
    """
    # Page Object 생성
    page = Chat_Expance(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send(wait_time=30)
    # 검증
    assert result, "❌ 퀴즈 생성 및 전송 프로세스 실패"
    print("✅ CE-003 테스트 통과!")

def test_ce_003_001(logged_in_driver):
    """
    CE-003_001: 퀴즈생성 테스트 - 예외케이스
    테스트 시나리오
    1.로그인
    2.플러스 버튼 클릭
    3.퀴즈 생성 메뉴 선택
    4.퀴즈내용입력(빈칸)
    5.엔터키로 전송
    6.AI 응답 대기
    """
    # Page Object 생성
    page = Chat_Expance(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_empty(wait_time=10)
    # 검증
    assert result, "✅CE-003_001 : 빈칸 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-003_001 테스트 통과! (빈칸 퀴즈 생성 반응확인)")

def test_ce_003_002(logged_in_driver):
    """
    CE-003_002: 퀴즈생성 테스트 - 예외케이스
    테스트 시나리오
    1.로그인
    2.플러스 버튼 클릭
    3.퀴즈 생성 메뉴 선택
    4.퀴즈내용입력(특수문자)
    5.엔터키로 전송
    6.AI 응답 대기
    """
    # Page Object 생성
    page = Chat_Expance(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_special_chars(wait_time=10)
    # 검증
    assert result, "✅CE-003_002 : 특수문자 퀴즈 생성이 허용되었습니다!"
    print("✅ CE-003_002 테스트 통과! (특수문자 퀴즈 생성 확인)")

def test_ce_003_003(logged_in_driver):
    """
    CE_003_003: 퀴즈생성 테스트 - 예외케이스
    테스트 시나리오
    1.로그인
    2.플러스 버튼 클릭
    3.퀴즈 생성 메뉴 선택
    4.퀴즈내용입력(난이도 혹은 주관식, 객관식을 명시하지 않음)
    5.엔터키로 전송
    6.AI 응답 대기
    """
    # Page Object 생성
    page = Chat_Expance(logged_in_driver)
    
    # 퀴즈 생성 및 전송 (전체 프로세스)
    result = page.create_quiz_and_send_no_type(wait_time=10)
    # 검증
    assert result, "✅CE-003_003 : 난이도 혹은 주관식, 객관식을 명시하지 않은 퀴즈 생성이 허용되었습니다!"
    print("✅ CE_003_003 테스트 통과! (난이도 혹은 주관식, 객관식을 명시하지 않은 퀴즈 생성 확인)")

# def test_ce_004(logged_in_driver):
#     """
#     CE-004: PPT 생성 테스트
#     테스트 시나리오
#     1.로그인
#     2.플러스 버튼 클릭
#     3.PPT 생성 메뉴 선택
#     4.PPT내용입력
#     5.엔터키로 전송
#     """
#     # Page Object 생성
#     page = Chat_Expance(logged_in_driver)

#     # PPT 생성 및 전송 (전체 프로세스)
#     result = page.create_ppt_and_send(wait_time=30)
#     # 검증
#     assert result, "❌ PPT 생성 및 전송 프로세스 실패"
#     print("✅ CE-004 테스트 통과!")
    