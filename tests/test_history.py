import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# POM 컴포넌트들
from src.pages.ht_composer import Composer
from src.pages.ht_chat_sidebar import ChatSidebar
from src.pages.ht_search_overlay import SearchOverlay
from src.pages.ht_dialogs import Dialogs
from src.pages.ht_agent_explorer_page import AgentExplorerPage

MAIN_URL = "https://qaproject.elice.io/ai-helpy-chat"

def _goto_main(drv):
    """메인 페이지로 이동하고 완전히 로드될 때까지 대기"""
    drv.get(MAIN_URL)
    
    # 페이지 로드 대기
    WebDriverWait(drv, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    # Composer가 준비될 때까지 대기
    composer = Composer(drv)
    composer.wait_ready()
    
    # 추가적인 안정화 시간
    time.sleep(1)

def test_ht_001_start_new_chat(logged_in_driver):
    """새 채팅 시작 시 스레드가 생성되는지 확인"""
    drv = logged_in_driver
    _goto_main(drv)

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)

    # 새 채팅 버튼 클릭 전 현재 상태 저장
    before_top = sidebar.top_thread_href()
    
    sidebar.click_new_chat()
    time.sleep(0.5)  # 새 채팅 UI 전환 대기

    # 메시지 전송
    test_msg = "안녕하세요, 테스트 메시지입니다."
    composer.send(test_msg)
    
    # 응답 시작 대기 (스레드 생성 시간 고려)
    time.sleep(3)

    # 스레드 변경 확인 (더 긴 시간 대기)
    try:
        WebDriverWait(drv, 30).until(
            lambda d: (sidebar.top_thread_href() is not None) and 
                     (sidebar.top_thread_href() != before_top)
        )
        after_top = sidebar.top_thread_href()
        print(f"새 최상단 스레드: {after_top}")
        assert after_top and after_top != before_top, "스레드가 변경되지 않았습니다"
    except TimeoutException:
        raise AssertionError("새 스레드가 생성되지 않았습니다 (타임아웃)")

def test_ht_002_search_history(logged_in_driver):
    drv = logged_in_driver
    _goto_main(drv)
    
    test_str = "테스트123"  # 검색할 메시지
    
    sidebar = ChatSidebar(drv)
    composer = Composer(drv)
    search = SearchOverlay(drv)

    # 1. 새 채팅 만들고 메시지 보내기
    sidebar.click_new_chat()
    composer.send(test_str)
    
    # 2. 
    time.sleep(5)  
    
    # 3. 검색하기
    sidebar.click_search_button()
    search.type_query(test_str)
    time.sleep(3)
    # 4. 검색 결과 확인
    vals = search.get_values()
    
    # 5. 
    assert any(v.startswith(test_str) for v in vals)
      
def test_ht_003_agent_search(logged_in_driver):
    """에이전트 탐색 페이지에서 검색 기능 확인"""
    drv = logged_in_driver
    _goto_main(drv)
    agent_name = "엘리스"

    agent = AgentExplorerPage(drv)
    
    # 에이전트 페이지 열기
    agent.open()
    time.sleep(2)  # 페이지 전환 완전 대기
    
    # 검색 수행
    agent.search(agent_name)
    time.sleep(2)  # 검색 결과 로딩 대기
    
    # 결과 검증
    try:
        agent.assert_all_titles_contain(agent_name)
        print(f"✅ test_ht_003: 모든 에이전트 제목에 '{agent_name}' 포함 확인")
    except AssertionError as e:
        print(f"❌ 검색 결과 검증 실패: {e}")
        raise

def test_ht_004_chat_title_fix(logged_in_driver):
    """채팅 스레드 이름 변경 기능 확인"""
    drv = logged_in_driver
    _goto_main(drv)

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)

    # 새 채팅 생성
    sidebar.click_new_chat()
    time.sleep(0.5)
    
    original_msg = "이름변경테스트_원본"
    composer.send(original_msg)
    
    # 스레드 생성 대기
    time.sleep(3)

    # 옵션 메뉴 열기
    sidebar.open_top_options()
    time.sleep(0.5)  # 메뉴 애니메이션 대기
    
    sidebar.click_menu_rename()
    time.sleep(0.5)  # 다이얼로그 애니메이션 대기

    # 이름 변경 (인라인 처리)
    from selenium.webdriver.common.keys import Keys
    SEL_RENAME_INPUT = (By.CSS_SELECTOR, "input[name='name']")
    XPATH_SAVE_BTN = (By.XPATH, "//button[@type='submit' and (normalize-space()='저장' or normalize-space()='Save')]")

    new_name = "테스트_변경된이름"
    
    try:
        # 입력 필드 찾기 및 수정
        inp = WebDriverWait(drv, 10).until(
            EC.visibility_of_element_located(SEL_RENAME_INPUT)
        )
        inp.click()
        time.sleep(0.2)
        
        # 기존 텍스트 완전 삭제
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        time.sleep(0.2)
        
        # 새 이름 입력
        inp.send_keys(new_name)
        time.sleep(0.5)
        
        # 저장 버튼 클릭
        save_btn = WebDriverWait(drv, 10).until(
            EC.element_to_be_clickable(XPATH_SAVE_BTN)
        )
        save_btn.click()
        
        # 다이얼로그 닫힘 대기
        WebDriverWait(drv, 10).until(
            EC.invisibility_of_element_located(SEL_RENAME_INPUT)
        )
        
        # 이름 변경 확인 (약간의 지연 후)
        time.sleep(1)
        
        # 변경된 이름 확인
        WebDriverWait(drv, 15).until(
            lambda d: sidebar.top_thread_title() == new_name
        )
        
        actual_title = sidebar.top_thread_title()
        assert actual_title == new_name, f"이름 변경 실패: 예상={new_name}, 실제={actual_title}"
        
    except TimeoutException:
        raise AssertionError("이름 변경 작업이 시간 초과되었습니다")

def test_ht_005_view_chat_history(logged_in_driver):
    """여러 메시지 전송 후 스레드 간 이동 확인"""
    drv = logged_in_driver
    _goto_main(drv)

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)
    test_str = "테스트시작"

    # 첫 번째 스레드 생성
    sidebar.click_new_chat()
    time.sleep(0.5)
    
    composer.send(test_str)
    time.sleep(2)
    
    composer.send("두 번째 메시지입니다")
    time.sleep(2)
    
    composer.send("세 번째 메시지입니다")
    time.sleep(3)

    # 두 번째 스레드 생성
    sidebar.click_new_chat()
    time.sleep(0.5)
    
    second_msg = "두번째스레드테스트"
    composer.send(second_msg)
    time.sleep(3)

    # 첫 번째 스레드로 돌아가기
    sidebar.click_second_thread()
    time.sleep(2)  # 페이지 전환 대기

    # 첫 번째 메시지 확인
    try:
        first_msg = WebDriverWait(drv, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-step-type="user_message"]'))
        )
        
        # 스크롤하여 메시지 표시
        drv.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", first_msg)
        time.sleep(1)  # 스크롤 완료 대기
        
        text = first_msg.text.strip()
        assert test_str in text, f"첫 메시지 텍스트가 예상과 다름: 예상={test_str}, 실제={text}"
        
    except TimeoutException:
        raise AssertionError("첫 번째 메시지를 찾을 수 없습니다")

def test_ht_006_delete_chat(logged_in_driver):
    """채팅 스레드 삭제 기능 확인"""
    drv = logged_in_driver
    _goto_main(drv)

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)
    dialogs = Dialogs(drv)

    # 1. 새 대화 생성
    sidebar.click_new_chat()
    time.sleep(0.5)
    
    delete_test_msg = "삭제테스트"
    composer.send(delete_test_msg)
    
    # 2. 응답 완료 대기
    time.sleep(3)
    composer.wait_ready()
    
    # 3. 삭제할 스레드의 정보 저장
    thread_href = sidebar.top_thread_href()
    assert thread_href, "최상단 스레드를 찾을 수 없습니다"
    
    # 4. 최상단 요소 참조 (staleness 검증용)
    try:
        top_el = WebDriverWait(drv, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "aside a[href^='/ai-helpy-chat/thread/'][data-index='0']"))
        )
    except TimeoutException:
        raise AssertionError("최상단 스레드 요소를 찾을 수 없습니다")
    
    # 5. 옵션 메뉴 열기
    sidebar.open_top_options()
    time.sleep(1)  # 메뉴 완전 오픈 대기
    
    # 6. 삭제 클릭
    sidebar.click_menu_delete()
    time.sleep(1)  # 다이얼로그 오픈 대기
    
    # 7. 삭제 확인
    dialogs.confirm_delete()
    
    # 8. 스레드가 사라질 때까지 대기
    try:
        assert WebDriverWait(drv, 30).until(
            EC.staleness_of(top_el)
        ), "스레드가 삭제되지 않았습니다"
    except TimeoutException:
        raise AssertionError("스레드 삭제 타임아웃")
    
    # 9. 추가 검증: href가 변경되었는지 확인
    time.sleep(1)  # DOM 업데이트 완전 대기
    
    new_href = sidebar.top_thread_href()
    assert new_href != thread_href, f"스레드 목록이 갱신되지 않았습니다 (이전={thread_href}, 현재={new_href})"

def test_ht_007_chat_history_ordered_by_time(logged_in_driver):
    """여러 채팅 생성 시 최신 스레드가 상단에 오는지 확인"""
    drv = logged_in_driver
    _goto_main(drv)

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)

    # 첫 번째 스레드 생성
    sidebar.click_new_chat()
    time.sleep(0.5)
    
    first_msg = "첫번째"
    composer.send(first_msg)
    time.sleep(3)
    
    before_top = sidebar.top_thread_href()
    assert before_top, "첫 번째 스레드 href를 가져올 수 없습니다"

    # 두 번째 스레드 생성
    sidebar.click_new_chat()
    time.sleep(0.5)
    
    second_msg = "두번째"
    composer.send(second_msg)
    time.sleep(3)

    # 스레드 순서 변경 확인
    try:
        WebDriverWait(drv, 30).until(
            lambda d: (sidebar.top_thread_href() is not None) and 
                     (sidebar.top_thread_href() != before_top)
        )
        
        after_top = sidebar.top_thread_href()
        assert after_top and after_top != before_top, "스레드 순서가 변경되지 않았습니다"
        
    except TimeoutException:
        raise AssertionError("새 스레드가 최상단으로 이동하지 않았습니다")
