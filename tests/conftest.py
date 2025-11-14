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

def build_options():
    opts = webdriver.ChromeOptions()
    opts.page_load_strategy = "eager"
    if os.getenv("HEADLESS", "true").lower() == "true":
        opts.add_argument("--headless=new")
    for a in ["--disable-gpu","--no-sandbox","--disable-dev-shm-usage","--window-size=1920,1080","--disable-extensions","--disable-infobars"]:
        opts.add_argument(a)
    # 이미지 비활성화로 속도 향상
    opts.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    return opts

def resolve_driver_path():
    sys_driver = os.getenv("CHROMEDRIVER", "/usr/bin/chromedriver")
    if os.getenv("WDM_SKIP") == "1":
        return sys_driver
    # Linux ARM이면 시스템 드라이버 우선
    if platform.system() == "Linux" and platform.machine().lower() in ("arm64","aarch64") and os.path.exists(sys_driver):
        return sys_driver
    # 그 외에는 webdriver_manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        cache = os.getenv("WDM_CACHE", os.path.join(os.getcwd(), ".wdm"))
        os.makedirs(cache, exist_ok=True)
        return ChromeDriverManager(path=cache).install()
    except Exception:
        return sys_driver

def create_driver():
    return webdriver.Chrome(service=Service(resolve_driver_path()), options=build_options())

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
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]')))
    except TimeoutException:
        Utils(driver).wait_for(timeout=15)
    yield driver

@pytest.fixture(scope="module")
def logged_in_driver_sub_account():
    d = create_driver()
    login = LoginFunction(d)
    login.open()
    login.login(os.getenv("SUB_EMAIL"), os.getenv("SUB_PASSWORD"))
    yield d
    d.quit()