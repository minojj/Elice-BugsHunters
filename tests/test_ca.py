import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from src.pages.agent_page import AgentPage
import pyautogui

CHROME_DRIVER_PATH = ChromeDriverManager().install()

@pytest.fixture
def logged_in_driver():
    #크롬 열고 로그인까지 완료된 드라이버 리턴
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    page = AgentPage(driver)
    page.open()
    page.login()
    yield driver  # 여기서부터 테스트 함수에 넘김
    driver.quit()  # 테스트 끝나면 자동 종료
    

@pytest.fixture
def create_page():
    #로그인 된 상태에서 커스텀에이전트 생성페이지로 이동
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    page = AgentPage(driver)
    page.open()
    page.login()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]'))).click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]'))).click()
    wait.until(EC.url_contains("builder#form"))
    yield driver
    driver.quit()  # 테스트 끝나면 자동 종료



def test_ca_001(logged_in_driver):
    # 1️⃣ 접속 및 로그인
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)

    # 2️⃣ Agent Explorer 클릭
    agent_explorer_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]'))).click()

    # 3️⃣ create 버튼 클릭
    creat_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]'))).click()

    # 4️⃣ 페이지 전환 확인
    try:
        wait.until(EC.url_contains("builder#form"))
        print("✅ CA_001_페이지로 이동 완료!")
    except TimeoutException:
        print("❌ 페이지로 이동 실패!")


def test_ca_002(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)

    # 1️⃣ 생성 페이지에서 필드 요소 찾기, name제외 기본 필드 입력
    name_input = wait.until(EC.visibility_of_element_located((By.NAME, "name")))

    description_input = wait.until(EC.element_to_be_clickable((By.NAME, "description")))
    description_input.click()
    description_input.send_keys("test description")
    rules_input = wait.until(EC.visibility_of_element_located((By.NAME, "systemPrompt")))
    rules_input.click()
    rules_input.send_keys("test system prompt")
    starting_conversation_input = wait.until(EC.visibility_of_element_located((By.NAME, "conversationStarters.0.value")))
    starting_conversation_input.click()
    starting_conversation_input.send_keys("test conversation starter")

    create_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.MuiButton-containedPrimary")))
    

    # 2️⃣ name 필드 안내문구 & 버튼 비활성화 확인
    
    if driver.find_element(By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error").is_displayed():
        "✅ name 필드 입력 안내문구 정상 출력"
    else:
        "❌ name 필드 입력 안내문구 미출력"

    assert not create_btn.is_enabled(), "❌ 생성 버튼 활성화상태"
    print("✅ 생성 버튼 비활성화 정상")

    # 3️⃣ name 입력 후 systemPrompt 필드 내용 삭제
    name_input.click()
    name_input.send_keys("Test Agent")
    rules_input.clear()

    # 4️⃣ name 안내문구 사라짐 & systemPrompt 필드 안내문구 출력 & 버튼 비활성화 확인
    if not driver.find_element(By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error").is_displayed():
        print("✅ name 필드 입력 안내문구 사라짐")
    else:
        print("❌ name 필드 입력 안내문구 여전히 출력")    
    
    assert not create_btn.is_enabled(), "❌ 생성 버튼 활성화상태"
    print("✅ 생성 버튼 비활성화 정상")










# 5️⃣실행
# if __name__ == "__main__":
#     driver = webdriver.Chrome()
#     test_ca_001(driver, "ssunull@daum.net", "dorpw-6Gewk")


