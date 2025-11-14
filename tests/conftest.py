import os
import platform
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from src.pages.login_page import LoginFunction
from src.utils.helpers import Utils

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def build_options():
    opts = webdriver.ChromeOptions()
    # 기본 headless (환경변수 HEADLESS=false면 비활성)
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    if headless:
        opts.add_argument("--headless=new")
    # 공통 안정화 옵션
    for arg in [
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--disable-extensions",
        "--disable-infobars"
    ]:
        opts.add_argument(arg)
    return opts

def create_driver():
    # Jenkins / Linux 환경이면 chromium 우선 시도
    is_ci = bool(os.getenv("JENKINS_HOME")) or platform.system() == "Linux"
    # WDM_SKIP=1 이면 시스템 드라이버 사용 (컨테이너에서 /usr/bin/chromedriver)
    if os.getenv("WDM_SKIP") == "1":
        path = os.getenv("CHROMEDRIVER", "/usr/bin/chromedriver")
        return webdriver.Chrome(service=Service(path), options=build_options())
    # webdriver_manager (chromium 우선 → 실패 시 기본 Chrome)
    from webdriver_manager.core.utils import ChromeType
    try:
        path = ChromeDriverManager(
            chrome_type=ChromeType.CHROMIUM if is_ci else ChromeType.GOOGLE
        ).install()
    except Exception:
        path = ChromeDriverManager().install()
    return webdriver.Chrome(service=Service(path), options=build_options())

@pytest.fixture(scope="session")
def driver():
    d = create_driver()
    yield d
    d.quit()

@pytest.fixture(scope="module")
def logged_in_driver(driver):
    login = LoginFunction(driver)
    login.open()
    login.login(os.getenv("MAIN_EMAIL"), os.getenv("MAIN_PASSWORD"))
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]')
        )
    except TimeoutException:
        Utils(driver).wait_for(timeout=15)
    yield driver

@pytest.fixture
def logged_in_driver_sub_account():
    d = create_driver()
    login = LoginFunction(d)
    login.open()
    login.login(os.getenv("SUB_EMAIL"), os.getenv("SUB_PASSWORD"))
    yield d
    d.quit()