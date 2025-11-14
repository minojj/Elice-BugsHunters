from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.pages.chat_base_page import ChatPage


def test_cb_001(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    
    print(f" 메시지 전송: '안녕하세요'")
    # 현재 기사 수 기준선 저장 후 전송
    count_before = len(chat_page.driver.find_elements(By.XPATH, "//div[@role='article']"))
    chat_page.send_message("안녕하세요")

    # AI 응답으로 기사 수 증가 대기 (명시적 대기)
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@role='article']")) > count_before
    )
    print("테스트 완료")


def test_cb_005(driver):
    chat_page = ChatPage(driver)
    ai_response = chat_page.get_ai_response("안녕하세요")
    assert ai_response, "AI 응답을 찾을 수 없습니다"
    
    sleep(1)  # 복사 전 안정화 대기
    result = chat_page.copy_message(ai_response)
    assert result, "복사 버튼 클릭 실패"
    
    sleep(2)  # 복사 완료 대기


def test_cb_007(driver):
    chat_page = ChatPage(driver)
    chat_page.edit_message("안녕하세요", "애국가 4절까지 가사 알려줘")
    sleep(5)  # AI 응답 대기


def test_cb_008(driver):
    chat_page = ChatPage(driver)
    
    sleep(3)
    chat_page.scroll_to_top()
    sleep(2)  # 스크롤 후 충분한 대기
    chat_page.click_scroll_to_latest_button()
    sleep(3)  # 버튼 클릭 후 충분한 대기


def test_cb_004(driver):
    chat_page = ChatPage(driver)
    chat_page.send_message("태극기를 그려줘")
    # 이미지 생성 대기 (check_image_exists 내부에 wait 포함)
    assert chat_page.check_image_exists(), "태극기 이미지를 찾을 수 없습니다"


def test_cb_002(driver):
    chat_page = ChatPage(driver)
    chat_page.upload_file(r"C:\Users\97min\OneDrive\바탕 화면\[수업 자료] Jenkins 개념 및 환경 설정.pdf")
    # 파일 업로드 완료 대기 (file input 값 설정 여부)
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: d.find_element(*chat_page.locators["file_input"]).get_attribute("value")
    )
    # 현재 기사 수 기준선 저장 후 메시지 전송
    count_before = len(chat_page.driver.find_elements(By.XPATH, "//div[@role='article']"))
    chat_page.send_message("이 파일 3줄로 요약해줘")
    # AI 응답 대기 (기사 수 증가)
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@role='article']")) > count_before
    )


def test_cb_003(driver):
    chat_page = ChatPage(driver)
    chat_page.upload_file(r"C:\Users\97min\OneDrive\바탕 화면\dog.png")
    # 파일 업로드 완료 대기 (file input 값 설정 여부)
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: d.find_element(*chat_page.locators["file_input"]).get_attribute("value")
    )
    # 현재 기사 수 기준선 저장 후 메시지 전송
    count_before = len(chat_page.driver.find_elements(By.XPATH, "//div[@role='article']"))
    chat_page.send_message("이 사진을 애니매이션화해서 그려줘")
    # AI 응답 대기 (기사 수 증가)
    WebDriverWait(chat_page.driver, 60).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@role='article']")) > count_before
    )
