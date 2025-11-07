import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- URLs & 계정 ---
LOGIN_URL = (
    "https://accounts.elice.io/accounts/signin/me"
    "?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat&lang=en-US&org=qaproject"
)
MAIN_URL = "https://qaproject.elice.io/ai-helpy-chat"

EMAIL = "team3@elice.com"
PASSWORD = "team3elice!@"

# --- 셀렉터 (안정성 중심) ---
# 헤더 햄버거(사이드바 토글) : 아이콘 data-testid 사용
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

# 사이드바 최상단(가상 스크롤 환경에서 신뢰 가능한) 쓰레드 Anchor
SEL_TOP_THREAD = (
    By.CSS_SELECTOR,
    "aside a[href^='/ai-helpy-chat/thread/'][data-index='0']",
)

# --- 공통 유틸 ---
def wait(drv, sec=10):
    return WebDriverWait(drv, sec)

@pytest.fixture(scope="session")
def driver():
    opts = Options()
    # 필요하면 주석 해제
    # opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()

def _open_sidebar_if_collapsed(drv):
    # 아이콘 버튼이 보이면 클릭(접혀있는 상태로 간주)
    try:
        burger = wait(drv, 2).until(EC.element_to_be_clickable(SEL_BURGER))
        # svg → 상위 button으로 이벤트 위임되는 경우가 있어 상위로 클릭 전달
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
    # 보이는 textarea가 클릭 가능해질 때까지 대기
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

    # 4) 최상단 쓰레드가 바뀌었는지로 검증 (가상 스크롤에서도 안전)
    wait(driver, 20).until(
        lambda d: (_top_thread_href(d) is not None) and (_top_thread_href(d) != before_top)
    )
    after_top = _top_thread_href(driver)
    assert after_top and after_top != before_top, f"최상단 세션 갱신 실패: before={before_top}, after={after_top}"