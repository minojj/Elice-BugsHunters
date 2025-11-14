import os
import platform
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from src.pages.login_page import LoginFunction
from src.utils.helpers import Utils

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)



# 1) Chrome Options 구성

def build_options():
    opts = webdriver.ChromeOptions()
    opts.page_load_strategy = "eager"

    # HEADLESS 환경 변수로 제어
    if os.getenv("HEADLESS", "true").lower() == "true":
        opts.add_argument("--headless=new")

    # 공통 옵션
    for a in [
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--disable-extensions",
        "--disable-infobars"
    ]:
        opts.add_argument(a)

    # 이미지 로딩 비활성화
    opts.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    return opts



# 2) Chrome 드라이버 경로 결정 (팀원 코드 유지)

def resolve_driver_path():
    """Always use webdriver_manager unless a real system CHROMEDRIVER path is provided."""
    sys_driver = os.getenv("CHROMEDRIVER")

    # 1) 환경변수로 시스템 chromedriver 강제 지정한 경우
    if sys_driver and os.path.exists(sys_driver):
        print(f"🔧 Using system ChromeDriver: {sys_driver}")
        return sys_driver

    # 2) 기본값: webdriver_manager 사용
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeDriverManager().install()   # ❗ path 파라미터 제거
    except Exception as e:
        print("❌ webdriver_manager failed:", e)
        raise


# 3) 최종 driver 생성 + OS별 메시지 추가

def create_driver():
    system = platform.system()  # Windows / Linux / Darwin

    if os.getenv("JENKINS_HOME"):
        print("🌐 Running on Jenkins (Linux-based CI)")
    else:
        if system == "Windows":
            print("🪟 Running on Windows")
        elif system == "Darwin":
            print("🍎 Running on macOS")
        elif system == "Linux":
            print("🐧 Running on Linux")
        else:
            print(f"🌍 Unknown OS detected: {system}")

    options = build_options()
    service = Service(resolve_driver_path())
    return webdriver.Chrome(service=service, options=options)



# 4) session-level driver

@pytest.fixture(scope="session")
def driver():
    d = create_driver()
    yield d
    d.quit()


# 5) 메인 계정 로그인

@pytest.fixture(scope="module")
def logged_in_driver(driver):
    login_page = LoginFunction(driver)
    login_page.open()
    login_page.login(
        os.getenv("MAIN_EMAIL"),
        os.getenv("MAIN_PASSWORD")
    )

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]'))
        )
    except TimeoutException:
        Utils(driver).wait_for(timeout=3)

    yield driver



# 6) 서브 계정 로그인 — 별도 driver 생성

@pytest.fixture(scope="module")
def logged_in_driver_sub_account():
    d = create_driver()
    login_page = LoginFunction(d)
    login_page.open()
    login_page.login(
        os.getenv("SUB_EMAIL"),
        os.getenv("SUB_PASSWORD")
    )
    yield d
    d.quit()
