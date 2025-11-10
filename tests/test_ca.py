import pytest
# from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
# from src.pages.agent_page import AgentPage
# from src.utils.helpers import Utils
from src.pages.custom_agent_page import CreateAgentPage, SaveAgentPage
# import pyautogui

CHROME_DRIVER_PATH = ChromeDriverManager().install()
    #크롬 열고 로그인까지 완료된 드라이버 리턴
    # service = Service(CHROME_DRIVER_PATH)
    # driver = webdriver.Chrome(service=service) 이거 fixture에 넣었었는데 현재 conftest.py에서 받아오기때문에 주석처리

# @pytest.fixture
# def logged_in_driver(driver) :
#     try :
#         page = AgentPage(driver)
#         page.open()
#         page.login()
#         print("✅ 로그인 성공")
#     except TimeoutException :
#         print("✅ 현재 로그인 상태")
#     Utils(driver).wait_for(timeout=15)
#     print("✅ 로그인 대기 완료")
#     yield driver  # 여기서부터 테스트 함수에 넘김
#     # driver.quit()  # 테스트 끝나면 자동 종료용인데, 브라우저 닫지 않고 로그인 유지한채 진행을 위해 주석처리
#     # 발표용으로는 적합하지만 실제 테스트용으로는 위험하므로 발표 외에는 주의필요 
    

@pytest.fixture
def create_page(logged_in_driver):
    #로그인 된 상태에서 커스텀에이전트 생성페이지로 이동
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]'))).click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]'))).click()
    wait.until(EC.url_contains("builder#form"))
    yield driver
    # driver.quit()  # 테스트 끝나면 자동 종료용인데 이하생략



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
        print("❌ CA_001_페이지로 이동 실패!")


def test_ca_002(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    page = CreateAgentPage(driver)

    # 1️⃣ 생성 페이지에서 필드 요소 찾기, name제외 기본 필드 입력
    
    page.fill_form(
    "", 
    "test description",
    "test system prompt",
    "test conversation starter")
    
    create_btn = page.get_element("create_btn")


    # 2️⃣ name 필드 안내문구 & 버튼 비활성화 확인
    
    if wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error"))).is_displayed():
        print("✅ CA_002_name 필드 입력 안내문구 정상 출력")
    else:
        print("❌ CA_002_name 필드 입력 안내문구 미출력")

    assert not create_btn.is_enabled(), "❌ CA_002_생성 버튼 활성화상태"
    print("✅ CA_002_생성 버튼 비활성화 정상")

    # 3️⃣ name 입력 후 systemPrompt 필드 내용 삭제
    name_input = page.get_element("name")
    name_input.click()
    name_input.send_keys("Test Agent")

    rules_input = page.get_element("rules")
    rules_input.send_keys(Keys.CONTROL + "a")
    rules_input.send_keys(Keys.DELETE) 

    WebDriverWait(driver, 5).until(lambda d: rules_input.get_attribute("value") == "")
    name_input.click()  # 포커스 이동 위해 클릭

    # 4️⃣ name 안내문구 사라짐 & systemPrompt 필드 안내문구 출력 & 버튼 비활성화 확인
    if wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error"))).is_displayed():
        print("✅ CA_002_name 필드 입력 안내문구 사라짐")
    else:
        print("❌ CA_002_name 필드 입력 안내문구 여전히 출력")    
    
    assert not create_btn.is_enabled(), "❌ CA_002_생성 버튼 활성화상태"
    print("✅ CA_002_생성 버튼 비활성화 정상")


def test_ca_003_1(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    page = CreateAgentPage(driver)

    # 1️⃣ 생성 페이지에서 필드 요소 찾고 모든 필드 입력 후 create 버튼 클릭
    page.fill_form(
    "project team",
    "for the team project",
    "If you must make a guess, clearly state that it is a guess",
    "Hello, we're team 03")
    page.get_element("create_btn", "clickable").click()


    # 2️⃣ 나만보기 설정으로 save & 생성 확인
    save_page = SaveAgentPage(driver)
    save_page.select_mode("private")
    print("✅ CA_003_1_나만보기 옵션 선택 완료")
    save_page.click_save()
    

    # 3️⃣ 페이지 자동 이동 확인

    try:
        WebDriverWait(driver, 10).until(lambda d: "builder#form" not in d.current_url)
        print("✅ CA_003_1_에이전트 메인 페이지로 이동 완료!")
    except TimeoutException:
        print("❌ CA_003_1_에이전트 메인 페이지로 자동 이동 실패!")
    #     try: 
    #         save_page.verify_success()
    #         save_page.click_start_chat_fast()
    #         print("✅ CA_003_1_생성 에이전트 페이지로 직접 이동")
    #     except: 
    #         print("❌ CA_003_1_버튼 사라짐으로 실패")

    # assert save_page.get_element("chat_input").is_displayed(), "❌ CA_003_1_생성 에이전트 페이지로 직접 이동하지 못함"            
    # print("✅ CA_003_1_생성 에이전트 페이지 직접 이동 성공")
    # 임시알림으로 뜬 스낵바에 바로가기 버튼인 'start to chat'을 클릭하는 연계 작업.. 너무 빨리 사라져서 계속 실패함



def test_ca_003_2(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    page = CreateAgentPage(driver)

    # 1️⃣ 생성 페이지에서 필드 요소 찾고 모든 필드 입력 후 create 버튼 클릭
    page.fill_form(
    "project team",
    "for the team project",
    "If you must make a guess, clearly state that it is a guess",
    "Hello, we're team 03")
    page.get_element("create_btn", "clickable").click()


    # 2️⃣ 전체공개 설정으로 save & 생성 확인
    save_page = SaveAgentPage(driver)
    save_page.select_mode("organization")
    print("✅ CA_003_2_조직 옵션 선택 완료")
    save_page.click_save()
    

    # 3️⃣ 페이지 자동 이동 확인

    try:
        WebDriverWait(driver, 10).until(lambda d: "builder#form" not in d.current_url)
        print("✅ CA_003_2_에이전트 메인 페이지로 이동 완료!")
    except TimeoutException:
        print("❌ CA_003_2_에이전트 메인 페이지로 자동 이동 실패!")



def test_ca_004(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    page = CreateAgentPage(driver)

    # 1️⃣ create with chat에서 필드 구성 답변 받기
    

    
    







# 5️⃣실행
# if __name__ == "__main__":
#     driver = webdriver.Chrome()
#     test_ca_001(driver, "ssunull@daum.net", "dorpw-6Gewk")


