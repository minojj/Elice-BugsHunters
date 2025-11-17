from time import sleep
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.pages.chat_base_page import ChatPage

TEST_FILES_DIR = Path(__file__).parent.parent / "resources" / "testdata"
TEST_FILENAME = TEST_FILES_DIR / "git.pdf"
TEST_DOG_IMAGE = TEST_FILES_DIR / "dog.png"


def test_cb_001_ai_chat(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    # 현재 기사 수 기준선 저장 후 전송
    count_before = len(chat_page.driver.find_elements(By.XPATH, "//div[@role='article']"))
    chat_page.send_message("안녕하세요")
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@role='article']")) > count_before
    )
    print("테스트 완료")


def test_cb_002_copy(driver):
    chat_page = ChatPage(driver)
    ai_response = chat_page.get_ai_response("안녕하세요")
    assert ai_response, "AI 응답을 찾을 수 없습니다"
    
    # 복사 버튼이 클릭 가능할 때까지 대기
    WebDriverWait(chat_page.driver, 10).until(
        EC.presence_of_element_located(chat_page.locators["copy_btn"])
    )
    result = chat_page.copy_message(ai_response)
    assert result, "복사 버튼 클릭 실패"


def test_cb_003_edit_message(driver):
    chat_page = ChatPage(driver)
    count_before = len(chat_page.driver.find_elements(By.XPATH, "//div[@role='article']"))
    chat_page.edit_message("안녕하세요", "애국가 4절까지 가사 알려줘")
    # AI 응답으로 기사 수 증가 대기
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@role='article']")) > count_before
    )


def test_cb_004_scroll_and_click(driver):
    chat_page = ChatPage(driver)
    
    sleep(3)
    chat_page.scroll_to_top()
    sleep(2)  # 스크롤 후 충분한 대기
    chat_page.click_scroll_to_latest_button()
    sleep(3)  # 버튼 클릭 후 충분한 대기


def test_cb_005_make_image(driver):
    chat_page = ChatPage(driver)
    chat_page.send_message("태극기를 그려줘")
    assert chat_page.check_image_exists(), "태극기 이미지를 찾을 수 없습니다"


def test_cb_006_upload_file(logged_in_driver):
    chat_page = ChatPage(logged_in_driver)
    chat_page.upload_file(str(TEST_FILENAME.absolute()))
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: d.find_element(*chat_page.locators["file_input"]).get_attribute("value")
    )
    count_before = len(chat_page.driver.find_elements(By.XPATH, "//div[@role='article']"))
    chat_page.send_message("이 파일 3줄로 요약해줘")
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@role='article']")) > count_before
    )


def test_cb_007_make_image(driver):
    chat_page = ChatPage(driver)
    chat_page.upload_file(str(TEST_DOG_IMAGE.absolute()))
    WebDriverWait(chat_page.driver, 30).until(
        lambda d: d.find_element(*chat_page.locators["file_input"]).get_attribute("value")
    )
    count_before = len(chat_page.driver.find_elements(By.XPATH, "//div[@role='article']"))
    chat_page.send_message("이 사진을 애니매이션화해서 그려줘")
    WebDriverWait(chat_page.driver, 60).until(
        lambda d: len(d.find_elements(By.XPATH, "//div[@role='article']")) > count_before
    )
    assert chat_page.check_image_exists(), "애니메이션 이미지를 찾을 수 없습니다"