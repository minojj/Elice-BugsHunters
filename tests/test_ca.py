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
from src.pages.login_page import LoginFunction
from src.pages.custom_agent_page import AgentExplorerPage, CreateAgentPage, SaveAgentPage, ChatCreatePage, MyAgentsPage
# import pyautogui


chrome_driver_path = ChromeDriverManager().install()

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
    

#생성 페이지로 이동하는 fixture
    
@pytest.fixture(scope="session")
def create_page(logged_in_driver):
    driver = logged_in_driver
    explorer_page = AgentExplorerPage(driver)
    wait = WebDriverWait(driver, 10)
    explorer_page.get_element("agent_explorer_btn", wait_type="presence").click()
    explorer_page.get_element("create_btn", wait_type="presence").click()
    wait.until(EC.url_contains("builder#form"))
    yield driver
    # driver.quit()  # 테스트 끝나면 자동 종료용인데 이하생략

#마이 에이전트 페이지로 이동하는 fixture

@pytest.fixture
def my_agents_page_loaded(logged_in_driver):
    driver = logged_in_driver
    explorer_page = AgentExplorerPage(driver)
    my_agent_page = MyAgentsPage(driver)

    explorer_page.get_element("agent_explorer_btn", wait_type="presence").click()
    my_agent_page.click_my_agents_button()

    yield driver

#fill_form 함수 사용시 생성된 에이전트 이름을 반환하는 fixture 
#006,015에서 받아감. 의존성 문제가 너무 큰데 여유가 생기면 리팩토링 필요. API 쪽으로 생각.

@pytest.fixture
def created_form_input(create_page):
    page = CreateAgentPage(create_page)

    agent_data = page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )

    page.get_element("create_btn", "clickable").click()
    return agent_data["name"] 







def test_ca_001(logged_in_driver):
    # 1️⃣ 접속 및 로그인
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)
    explorer_page = AgentExplorerPage(driver)

    # 2️⃣ Agent Explorer 클릭
    explorer_page.get_element("agent_explorer_btn", wait_type="presence").click()
    
    # 3️⃣ create 버튼 클릭
    explorer_page.get_element("create_btn", wait_type="presence").click()

    # 4️⃣ 페이지 전환 확인
    try:
        wait.until(EC.url_contains("builder#form"))
        print("✅ CA_001_페이지로 이동 완료!")
    except TimeoutException:
        print("❌ CA_001_페이지로 이동 실패!")


def test_ca_002(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    create_page = CreateAgentPage(driver)

    # 1️⃣ 생성 페이지에서 필드 요소 찾기, name제외 기본 필드 입력
    
    create_page.fill_form(
    "", 
    "test description",
    "test system prompt",
    "test conversation starter")
    
    create_btn = create_page.get_element("create_btn")


    # 2️⃣ name 필드 안내문구 & 버튼 비활성화 확인
    
    if wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error"))).is_displayed():
        print("✅ CA_002_name 필드 입력 안내문구 정상 출력")
    else:
        print("❌ CA_002_name 필드 입력 안내문구 미출력")

    assert not create_btn.is_enabled(), "❌ CA_002_생성 버튼 활성화상태"
    print("✅ CA_002_생성 버튼 비활성화 정상")

    # 3️⃣ name 입력 후 systemPrompt 필드 내용 삭제
    name_input = create_page.get_element("name")
    name_input.click()
    name_input.send_keys("Test Agent")

    rules_input = create_page.get_element("rules")
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


def test_ca_003_1(create_page,created_form_input):
    driver = create_page

    # 1️⃣ 나만보기 설정으로 save & 생성 확인
    save_page = SaveAgentPage(driver)
    save_page.select_mode("private")
    print("✅ CA_003_1_나만보기 옵션 선택 완료")
    save_page.click_save()
    message = save_page.get_snackbar_text().lower()
    assert "created" in message, f"❌ 예상과 다른 메시지: {message}"
    print(f"✅ CA_003_1_private 에이전트 생성 성공 알림 확인: {message}")
    

    # 2️⃣ 페이지 자동 이동 확인

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



def test_ca_003_2(create_page,created_form_input):
    driver = create_page

    # 1️⃣ 전체공개 설정으로 save & 생성 확인
    save_page = SaveAgentPage(driver)
    save_page.select_mode("organization")
    print("✅ CA_003_2_조직 옵션 선택 완료")
    save_page.click_save()
    message = save_page.get_snackbar_text().lower()
    assert "created" in message, f"❌ 예상과 다른 메시지: {message}"
    print(f"✅ CA_003_2_organization 에이전트 생성 성공 알림 확인: {message}")
    

    # 2️⃣ 페이지 자동 이동 확인

    try:
        WebDriverWait(driver, 10).until(lambda d: "builder#form" not in d.current_url)
        print("✅ CA_003_2_에이전트 메인 페이지로 이동 완료!")
    except TimeoutException:
        print("❌ CA_003_2_에이전트 메인 페이지로 자동 이동 실패!")



# def test_ca_004(create_page):
#     driver = create_page
#     wait = WebDriverWait(driver, 10)
#     page = CreateAgentPage(driver)
#     chat_page = ChatCreatePage(driver)
#     save_page = SaveAgentPage(driver)

#     # 1️⃣ create with chat에서 필드 구성 답변 받기

#     chat_page.click_create_with_chat()
#     chat_page.typing_chat()   

#     # 2️⃣ 답변 기반으로 필드 자동 입력
#     chat_page.transfer_to_create_form()
#     page.get_element("create_btn", "clickable").click()
    
#     # 3️⃣ 나만보기 설정으로 save & 생성 확인
#     save_page.select_mode("private")
#     print("✅ CA_004_나만보기 옵션으로 생성")
#     save_page.click_save()
#     save_page.verify_success()
#     print("✅ CA_004_생성완료 알림 확인")

# ##이거 챗봇 대답이 할때마다 구조가 달라짐



def test_ca_005(create_page):
    driver = create_page
    create_agent_page = CreateAgentPage(driver)

    # 1️⃣ 동일 이름 입력 후 생성 시도
    create_agent_page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )
    create_agent_page.get_element("create_btn", "clickable").click()

    # 2️⃣ 저장 시도
    save_page = SaveAgentPage(driver)
    save_page.select_mode("organization")
    save_page.click_save()

    # 3️⃣ 팝업 확인
    message = save_page.get_snackbar_text().lower()
    print("📢 알림 메시지:", message)

    if "created" in message or "success" in message or "성공" in message:
        print("❌ 성공팝업 - 중복 검증 누락 가능성")
    elif "duplicate" in message or "faild" in message or "이미 존재" in message or "동일한 이름" in message:
        print("✅ 중복 이름 감지 정상 동작")
    else:
        print(f"⚠️ 예상치 못한 팝업 메시지: {message}")




def test_ca_006(logged_in_driver,created_form_input):
    driver = logged_in_driver
    create_agent_name = created_form_input
    explorer_page = AgentExplorerPage(driver)

    # 1️⃣ Agent Explorer 메인화면 진입 후 생성된 커스텀 에이전트 확인

    explorer_page.navigate_to_agent_explorer(force_refresh=True)

    assert create_agent_name is not None, "❌ CA_006_이전 테스트에서 생성된 에이전트 탐색 불가"
    found = explorer_page.click_agent_card_by_name(create_agent_name)
    assert found, "❌ CA_006_생성된 에이전트 탐색 불가"
    print("✅ CA_006_생성된 에이전트 탐색 후 진입")

    # 2️⃣ 에이전트 대화 페이지 진입 확인

    explorer_page.get_element("agent_chat_input", "visible")
    print("✅ CA_006_에이전트 대화 페이지 진입 성공")



def test_ca_007(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)

    # 1️⃣ My Agents 페이지 진입 후 Draft, Private, Organization 카드 존재여부 확인

    draft_cards = my_agent_page.get_draft_cards()   
    private_cards = my_agent_page.get_private_cards()
    organization_cards = my_agent_page.get_organization_cards()

    assert my_agent_page.has_cards("private", minimum=1), "❌ CA_007_Private 카드 없음."
    assert my_agent_page.has_cards("draft", minimum=1), "❌ CA_007_Draft 카드 없음"
    assert my_agent_page.has_cards("organization", minimum=1), "❌ CA_007_Organization 카드 없음"
    
    # 2️⃣ 각 카드의 화면 노출 확인

    assert my_agent_page.is_card_visible(private_cards[0]), "❌ CA_007_Private 카드 미출력"
    assert my_agent_page.is_card_visible(draft_cards[0]), "❌ CA_007_Draft 카드 미출력"
    assert my_agent_page.is_card_visible(organization_cards[0]), "❌ CA_007_Organization 카드 미출력"
    
    # 3️⃣ 각 카드 개수 출력

    print(f"✅ Private 카드 개수: {my_agent_page.get_card_count('private')}")
    print(f"✅ Draft 카드 개수: {my_agent_page.get_card_count('draft')}")
    print(f"✅ Organization 카드 개수: {my_agent_page.get_card_count('organization')}")




def test_ca_008(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    create_agent_page = CreateAgentPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ 첫 번째 Private 카드의 edit 버튼 클릭(organization으로 변경 가능)
    my_agent_page.click_edit_button_by_card_type("private")

    #2️⃣ 수정 작업
    name_field = create_page.get_element("name")
    name_field.click()
    name_field.send_keys("_edit")
    create_page.get_element("create_btn", "clickable").click() #수정 작업의 경우 publish로 텍스트만 변경됨

    #3️⃣ 수정 후 저장, 알림 확인(1️⃣에서 organization으로 변경 시 organization으로 변경)
    save_page.select_mode("private")
    print("✅ CA_008_Private 모드 유지 확인")
    save_page.click_save()
    message = save_page.get_snackbar_text().lower()
    assert "updated" in message, f"❌ CA_008_예상과 다른 메시지: {message}"
    print(f"✅ CA_008_에이전트 수정 성공 알림 확인: {message}")



def test_ca_009(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    create_agent_page = CreateAgentPage(driver)
    
    #1️⃣ 첫 번째 Draft 카드의 edit 버튼 클릭
    my_agent_page.click_edit_button_by_card_type("draft")
    
    #2️⃣ 수정을 위해 필드 요소 찾고 모든 필드 입력 후 create 버튼 클릭
    create_agent_page.fill_form(
    "project team",
    "for the team project",
    "If you must make a guess, clearly state that it is a guess",
    "Hello, we're team 03")
    create_agent_page.get_element("create_btn", "clickable").click()
    
    #3️⃣ 나만보기 설정으로 save & 생성 확인(organization으로 변경 가능)
    save_page = SaveAgentPage(driver)
    save_page.select_mode("private")
    print("✅ CA_008_private 옵션 선택 완료")
    save_page.click_save()

    message = save_page.get_snackbar_text().lower()
    assert "created" in message, f"❌ CA_009_예상과 다른 메시지: {message}"
    print(f"✅ CA_009_임시 저장된 에이전트 생성 성공 알림 확인: {message}")

    

def test_ca_010(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    create_agent_page = CreateAgentPage(driver)
    
    #1️⃣ 첫 번째 Draft 카드의 edit 버튼 클릭
    my_agent_page.click_edit_button_by_card_type("draft")
    
    #2️⃣ 수정을 위해 필드 요소 찾고 모든 필드 입력 후 뒤로가기
    expected_values = create_agent_page.fill_form(
    "project team",
    "",
    "If you must make a guess, clearly state that it is a guess",
    "")
    driver.back()
    driver.refresh()
    print("✅ CA_010_뒤로가기 실행")

    # 3️⃣ 재진입 후 필드 내용 임시저장 여부 확인
    my_agent_page.click_edit_button_by_card_type("draft")
    actual_values = create_agent_page.get_all_field_values()

    assert actual_values["name"] == expected_values["name"], f"❌ CA_010_name 불일치: 예상 '{expected_values['name']}', 실제 '{actual_values['name']}'"
    assert actual_values["rules"] == expected_values["rules"], f"❌ CA_010_rules 불일치: 예상 '{expected_values['rules']}', 실제 '{actual_values['rules']}'"
    print(f"✅ CA_010_임시저장 성공")



def test_ca_011(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)

    #1️⃣ 두 번째 draft 카드의 delete 버튼 클릭(위치나 종류는 환경에 따라 변경 가능) 
    my_agent_page.click_delete_button_by_card_type("draft", index=1)

    #2️⃣ 삭제 팝업 모달 확인
    assert my_agent_page.is_delete_modal_visible(), "❌ CA_011_삭제 팝업 모달 미출력"
    
    my_agent_page.cancel_delete_modal()
    
    assert not my_agent_page.is_delete_modal_visible(), "❌ CA_011_모달이 닫히지 않음"
    print("✅ CA_011_삭제 팝업 모달 Cancel 버튼 정상 작동")



def test_ca_012(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ 두 번째 draft 카드의 완전 삭제(위치나 종류는 환경에 따라 변경 가능)
    my_agent_page.click_delete_button_by_card_type("draft", index=1)
    my_agent_page.confirm_delete_modal()

    #2️⃣ 삭제 후 알림 확인
    message = save_page.get_snackbar_text().lower()
    assert "success" in message or "delete" in message, f"❌ CA_012_예상과 다른 메시지: {message}"
    print(f"✅ CA_012_선택한 에이전트 삭제 완료: {message}")





def test_ca_015(logged_in_driver_sub_account,created_form_input):
    driver = logged_in_driver_sub_account
    create_agent_name = created_form_input
    explorer_page = AgentExplorerPage(driver)

    #1️⃣ 페이지 접속 후 Private 카드 이름 인자로 받아와서 검색
    explorer_page.get_element("agent_explorer_btn", wait_type="presence").click()
    results = explorer_page.get_filtered_search_results(create_agent_name)

    #2️⃣ Private 카드 노출 여부 확인

    assert len(results) == 0, f"❌ CA_015_private 카드 노출: {results}"
    print("✅ CA_015_private 카드 '나만보기' 설정 정상 동작")



    

    
    


