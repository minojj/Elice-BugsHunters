from time import sleep
from src.pages.ChatBasepage import ChatPage


def test_cb_001(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    
    print(f" 메시지 전송: '안녕하세요'")
    chat_page.send_message("안녕하세요")

    sleep(5)
    print("테스트 완료")


def test_cb_005(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    ai_response = chat_page.get_ai_response("안녕")
    assert ai_response, "AI 응답을 찾을 수 없습니다"
    sleep(2)
    chat_page.copy_message(ai_response)
    sleep(2)
    # 복사한 내용을 입력창에 붙여넣고 원문과 동일한지 검증
    assert chat_page.verify_copied_equals_paste(ai_response), "복사/붙여넣기 내용이 원문과 일치하지 않습니다"


def test_cb_007(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    chat_page.edit_message("안녕하세요", "애국가 4절까지 가사 알려줘")
    sleep(15)


def test_cb_008(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    
    sleep(3)
    chat_page.scroll_to_top()
    sleep(1)
    chat_page.click_scroll_to_latest_button()
    sleep(2)


def test_cb_004(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    chat_page.send_message("태극기를 그려줘")
    sleep(20)
    
    assert chat_page.check_image_exists(), "태극기 이미지를 찾을 수 없습니다"
    sleep(3)


def test_cb_002(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    chat_page.upload_file(r"C:\Users\97min\OneDrive\바탕 화면\[수업 자료] Jenkins 개념 및 환경 설정.pdf")
    sleep(2)
    chat_page.send_message("이 파일 3줄로 요약해줘")
    sleep(10)


def test_cb_003(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    chat_page.upload_file(r"C:\Users\97min\OneDrive\바탕 화면\dog.png")
    sleep(2)
    chat_page.send_message("이 사진을 애니매이션화해서 그려줘")
    sleep(20)
    input("\n테스트 완료. 종료하려면 Enter를 누르세요...")
