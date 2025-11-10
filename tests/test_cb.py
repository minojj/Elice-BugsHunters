import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root) 
# 'pom연습파일' 디렉토리를 경로에 추가하여 'src'를 찾을 수 있게 합니다.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.pages.ChatBasepage import ChatPage 

# 테스트 설정
USERNAME = "team3@elice.com"
PASSWORD = "team3elice!@"

# WebDriver 초기화
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
chat_page = ChatPage(driver)


def test_cb_001():
    print("--- TEST_CB_001: 로그인 및 기본 검색 테스트 시작 ---")

    try:
        if not chat_page.open():
            return False

        if not chat_page.login(USERNAME, PASSWORD):
            return False

        if not chat_page.is_logged_in():
            return False

        search_term = "안녕하세요."
        if not chat_page.send_message(search_term):
            return False

        print("--- TEST_CB_001: 로그인 및 기본 검색 테스트 완료 ---")
        return True
    except Exception as e:
        print(f" TEST_CB_001 실패: 치명적 오류 발생: {e}")
        return False


def test_cb_005():
    print("\n--- TEST_CB_002: 대화 내용 복사 기능 테스트 시작 ---")

    try:
        expected_text = "안녕하세요!"
        ai_response = chat_page.get_ai_response(expected_text)

        if not ai_response:
            return False

        if not chat_page.copy_message(ai_response):
            return False

        print("--- TEST_CB_002: 대화 내용 복사 기능 테스트 완료 (클립보드 확인 필요) ---")
        return True

    except Exception as e:
        print(f" TEST_CB_002 실패: 오류 발생: {e}")
        return False


def test_cb_007():
    print("\n--- TEST_CB_003: 메시지 수정 기능 테스트 시작 ---")

    try:
        original_message = "안녕하세요."
        new_message = "애국가 4절까지 가사 알려줘"
        
        if not chat_page.edit_message(original_message, new_message):
            return False

        if not chat_page.verify_message_updated(new_message):
            return False

        print("--- TEST_CB_003: 메시지 수정 기능 테스트 완료 ---")
        return True

    except Exception as e:
        print(f" TEST_CB_003 실패: 오류 발생: {e}")
        return False


def test_cb_008():
    print("\n--- TEST_CB_008: 스크롤 및 최신 답변 이동 테스트 시작 ---")

    try:
        print(" AI 응답 완료 대기 중...")
        if not chat_page.wait_for_ai_response_complete(timeout=10):
            return False

        if not chat_page.scroll_to_top():
            return False

        import time
        time.sleep(2)

        if not chat_page.click_scroll_to_latest_button():
            return False

        print("--- TEST_CB_008: 스크롤 및 최신 답변 이동 테스트 완료 ---")
        return True

    except Exception as e:
        print(f" TEST_CB_008 실패: 오류 발생: {e}")
        return False


# 메인 실행
if __name__ == "__main__":
    try:
        if test_cb_001():
            test_cb_005()
            test_cb_007()  
            test_cb_008()  

        # 결과 확인을 위해 사용자 입력 대기
        print("\n--- 모든 테스트 스크립트 실행 완료 ---")
        input("Enter 키를 누르면 브라우저가 종료됩니다...")

    finally:
        driver.quit()