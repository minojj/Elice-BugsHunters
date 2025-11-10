import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# --- URLs & 계정 ---
LOGIN_URL = (
    "https://accounts.elice.io/accounts/signin/me"
    "?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat&lang=en-US&org=qaproject"
)
MAIN_URL = "https://qaproject.elice.io/ai-helpy-chat"

EMAIL = "team3@elice.com"
PASSWORD = "team3elice!@"

# --- 셀렉터 (안정성 중심) ---
SEL_BURGER = (By.CSS_SELECTOR, "header button svg[data-testid='barsIcon']")

# 사이드바 '새 대화' 버튼 : role="button" + 텍스트 매칭
SEL_NEW_CHAT_BTN = (
    By.XPATH,
    "//aside//div[@role='button'][.//span[normalize-space()='새 대화']]",
)

# 메시지 입력 textarea (보이는 것만; composer 내부, 숨김/readonly 제외)
SEL_TEXTAREA = (
    By.CSS_SELECTOR,
    "#message-composer .MuiInputBase-root textarea.MuiInputBase-input:not([aria-hidden='true']):not([readonly])",
)

# 전송 버튼(활성화 상태)
SEL_SUBMIT_ENABLED = (By.CSS_SELECTOR, "button#chat-submit:not([disabled])")

# 최상단 쓰레드(데이터 인덱스 0) 앵커
SEL_TOP_THREAD = (
    By.CSS_SELECTOR,
    "aside a[href^='/ai-helpy-chat/thread/'][data-index='0']",
)

# 최상단 쓰레드 내부의 옵션(점3개) 버튼
SEL_TOP_THREAD_MENU_BTN = (
    By.CSS_SELECTOR,
    "aside a[href^='/ai-helpy-chat/thread/'][data-index='0'] .menu-button button"
)

# 메뉴 UL
SEL_MENU_UL = (By.CSS_SELECTOR, "ul.MuiMenu-list[role='menu']")

# '이름 변경' 항목 (한/영 모두 대응)
XPATH_MENU_RENAME = (
    "//ul[contains(@class,'MuiMenu-list') and @role='menu']"
    "//li[.//*[normalize-space()='이름 변경'] or .//*[normalize-space()='Rename']]"
)

# 이름 변경 다이얼로그 입력 & 저장
SEL_RENAME_INPUT = (By.CSS_SELECTOR, "input[name='name']")
XPATH_SAVE_BTN = "//button[@type='submit' and (normalize-space()='저장' or normalize-space()='Save')]"

# --- [추가] 메뉴 '삭제' 셀렉터 (한/영 대응) ---
XPATH_MENU_DELETE = (
    "//ul[contains(@class,'MuiMenu-list') and @role='menu']"
    "//li[.//*[normalize-space()='삭제'] or .//*[normalize-space()='Delete']]"
)

# (선택) 아이콘 폴백: 휴지통 아이콘으로 li 찾기
CSS_MENU_TRASH_ICON = "li svg[data-icon='trash']"

# --- [추가] 삭제 확인 다이얼로그 셀렉터 ---
SEL_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")

# 다이얼로그 안의 '삭제/Delete' 버튼 (텍스트 기반, 로케일 대응)
XPATH_DIALOG_DELETE_BTN = (
    ".//button[@type='button' and "
    " (normalize-space()='삭제' or normalize-space()='Delete' or "
    "  .//*[normalize-space()='삭제'] or .//*[normalize-space()='Delete'])]"
)

# --- 공통 유틸 ---
def wait(drv, sec=10):
    return WebDriverWait(drv, sec)

@pytest.fixture(scope="session")
def driver():
    opts = Options()
    # 필요하면 headless 사용
    # opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    # 테스트 동작 눈으로 보려면 detach 유지
    opts.add_experimental_option("detach", True)
    drv = webdriver.Chrome(options=opts)
    yield drv
    # 눈으로 확인하려면 종료 막기
    # drv.quit()

def _open_sidebar_if_collapsed(drv):
    # 아이콘 버튼이 보이면 클릭(접힘 → 펼치기)
    try:
        burger = wait(drv, 2).until(EC.element_to_be_clickable(SEL_BURGER))
        burger.find_element(By.XPATH, "./ancestor::button").click()
    except TimeoutException:
        pass  # 이미 열려 있음

def _login(drv):
    drv.get(LOGIN_URL)

    email_input = wait(drv).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='loginId']"))
    )
    pwd_input = wait(drv).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
    )

    email_input.clear(); email_input.send_keys(EMAIL)
    pwd_input.clear();   pwd_input.send_keys(PASSWORD)

    submit_btn = wait(drv).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "form button[type='submit']"))
    )
    submit_btn.click()

    # 메인 도착 & composer 노출까지 대기
    wait(drv, 20).until(EC.visibility_of_element_located(SEL_TEXTAREA))
    assert MAIN_URL in drv.current_url, f"메인 페이지로 이동 실패: {drv.current_url}"

def _click_new_chat(drv):
    _open_sidebar_if_collapsed(drv)
    btn = wait(drv).until(EC.element_to_be_clickable(SEL_NEW_CHAT_BTN))
    btn.click()

def _send_message(drv, text="안녕"):
    ta = wait(drv).until(EC.element_to_be_clickable(SEL_TEXTAREA))
    ta.click()
    try:
        ta.send_keys(text)
    except Exception:
        # 드물게 interactable 문제시 JS 폴백
        drv.execute_script(
            """
            const el = arguments[0];
            el.value = arguments[1];
            el.dispatchEvent(new Event('input', {bubbles:true}));
            """,
            ta, text
        )

    submit = wait(drv, 20).until(EC.element_to_be_clickable(SEL_SUBMIT_ENABLED))
    submit.click()

def _top_thread_href(drv):
    try:
        el = wait(drv, 3).until(EC.presence_of_element_located(SEL_TOP_THREAD))
        return el.get_attribute("href")
    except TimeoutException:
        return None

def _top_thread_title(drv):
    """최상단 쓰레드의 제목 텍스트를 추출"""
    top = wait(drv, 10).until(EC.visibility_of_element_located(SEL_TOP_THREAD))
    # 보통 내부에 <p>가 제목 노드로 들어감
    try:
        return top.find_element(By.CSS_SELECTOR, "p").text.strip()
    except Exception:
        return (top.text or "").strip()

def _open_top_thread_options(drv):
    """사이드바 최상단 대화 항목 위에 호버 → 우측 옵션 버튼 클릭"""
    _open_sidebar_if_collapsed(drv)

    top = wait(drv).until(EC.presence_of_element_located(SEL_TOP_THREAD))
    drv.execute_script("arguments[0].scrollIntoView({block:'center'});", top)

    ActionChains(drv).move_to_element(top).pause(0.2).perform()

    try:
        btn = wait(drv, 5).until(EC.element_to_be_clickable(SEL_TOP_THREAD_MENU_BTN))
        btn.click()
    except TimeoutException:
        # 폴백: headless 환경에서 hover 미감지 시 JS로 강제
        drv.execute_script("""
            const el = arguments[0];
            el.dispatchEvent(new MouseEvent('mouseover', {bubbles:true}));
            el.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
            el.dispatchEvent(new MouseEvent('mousemove', {bubbles:true}));
        """, top)
        btn = wait(drv, 5).until(EC.presence_of_element_located(SEL_TOP_THREAD_MENU_BTN))
        drv.execute_script("arguments[0].click();", btn)

def _click_menu_rename(drv, timeout=5):
    """열려있는 옵션 메뉴에서 '이름 변경' 항목 클릭"""
    menu = wait(drv, timeout).until(EC.visibility_of_element_located(SEL_MENU_UL))
    try:
        item = menu.find_element(By.XPATH, ".//li[.//*[normalize-space()='이름 변경'] or .//*[normalize-space()='Rename']]")
    except NoSuchElementException:
        try:
            pen = menu.find_element(By.CSS_SELECTOR, "li svg[data-icon='pen']")
            item = pen.find_element(By.XPATH, "./ancestor::li[1]")
        except Exception:
            raise AssertionError("메뉴에서 '이름 변경' 항목을 찾지 못했습니다.")
    drv.execute_script("arguments[0].scrollIntoView({block:'center'});", item)
    try:
        wait(drv, timeout).until(EC.element_to_be_clickable((By.XPATH, XPATH_MENU_RENAME)))
        item.click()
    except TimeoutException:
        drv.execute_script("arguments[0].click();", item)

def _rename_top_thread_and_save(drv, new_title: str):
    """이름 변경 다이얼로그에서 제목을 바꾸고 저장"""
    # 입력창
    inp = wait(drv, 10).until(EC.visibility_of_element_located(SEL_RENAME_INPUT))
    drv.execute_script("arguments[0].scrollIntoView({block:'center'});", inp)
    inp.click()
    # 안전하게 초기화 후 입력
    try:
        inp.clear()
    except Exception:
        pass
    inp.send_keys(Keys.CONTROL, "a")
    inp.send_keys(Keys.DELETE)
    inp.send_keys(new_title)

    # 저장 클릭
    save = wait(drv, 10).until(
        EC.element_to_be_clickable((By.XPATH, XPATH_SAVE_BTN))
    )
    try:
        save.click()
    except Exception:
        drv.execute_script("arguments[0].click();", save)

    # 다이얼로그 닫힘 대기(입력창 사라짐)
    wait(drv, 10).until(EC.invisibility_of_element_located(SEL_RENAME_INPUT))

# --- [추가] 메뉴에서 '삭제' 클릭 (확인 다이얼로그 처리 없음) ---
def _click_menu_delete(drv, timeout=5):
    # 메뉴가 떠 있을 때만 호출하세요 (_open_top_thread_options 이후)
    menu = wait(drv, timeout).until(EC.visibility_of_element_located(SEL_MENU_UL))

    # 1) 텍스트로 '삭제/Delete' 찾기
    try:
        item = menu.find_element(
            By.XPATH, ".//li[.//*[normalize-space()='삭제'] or .//*[normalize-space()='Delete']]"
        )
    except NoSuchElementException:
        # 2) 폴백: 휴지통 아이콘으로 li 찾기
        try:
            icon = menu.find_element(By.CSS_SELECTOR, CSS_MENU_TRASH_ICON)
            item = icon.find_element(By.XPATH, "./ancestor::li[1]")
        except Exception:
            raise AssertionError("메뉴에서 '삭제' 항목을 찾지 못했습니다.")

    # 클릭
    drv.execute_script("arguments[0].scrollIntoView({block:'center'});", item)
    try:
        wait(drv, timeout).until(EC.element_to_be_clickable((By.XPATH, XPATH_MENU_DELETE)))
        item.click()
    except TimeoutException:
        # 드물게 clickable 판정이 늦는 경우 JS 폴백
        drv.execute_script("arguments[0].click();", item)

def _confirm_delete_in_dialog(drv, timeout=10):
    """삭제 확인 다이얼로그의 빨간 '삭제' 버튼을 클릭하고 닫힘까지 대기"""
    dlg = wait(drv, timeout).until(EC.visibility_of_element_located(SEL_DIALOG))

    # 버튼 찾기 (로케일/구조 변화 대비: 텍스트 우선)
    try:
        btn = dlg.find_element(By.XPATH, XPATH_DIALOG_DELETE_BTN)
    except NoSuchElementException:
        # 폴백: 빨간 contained 에러 버튼(MUI)을 힌트로 탐색
        try:
            btn = dlg.find_element(
                By.CSS_SELECTOR,
                "button.MuiButton-containedError, button.MuiButton-colorError"
            )
        except Exception:
            raise AssertionError("삭제 확인 다이얼로그에서 '삭제' 버튼을 찾지 못했습니다.")

    # 클릭 가능까지 대기 후 클릭 (로딩 스피너 대응)
    try:
        wait(drv, timeout).until(EC.element_to_be_clickable(btn))
        btn.click()
    except Exception:
        drv.execute_script("arguments[0].click();", btn)

    # 다이얼로그 닫힘 확인
    wait(drv, timeout).until(EC.invisibility_of_element_located(SEL_DIALOG))

# --- 테스트 ---
@pytest.mark.e2e
def test_ht_001(driver):
    # 0) 로그인
    _login(driver)

    # 1) 최상단 스냅샷
    _open_sidebar_if_collapsed(driver)
    before_top = _top_thread_href(driver)

    # 2) 새 대화 클릭 (일부 환경에선 여기서 이미 새 세션 생성)
    _click_new_chat(driver)

    # 2-1) 클릭 직후 최상단 변경(신규 세션 생성) 여부를 짧게 체크
    try:
        wait(driver, 5).until(
            lambda d: (_top_thread_href(d) is not None) and (_top_thread_href(d) != before_top)
        )
    except TimeoutException:
        pass  # 아직이면 메시지 전송으로 이어감

    # 3) 메시지 전송
    _send_message(driver, "안녕")

    # 4) 최상단 쓰레드 변경 검증 (가상 스크롤에서도 안전)
    wait(driver, 20).until(
        lambda d: (_top_thread_href(d) is not None) and (_top_thread_href(d) != before_top)
    )
    after_top = _top_thread_href(driver)
    assert after_top and after_top != before_top, f"최상단 세션 갱신 실패: before={before_top}, after={after_top}"

    # 5) 최상단 옵션 열고, '이름 변경' 클릭
    _open_top_thread_options(driver)
    _click_menu_rename(driver)

    # 6) 제목을 '안녕123'으로 변경 후 저장
    target = "안녕123"
    _rename_top_thread_and_save(driver, target)

    # 7) 사이드바 최상단 제목이 기대값으로 갱신됐는지 검증
    wait(driver, 10).until(lambda d: _top_thread_title(d) == target)
    actual = _top_thread_title(driver)
    assert actual == target, f"제목 변경 실패: expected={target}, actual={actual}"

    _open_top_thread_options(driver)  # 점3개 열기
    _click_menu_delete(driver)        # 삭제 항목 클릭 (여기까지만)

    # 8) 삭제 확인 다이얼로그에서 '삭제' 버튼 클릭
    deleted_href = after_top  # 방금 만든 최상단 쓰레드가 삭제 대상
    _confirm_delete_in_dialog(driver)

    # 9) 삭제 결과 검증: 최상단이 바뀌었는지(=삭제된 href와 달라졌는지) 확인
    wait(driver, 20).until(
        lambda d: (_top_thread_href(d) is not None) and (_top_thread_href(d) != deleted_href)
    )
    new_top = _top_thread_href(driver)
    assert new_top != deleted_href, f"삭제 후 최상단이 갱신되지 않았습니다. deleted={deleted_href}, current_top={new_top}"

    # (선택) 사이드바 DOM에 삭제된 항목이 더 이상 존재하지 않는지 추가 확인
    # 존재한다면 가상 스크롤 영역 밖일 수 있어 엄격 검증은 비활성화. 필요 시 아래 주석 해제:
    # with pytest.raises(TimeoutException):
    #     wait(driver, 2).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, f"aside a[href='{deleted_href}']"))
    #     )