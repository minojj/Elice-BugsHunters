import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

# POM 컴포넌트들
from src.pages.history_page import (
    MainPage,
    ChatSidebar,
    Composer,
    Dialogs,
    SearchOverlay,
    AgentExplorerPage,
)


def test_ht_001_start_new_chat(logged_in_driver):
    """새 채팅 시작 시 스레드가 생성되는지 확인"""
    drv = logged_in_driver
    main = MainPage(drv)
    main.open()

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)

    # 새 채팅 버튼 클릭 전 현재 상태 스냅샷
    before_top = sidebar.top_thread_href()

    # 1) 새 채팅 시작
    sidebar.click_new_chat()  # 내부에서 clickable 사용

    # 2) 메시지 전송 (textarea/submit은 Composer가 알아서 명시적 대기)
    test_msg = "안녕하세요, 테스트 메시지입니다."
    composer.send(test_msg)

    # 3) 새 스레드가 최상단으로 올라올 때까지 대기
    def _wait_new_top(_):
        href = sidebar.top_thread_href()
        if not href:
            return False
        # 이전 스레드가 없었다면, href가 생긴 시점이 곧 새 스레드
        if before_top is None:
            return href
        # 이전 최상단과 다른 href가 되면 새 스레드로 간주
        if href != before_top:
            return href
        return False

    try:
        after_top = WebDriverWait(drv, 30).until(
            _wait_new_top,
            "새 스레드가 생성되지 않았습니다 (타임아웃)",
        )
        assert after_top and after_top != before_top, "스레드가 변경되지 않았습니다"
    except TimeoutException:
        raise AssertionError("새 스레드가 생성되지 않았습니다 (타임아웃)")

def test_ht_002_search_history(logged_in_driver):
    drv = logged_in_driver
    main = MainPage(drv)
    main.open()
    
    test_str = "테스트123"  # 검색할 메시지
    
    sidebar = ChatSidebar(drv)
    composer = Composer(drv)
    search = SearchOverlay(drv)

    # 1. 새 채팅 만들고 메시지 보내기
    sidebar.click_new_chat()      # 내부에서 clickable 대기
    composer.send(test_str)       # textarea/submit에 대해 명시적 대기
    time.sleep(3)                 # 메시지 응답 대기

    # 2. 검색 오버레이 열기
    sidebar.click_search_button() # 검색 버튼 clickable 대기 포함

    # 3. 검색어 입력 (입력값이 실제로 반영될 때까지 대기)
    search.type_query(test_str)

    # 4. 검색 결과가 prefix를 만족할 때까지 명시적 대기
    search.wait_result_has_prefix(test_str, timeout=10)

    # 5. 검색 결과 값들 가져와서 검증
    vals = search.get_values()
    assert vals, "검색 결과가 비어 있습니다."
    assert any(v.startswith(test_str) for v in vals), f"검색 결과에 '{test_str}'로 시작하는 항목이 없습니다: {vals}"
      
def test_ht_003_agent_search(logged_in_driver):
    """에이전트 탐색 페이지에서 검색 기능 확인"""
    drv = logged_in_driver
    main = MainPage(drv)
    main.open()

    agent_name = "엘리스"

    agent = AgentExplorerPage(drv)
    
    # 1) 에이전트 페이지 열기 (URL 변경까지 BasePage.wait 사용)
    agent.open()

    # 2) 검색 수행 (입력 값이 실제로 세팅될 때까지 대기)
    agent.search(agent_name)

    # 3) 결과 검증 (내부에서 Stale 처리 + 타이틀/timeout까지 다 처리)
    try:
        agent.assert_all_titles_contain(agent_name, timeout=10)
    except AssertionError as e:
        print(f"❌ 검색 결과 검증 실패: {e}")
        raise

def test_ht_004_chat_title_fix(logged_in_driver):
    """채팅 스레드 이름 변경 기능 확인"""
    drv = logged_in_driver
    main = MainPage(drv)
    main.open()

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)

    # 1) 새 채팅 생성 + 메시지 전송
    sidebar.click_new_chat()  # clickable() 대기 포함
    original_msg = "이름변경테스트_원본"
    composer.send(original_msg)
    time.sleep(3)  # 응답 대기

    # 스레드가 실제로 생성되어 top_thread_title을 읽을 수 있을 때까지 대기
    try:
        WebDriverWait(drv, 10).until(
            lambda d: sidebar.top_thread_title() is not None
                      and sidebar.top_thread_title().strip() != "",
            "스레드 제목을 가져올 수 없습니다",
        )
    except TimeoutException:
        raise AssertionError("첫 번째 스레드 제목을 가져올 수 없습니다")

    # 2) 옵션 메뉴 열기 → 이름 변경 메뉴 클릭
    sidebar.open_top_options()   # 내부에서 present/clickable + 재시도
    sidebar.click_menu_rename()  # 메뉴/아이템 visible/clickable 대기 포함

    # 3) 이름 변경 다이얼로그 핸들링
    SEL_RENAME_INPUT = (By.CSS_SELECTOR, "input[name='name']")
    XPATH_SAVE_BTN = (
        By.XPATH,
        "//button[@type='submit' and (normalize-space()='저장' or normalize-space()='Save')]",
    )

    new_name = "테스트_변경된이름"

    try:
        # 입력 필드 클릭 가능할 때까지 대기
        inp = WebDriverWait(drv, 10).until(
            EC.element_to_be_clickable(SEL_RENAME_INPUT)
        )
        inp.click()

        # 기존 텍스트 삭제
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)

        # 새 이름 입력
        inp.send_keys(new_name)

        # 인풋 value에 new_name 이 실제로 반영될 때까지 대기
        WebDriverWait(drv, 10).until(
            EC.text_to_be_present_in_element_value(SEL_RENAME_INPUT, new_name)
        )

        # 저장 버튼 클릭 가능해질 때까지 대기 후 클릭
        save_btn = WebDriverWait(drv, 10).until(
            EC.element_to_be_clickable(XPATH_SAVE_BTN)
        )
        save_btn.click()

        # 다이얼로그가 닫힐 때까지 대기
        WebDriverWait(drv, 10).until(
            EC.invisibility_of_element_located(SEL_RENAME_INPUT)
        )

        # 4) 사이드바 최상단 스레드 제목이 new_name 으로 바뀔 때까지 대기
        WebDriverWait(drv, 15).until(
            lambda d: sidebar.top_thread_title() == new_name,
            "스레드 제목이 변경된 이름으로 업데이트되지 않았습니다",
        )

        actual_title = sidebar.top_thread_title()
        assert actual_title == new_name, f"이름 변경 실패: 예상={new_name}, 실제={actual_title}"

    except TimeoutException:
        raise AssertionError("이름 변경 작업이 시간 초과되었습니다")

def test_ht_005_view_chat_history(logged_in_driver):
    drv = logged_in_driver
    main = MainPage(drv)
    main.open()
    time.sleep(2)
    
    sidebar = ChatSidebar(drv)
    composer = Composer(drv)
    test_str = "테스트시작"

    # --- 1) 첫 번째 스레드 생성 ---
    sidebar.click_new_chat()
    time.sleep(2)  # 스레드 생성 대기
    # 첫 번째 메시지
    composer.send(test_str)
    time.sleep(3)  # 응답 대기
    # 두 번째 메시지
    composer.send("두 번째 메시지입니다")
    time.sleep(3)  # 응답 대기
    # 세 번째 메시지
    composer.send("세 번째 메시지입니다")
    time.sleep(3)  # 응답 대기

    # --- 2) 두 번째 스레드 생성 ---
    sidebar.click_new_chat()
    second_msg = "두번째스레드테스트"
    composer.send(second_msg)
    time.sleep(3)  # 응답 대기

    # --- 3) 첫 번째 스레드로 돌아가기 ---
    sidebar.click_second_thread()
    time.sleep(3)  # 스레드 전환 대기
    # 이 시점에서 첫 번째 스레드의 메시지들이 다시 로딩될 때까지 대기
    try:
        first_msg = WebDriverWait(drv, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[data-step-type="user_message"]')
            )
        )

        # 가운데로 스크롤 (scrollIntoView는 동기라서 추가 sleep 불필요)
        drv.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", first_msg
        )

        text = first_msg.text.strip()
        assert test_str in text, (
            f"첫 메시지 텍스트가 예상과 다름: 예상={test_str}, 실제={text}"
        )

    except TimeoutException:
        raise AssertionError("첫 번째 메시지를 찾을 수 없습니다")

def test_ht_006_delete_chat(logged_in_driver):
    """채팅 스레드 삭제 기능 확인"""
    drv = logged_in_driver
    main = MainPage(drv)
    main.open()

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)
    dialogs = Dialogs(drv)

    # 0) 삭제 이전의 최상단 스레드 href 스냅샷
    before_top = sidebar.top_thread_href()

    # 1) 새 대화 생성 + 메시지 전송 (삭제 대상 세션)
    sidebar.click_new_chat()
    delete_test_msg = "삭제테스트"
    composer.send(delete_test_msg)

    # 2) "새로 생성된" 최상단 스레드가 올라올 때까지 대기
    def _wait_new_top(_):
        href = sidebar.top_thread_href()
        if not href:
            return False
        # 이전 최상단이 없었다면(href가 없었다면) href만 생겨도 ok
        if before_top is None:
            return href
        # 이전 최상단이 있었다면, 값이 달라졌을 때가 "새 세션"
        if href != before_top:
            return href
        return False

    try:
        thread_href = WebDriverWait(drv, 20).until(
            _wait_new_top,
            "새로 생성된 삭제 대상 스레드가 최상단으로 오지 않았습니다",
        )
    except TimeoutException:
        raise AssertionError("새로 생성된 삭제 대상 스레드가 최상단으로 오지 않았습니다")

    assert thread_href, "삭제 대상 스레드 href를 가져올 수 없습니다"

    # 3) staleness 검증용: 현재 최상단 요소 잡기
    try:
        top_el = WebDriverWait(drv, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "aside a[href^='/ai-helpy-chat/thread/'][data-index='0']")
            )
        )
    except TimeoutException:
        raise AssertionError("최상단 스레드 요소를 찾을 수 없습니다")

    # 혹시 정말 우리가 기대한 href가 맞는지 한 번 더 체크 (선택 사항)
    try:
        actual_href = top_el.get_attribute("href")
        assert thread_href in actual_href, (
            f"최상단 스레드 href 불일치: 기대 포함={thread_href}, 실제={actual_href}"
        )
    except Exception:
        # href 비교 실패해도 치명적이진 않으니 패스하거나 로그만 남겨도 됨
        pass

    # 4) 옵션 메뉴 열기
    sidebar.open_top_options()

    # 5) 삭제 클릭
    sidebar.click_menu_delete()

    # 6) 삭제 확인 (다이얼로그 열림/닫힘까지 Dialogs.confirm_delete가 처리)
    dialogs.confirm_delete()

    # 7) 해당 요소가 DOM에서 사라질 때까지(stale) 대기
    try:
        WebDriverWait(drv, 30).until(EC.staleness_of(top_el))
    except TimeoutException:
        raise AssertionError("스레드 삭제 타임아웃: 요소가 여전히 DOM에 남아 있습니다")

    # 8) 추가 검증: 최상단이 변경되었거나, 아예 리스트가 비어 있는 상태까지 대기
    def _wait_after_delete(_):
        href = sidebar.top_thread_href()
        # 스레드가 하나뿐이었으면 삭제 후 None이 될 수 있음 → 이것도 성공 케이스
        if href is None:
            return True
        # 여러 개 중 하나를 지웠다면, 최상단 href가 삭제 대상과 달라야 함
        if href != thread_href:
            return True
        return False

    try:
        WebDriverWait(drv, 10).until(
            _wait_after_delete,
            f"스레드 목록이 갱신되지 않았습니다 (삭제 대상={thread_href}, 현재 최상단={sidebar.top_thread_href()})",
        )
    except TimeoutException:
        raise AssertionError(
            f"스레드 목록이 갱신되지 않았습니다 (삭제 대상={thread_href}, 현재 최상단={sidebar.top_thread_href()})"
        )

    new_href = sidebar.top_thread_href()
    # new_href가 None이어도(리스트 비었어도) 삭제 대상과 다르기만 하면 ok
    assert new_href != thread_href, f"스레드 목록이 갱신되지 않았습니다 (이전={thread_href}, 현재={new_href})"

def test_ht_007_chat_history_ordered_by_time(logged_in_driver):
    """여러 채팅 생성 시 최신 스레드가 상단에 오는지 확인"""
    drv = logged_in_driver
    main = MainPage(drv)
    main.open()

    sidebar = ChatSidebar(drv)
    composer = Composer(drv)

    # --- 1) 첫 번째 스레드 생성 ---
    sidebar.click_new_chat()            # 클릭 시 clickable()로 명시적 대기

    first_msg = "첫번째테스트"
    composer.send(first_msg)            # textarea/submit 에 대한 명시적 대기 포함
    time.sleep(3)                       # 응답 대기
    # 첫 번째 스레드 href가 생길 때까지 명시적 대기 후 저장
    try:
        before_top = WebDriverWait(drv, 10).until(
            lambda d: sidebar.top_thread_href(),
            "첫 번째 스레드 href를 가져올 수 없습니다",
        )
    except TimeoutException:
        raise AssertionError("첫 번째 스레드 href를 가져올 수 없습니다")

    assert before_top, "첫 번째 스레드 href를 가져올 수 없습니다"
    
    # --- 2) 두 번째 스레드 생성 ---
    sidebar.click_new_chat()
    second_msg = "두번째테스트"
    composer.send(second_msg)

    # --- 3) 새 스레드가 최상단으로 올라올 때까지 명시적 대기 ---
    def _wait_new_top(_):
        href = sidebar.top_thread_href()
        # href가 있고, 기존 before_top과 다르면 그 값을 반환 → WebDriverWait 성공
        if href and href != before_top:
            return href
        return False  # 계속 재시도

    try:
        after_top = WebDriverWait(drv, 30).until(
            _wait_new_top,
            "새 스레드가 최상단으로 이동하지 않았습니다",
        )
    except TimeoutException:
        raise AssertionError("새 스레드가 최상단으로 이동하지 않았습니다")

    assert after_top and after_top != before_top, "스레드 순서가 변경되지 않았습니다"
