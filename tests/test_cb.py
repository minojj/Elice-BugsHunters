from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.pages.chat_base_page import ChatPage


def test_cb_001(driver):
    chat_page = ChatPage(driver)
    
    print(f" 메시지 전송: '안녕하세요'")
    chat_page.send_message("안녕하세요")

    # AI 응답 대기
    sleep(5)
    print("테스트 완료")


def test_cb_005(driver):
    chat_page = ChatPage(driver)
    ai_response = chat_page.get_ai_response("안녕")
    assert ai_response, "AI 응답을 찾을 수 없습니다"
    sleep(1)  # 클립보드 준비를 위한 최소 대기
    chat_page.copy_message(ai_response)
    sleep(1)  # 클립보드 복사 완료를 위한 최소 대기
    assert chat_page.verify_copied_equals_paste(ai_response), "복사/붙여넣기 내용이 원문과 일치하지 않습니다"


def test_cb_007(driver):
    chat_page = ChatPage(driver)
    chat_page.edit_message("안녕하세요", "애국가 4절까지 가사 알려줘")
    # 수정된 메시지에 대한 AI 응답 대기
    sleep(15)


def test_cb_008(driver):
    chat_page = ChatPage(driver)
    
    sleep(3)
    chat_page.scroll_to_top()
    sleep(1)
    chat_page.click_scroll_to_latest_button()
    sleep(2)


def test_cb_004(driver):
    chat_page = ChatPage(driver)
    chat_page.send_message("태극기를 그려줘")
    # 이미지 생성 대기 (check_image_exists 내부에 wait 포함)
    assert chat_page.check_image_exists(), "태극기 이미지를 찾을 수 없습니다"


def test_cb_002(driver):
    chat_page = ChatPage(driver)
    chat_page.upload_file(r"C:\Users\97min\OneDrive\바탕 화면\[수업 자료] Jenkins 개념 및 환경 설정.pdf")
    # 파일 업로드 완료 대기
    sleep(2)
    chat_page.send_message("이 파일 3줄로 요약해줘")
    # AI 응답 대기
    sleep(10)


# def test_cb_003(driver):
#     chat_page = ChatPage(driver)
#     chat_page.upload_file(r"C:\Users\97min\OneDrive\바탕 화면\dog.png")
#     sleep(2)
#     chat_page.send_message("이 사진을 애니매이션화해서 그려줘")
#     sleep(30)
#     input("\n테스트 완료. 종료하려면 Enter를 누르세요...")