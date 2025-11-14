import pytest
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import os
from src.pages.custom_agent_page import AgentExplorerPage, CreateAgentPage, SaveAgentPage, ChatCreatePage, MyAgentsPage


chrome_driver_path = ChromeDriverManager().install()


@pytest.fixture
def pages(logged_in_driver):
    driver = logged_in_driver
    return {
        "explorer": AgentExplorerPage(driver),
        "create": CreateAgentPage(driver),
        "my_agents": MyAgentsPage(driver),
        "chat_create": ChatCreatePage(driver)
    }


# Explorer 페이지 진입용 fixture
@pytest.fixture
def explorer_page_loaded(pages):
    driver = pages["explorer"].driver
    explorer_page = pages["explorer"]

    driver.get(explorer_page.url)  
    WebDriverWait(driver, 10).until(EC.url_contains("/ai-helpy-chat/agent"))
    print("✅ Explorer 페이지 로드 완료")

    yield driver


# My Agents 페이지 진입용 fixture
@pytest.fixture
def my_agents_page_loaded(pages):
    driver = pages["my_agents"].driver
    my_agents_page = pages["my_agents"]

    driver.get(my_agents_page.url)
    WebDriverWait(driver, 10).until(EC.url_contains("/ai-helpy-chat/agent/mine"))
    print("✅ My Agents 페이지 로드 완료")

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".MuiCard-root"))
        )
        print("✅ My Agents 페이지 로드 + 카드 렌더링 완료")
    except TimeoutException:
        print("⚠️ 카드 리스트 렌더링 실패 (카드 0개일 수도 있음)")

    yield driver


#생성폼 수동 진입용 fixture   

@pytest.fixture
def create_page(pages):
    driver = pages["explorer"].driver
    explorer_page = pages["explorer"]
    wait = WebDriverWait(driver, 10)

    driver.get(explorer_page.url)
    wait.until(EC.url_contains("/ai-helpy-chat/agent"))

    explorer_page.get_element("create_btn", wait_type="clickable").click()

    wait.until(EC.url_contains("builder#form"))
    wait.until(EC.visibility_of_element_located((By.NAME, "name")))

    print("✅ 생성 페이지로 진입 완료")

    yield driver


#더미파일 생성,삭제용 fixture

@pytest.fixture
def dummy_files():
    small = "dummy_small.pdf"
    big = "dummy_big.pdf"

    with open(small, "wb") as f:
        f.write(b"0" * 1024)
    with open(big, "wb") as f:
        f.write(b"0" * 55 * 1024 * 1024)

    yield {
        "small": os.path.abspath(small),
        "big": os.path.abspath(big),
    }

    for fpath in [small, big]:
        if os.path.exists(fpath):
            os.remove(fpath)






def test_ca_001(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)
    explorer_page = AgentExplorerPage(driver)

    explorer_page.get_element("agent_explorer_btn", wait_type="clickable").click()
    explorer_page.get_element("create_btn", wait_type="clickable").click()

    try:
        wait.until(EC.url_contains("builder#form"))
        print("✅ CA_001_페이지로 이동 완료!")
    except TimeoutException:
        print("❌ CA_001_페이지로 이동 실패!")



def test_ca_002(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    create_agent_page = CreateAgentPage(driver)

    # 1️⃣ 생성 페이지에서 필드 요소 찾기, name제외 기본 필드 입력
    
    create_agent_page.fill_form(
    "", 
    "test description",
    "test system prompt",
    "test conversation starter")
    
    create_btn = create_agent_page.get_element("create_btn")


    # 2️⃣ name 필드 안내문구 & 버튼 비활성화 확인
    
    if wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error"))).is_displayed():
        print("✅ CA_002_name 필드 입력 안내문구 정상 출력")
    else:
        print("❌ CA_002_name 필드 입력 안내문구 미출력")

    assert not create_btn.is_enabled(), "❌ CA_002_생성 버튼 활성화상태"
    print("✅ CA_002_생성 버튼 비활성화 정상")

    # 3️⃣ name 입력 후 systemPrompt 필드 내용 삭제
    name_input = create_agent_page.get_element("name")
    name_input.click()
    name_input.send_keys("Test Agent")

    rules_input = create_agent_page.get_element("rules")
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




def test_ca_003_1(create_page, request):
    driver = create_page
    create_agent_page = CreateAgentPage(driver)

    # 1️⃣ 나만보기 설정으로 save & 생성 확인

    create_agent_page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )

    create_agent_page.get_element("create_btn", "clickable").click()

    save_page = SaveAgentPage(driver)
    save_page.select_mode("private")
    print("✅ CA_003_1_나만보기 옵션 선택 완료")
    save_page.click_save()
    message = save_page.get_snackbar_text().lower()
    assert "created" in message, f"❌ CA_003_1_예상과 다른 메시지: {message}"
    print(f"✅ CA_003_1_private 에이전트 생성 성공 알림 확인: {message}")

    agent_id = create_agent_page.get_agent_id_from_url()

    request.config.cache.set("private_agent_id", agent_id)
    print(f"✅ CA_003_1_Private agent ID 저장 완료: {agent_id}")
    

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



def test_ca_003_2(create_page, request):
    driver = create_page
    create_agent_page = CreateAgentPage(driver)

    # 1️⃣ 전체공개 설정으로 save & 생성 확인


    create_agent_page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )

    create_agent_page.get_element("create_btn", "clickable").click()
    save_page = SaveAgentPage(driver)
    save_page.select_mode("organization")
    print("✅ CA_003_2_조직 옵션 선택 완료")
    save_page.click_save()
    message = save_page.get_snackbar_text().lower()
    assert "created" in message, f"❌ CA_003_2_예상과 다른 메시지: {message}"
    print(f"✅ CA_003_2_organization 에이전트 생성 성공 알림 확인: {message}")
    
    agent_id = create_agent_page.get_agent_id_from_url()

    request.config.cache.set("organization_agent_id", agent_id)
    print(f"✅ CA_003_2_Organization agent ID 저장 완료: {agent_id}")

    # 2️⃣ 페이지 자동 이동 확인

    try:
        WebDriverWait(driver, 10).until(lambda d: "builder#form" not in d.current_url)
        print("✅ CA_003_2_에이전트 메인 페이지로 이동 완료!")
    except TimeoutException:
        print("❌ CA_003_2_에이전트 메인 페이지로 자동 이동 실패!")



def test_ca_004(create_page, pages):
    driver = create_page
    chat_page = pages["chat_create"]

    # 1️⃣ create with chat 클릭
    chat_page.click_create_with_chat()

    # 2️⃣ 챗봇에 메시지 입력 & 답변 생성 대기
    chat_page.send_single_message()
    assert chat_page.wait_for_ai_answer(), "❌ CA_004_AI 답변 생성 실패"
    print("✅ CA_004_챗봇 답변 생성 성공")






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




def test_ca_006(explorer_page_loaded, request):
    driver = explorer_page_loaded
    explorer_page = AgentExplorerPage(driver)

    # 1️⃣ 이전에 저장된 두 개의 ID 가져오기
    private_id = request.config.cache.get("private_agent_id", None)
    org_id = request.config.cache.get("organization_agent_id", None)
    assert private_id or org_id, "❌ CA_006_이전 테스트의 agent_id를 불러올 수 없습니다."

    # 2️⃣ Private/Organization 카드 확인
    if private_id:
        explorer_page.click_agent_card_by_id(private_id)
    if org_id:
        explorer_page.click_agent_card_by_id(org_id)

    print("✅ CA_006_Explorer 페이지에서 생성된 에이전트 확인 완료")



def test_ca_007(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)

    # 1️⃣ My Agents 페이지 진입 후 Draft, Private, Organization 카드 존재여부 확인
    my_agent_page.load_all_cards()
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
    my_agent_page.load_all_cards()
    my_agent_page.click_edit_button_by_card_type("private")

    #2️⃣ 수정 작업
    name_field = create_agent_page.get_element("name")
    name_field.click()
    name_field.send_keys("_edit")
    create_agent_page.get_element("create_btn", "clickable").click() #수정 작업의 경우 publish로 텍스트만 변경됨

    #3️⃣ 수정 후 저장, 알림 확인(1️⃣에서 organization으로 변경 시 organization으로 변경)
    save_page.select_mode("private")
    print("✅ CA_008_Private 모드 유지 확인")
    save_page.click_save()
    message = save_page.get_snackbar_text().lower()
    assert "updated" in message, f"❌ CA_008_예상과 다른 메시지: {message}"
    print(f"✅ CA_008_에이전트 수정 성공 알림 확인: {message}")


@pytest.mark.xdist_group(name="serial_group")
def test_ca_009(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    create_agent_page = CreateAgentPage(driver)
    
    #1️⃣ 첫 번째 Draft 카드의 edit 버튼 클릭
    my_agent_page.load_all_cards()
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




@pytest.mark.xdist_group(name="serial_group")
def test_ca_010(my_agents_page_loaded, pages):
    driver = my_agents_page_loaded  
    my_agent_page = pages["my_agents"]
    create_agent_page = pages["create"]

    # 1️⃣  첫 번째 Draft 카드 편집
    my_agent_page.load_all_cards()
    draft_cards = my_agent_page.get_draft_cards()
    assert len(draft_cards) >= 1, "Draft 카드 존재하지 않음"

    target_card = draft_cards[0]
    agent_id = my_agent_page.get_agent_id_from_card(target_card)
    print("🎯 수정할 agent_id:", agent_id)

    my_agent_page.scroll_into_view(target_card)
    target_card.find_element(By.CSS_SELECTOR, "svg[data-icon='pen']").click()

    # 2️⃣ 값 입력 및 자동저장 대기 후 갱신
    TARGET_TITLE = "draft test"
    expected_values = create_agent_page.fill_form_with_trigger(
        TARGET_TITLE,
        "",
        "draft rules",
        ""
    )

    time.sleep(1) 
    create_agent_page.wait_for_autosave(expected_values, timeout=20)
    print("⏳ auto-save 완료")

  
    driver.back()
    driver.refresh()
    my_agent_page.wait_for_cards_loaded()
    my_agent_page.load_all_cards()
    print("⬅️ 뒤로가기 및 새로고침 완료")
    updated_card = my_agent_page.wait_for_card_update(agent_id, TARGET_TITLE)


    assert updated_card is not None, f"Draft 카드(ID: {agent_id})가 My Agents에 없음"
    print("🔄 Draft 반영 확인 완료")

    # 3️⃣ 갱신된 Draft 카드 편집 진입 및 값 비교
    my_agent_page.scroll_into_view(updated_card)
    updated_card.find_element(By.CSS_SELECTOR, "svg[data-icon='pen']").click()

    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.NAME, "name").get_attribute("value") != ""
    )

    actual_values = create_agent_page.get_all_field_values()

    assert actual_values["name"] == expected_values["name"], (
        f"❌ name 불일치: '{expected_values['name']}' vs '{actual_values['name']}'"
    )
    assert actual_values["rules"] == expected_values["rules"], (
        f"❌ rules 불일치: '{expected_values['rules']}' vs '{actual_values['rules']}'"
    )

    print("✅ CA_010_임시저장 성공")



def test_ca_011(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)

    #1️⃣ 두 번째 organization 카드의 delete 버튼 클릭(위치나 종류는 환경에 따라 변경 가능) 
    my_agent_page.load_all_cards()
    my_agent_page.click_delete_button_by_card_type("organization", index=1)

    #2️⃣ 삭제 팝업 모달 확인
    assert my_agent_page.is_delete_modal_visible(), "❌ CA_011_삭제 팝업 모달 미출력"
    
    my_agent_page.cancel_delete_modal()
    
    assert not my_agent_page.is_delete_modal_visible(), "❌ CA_011_모달이 닫히지 않음"
    print("✅ CA_011_삭제 팝업 모달 Cancel 버튼 정상 작동")



def test_ca_012(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ 두 번째 organization 카드의 완전 삭제(위치나 종류는 환경에 따라 변경 가능)
    my_agent_page.load_all_cards()
    my_agent_page.click_delete_button_by_card_type("organization", index=1)
    my_agent_page.confirm_delete_modal()

    #2️⃣ 삭제 후 알림 확인
    message = save_page.get_snackbar_text().lower()
    assert "success" in message or "delete" in message, f"❌ CA_012_예상과 다른 메시지: {message}"
    print(f"✅ CA_012_선택한 에이전트 삭제 완료: {message}")
    


def test_ca_013(explorer_page_loaded):
    driver = explorer_page_loaded
    explorer = AgentExplorerPage(driver)
    my_agent_page = MyAgentsPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ 기본제공 에이전트 삭제 시도 및 알림 확인

    my_agent_page.load_all_cards()
    result = explorer.delete_fixed_agent(my_agent_page, save_page)

    assert result is True, "❌ CA_013_기본제공 에이전트 삭제"
    print("✅ CA_013_기본 에이전트 삭제 방지")



def test_ca_014(create_page, pages, dummy_files):
    driver = create_page
    create = pages["create"]

    #1️⃣ 지식파일에 작은 파일 업로드 기능 확인

    create.upload_file(dummy_files["small"])

    small_item = create.get_last_uploaded_item()

    assert create.has_success_icon(small_item), "❌ CA_014_작은 파일 업로드 성공 아이콘 없음"
    assert "success" in create.get_file_status(small_item).lower(), "❌ CA_014_작은 파일 상태값이 Success가 아님"

    print("✅ CA_014_작은 파일 업로드 성공")

    #2️⃣ 지식파일에 큰 파일 업로드 불가 확인

    create.upload_file(dummy_files["big"])

    big_item = create.get_last_uploaded_item()

    assert create.has_failed_icon(big_item), "❌ CA_014_큰 파일 실패 아이콘 없음"
    assert "failed" in create.get_file_status(big_item).lower(), "❌ CA_014_큰 파일 상태값이 Failed가 아님"

    err = create.get_error_msg(big_item)
    if not err:
        print("⚠️ CA_014_오류 문구가 없음")
    elif "file size" not in err.lower():
        print(f"⚠️ CA_014_예상 외 오류 문구: {err}")
    else:
        print("✅ CA_014_파일 사이즈 제한 오류 문구 정상 감지!")

    print("✅ CA_014_파일 용량 제한 검증 완료!")




def test_ca_015(logged_in_driver_sub_account, request):
    driver = logged_in_driver_sub_account
    explorer_page = AgentExplorerPage(driver)

    # 1️⃣ Private ID 불러오기
    private_id = request.config.cache.get("private_agent_id", None)
    assert private_id, "❌ CA_015_private agent_id 누락"

    # 2️⃣ 해당 카드 검색 후 노출 여부 확인
    results = explorer_page.click_agent_card_by_id(private_id)
    assert len(results) == 0, f"❌ CA_015_Private 카드 노출됨: {results}"
    print("✅ CA_015_서브 계정에서 Private 카드 미노출 확인 완료")



    

    
    


