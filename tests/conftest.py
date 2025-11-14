import os
import platform
import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from src.pages.login_page import LoginFunction
from src.utils.helpers import Utils

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def build_options():
    opts = webdriver.ChromeOptions()
    # 빠른 로드
    opts.page_load_strategy = "eager"
    # 기본 headless
    if os.getenv("HEADLESS", "true").lower() == "true":
        opts.add_argument("--headless=new")
    # 안정화 옵션
    for arg in [
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--disable-extensions",
        "--disable-infobars",
    ]:
        opts.add_argument(arg)
    # 이미지 비활성(가속)
    prefs = {"profile.managed_default_content_settings.images": 2}
    opts.add_experimental_option("prefs", prefs)
    return opts

def resolve_driver_path():
    system = platform.system()
    arch = platform.machine().lower()
    sys_driver = os.getenv("CHROMEDRIVER", "/usr/bin/chromedriver")

    # 강제: 시스템 드라이버
    if os.getenv("WDM_SKIP") == "1":
        print(f"[webdriver] WDM_SKIP=1 -> {sys_driver}")
        return sys_driver

    # Linux ARM이면 시스템 드라이버 우선(amd64 바이너리 크래시 방지)
    if system == "Linux" and arch in ("aarch64", "arm64") and os.path.exists(sys_driver):
        print(f"[webdriver] Linux {arch} -> system chromedriver 사용: {sys_driver}")
        return sys_driver

    # 그 외: webdriver_manager 사용 + 캐시 사용
    cache_dir = os.getenv("WDM_CACHE", os.path.join(os.getcwd(), ".wdm"))
    os.makedirs(cache_dir, exist_ok=True)
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        path = ChromeDriverManager(path=cache_dir).install()
        print(f"[webdriver] webdriver_manager path: {path}")
        return path
    except Exception as e:
        print(f"[webdriver] webdriver_manager 실패: {e} -> {sys_driver} 폴백")
        return sys_driver

def create_chrome_driver():
    service = Service(resolve_driver_path())
    return webdriver.Chrome(service=service, options=build_options())

@pytest.fixture(scope="session")
def driver():
    d = create_chrome_driver()
    yield d
    d.quit()

@pytest.fixture(scope="module")
def logged_in_driver(driver):
    try:
        login_page = LoginFunction(driver)
        login_page.open()
        login_page.login(os.getenv("MAIN_EMAIL"), os.getenv("MAIN_PASSWORD"))
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]')))
    except TimeoutException:
        Utils(driver).wait_for(timeout=15)
    yield driver

@pytest.fixture(scope="module")  # 기존 function -> module로 변경해 생성 횟수 감소
def logged_in_driver_sub_account():
    d = create_chrome_driver()
    login_page = LoginFunction(d)
    login_page.open()
    login_page.login(os.getenv("SUB_EMAIL"), os.getenv("SUB_PASSWORD"))
    yield d
    d.quit()