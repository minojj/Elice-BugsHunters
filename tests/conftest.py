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



# 1) HEADLESS 여부


def is_headless():
    return os.getenv("HEADLESS", "true").lower() == "true"



# 2) OPTIONS 구성 (환경 공통)


def build_options():
    opts = webdriver.ChromeOptions()
    opts.page_load_strategy = "eager"

    if is_headless():
        opts.add_argument("--headless=new")

    for a in [
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--disable-extensions",
        "--disable-infobars"
    ]:
        opts.add_argument(a)

    # 이미지 비활성화 → 성능 향상
    opts.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    return opts



# 3) ChromeDriver 경로 결정


def resolve_driver_path():
    sys_driver = os.getenv("CHROMEDRIVER")

    # 환경변수 CHROMEDRIVER가 설정된 경우
    if sys_driver and os.path.exists(sys_driver):
        print(f"🔧 Using system chromedriver: {sys_driver}")
        return sys_driver

    # webdriver_manager 기본
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeDriverManager().install()
    except Exception as e:
        print("❌ webdriver_manager failed:", e)
        raise



# 4) Driver 생성


def create_driver():
    system = platform.system()

    if os.getenv("JENKINS_HOME"):
        print("🌐 Running in Jenkins CI (Linux based)")
    else:
        print(f"💻 Running on {system} (headless={is_headless()})")

    service = Service(resolve_driver_path())
    return webdriver.Chrome(service=service, options=build_options())



# 5) WAIT TIME 보정 (macOS headless only)


def get_wait(driver):
    system = platform.system()

    if system == "Darwin" and is_headless():
        return WebDriverWait(driver, 20)   # mac headless → 2배 증가
    return WebDriverWait(driver, 10)




# 6) session-level driver


@pytest.fixture(scope="session")
def driver():
    d = create_driver()
    yield d
    d.quit()


# 7) 로그인 (메인 계정)


@pytest.fixture(scope="module")
def logged_in_driver(driver):
    login_page = LoginFunction(driver)
    wait = get_wait(driver)

    login_page.open()
    login_page.login(
        os.getenv("MAIN_EMAIL"),
        os.getenv("MAIN_PASSWORD")
    )

    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]'))
        )
    except TimeoutException:
        Utils(driver).wait_for(timeout=15)

    yield driver


# 8) 로그인 (서브 계정) - 별도 driver

@pytest.fixture(scope="module")
def logged_in_driver_sub_account():
    d = create_driver()
    wait = get_wait(d)

    login_page = LoginFunction(d)
    login_page.open()
    login_page.login(
        os.getenv("SUB_EMAIL"),
        os.getenv("SUB_PASSWORD")
    )

    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]'))
        )
    except TimeoutException:
        Utils(d).wait_for(timeout=15)

    yield d
    d.quit()