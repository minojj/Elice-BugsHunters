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


# 1) Chrome OPTIONS (환경별 분리)

def build_options():
    opts = webdriver.ChromeOptions()
    opts.page_load_strategy = "eager"

    system = platform.system()  # Windows / Linux / Darwin
    is_jenkins = bool(os.getenv("JENKINS_HOME"))

 
    # HEADLESS 설정 (공통)

    if os.getenv("HEADLESS", "true").lower() == "true":
        opts.add_argument("--headless=new")

    # 환경별 분기

    # (1) Jenkins / Docker / Linux
    if is_jenkins or system == "Linux":
        print("🐧 Linux/Jenkins 환경 → 강력한 headless 옵션 적용")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")

    # (2) macOS
    elif system == "Darwin":
        print("🍎 macOS 환경 → 안정적 headless + window-size")
        opts.add_argument("--window-size=1920,1080")

    # (3) Windows
    elif system == "Windows":
        print("🪟 Windows 환경 → scale-factor 적용")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--force-device-scale-factor=1")

    else:
        print(f"🌍 Unknown OS detected: {system}")
        opts.add_argument("--window-size=1920,1080")


    # 공통 최적화 옵션

    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")

    # 이미지 비활성화 (성능 개선)
    opts.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    return opts



# 2) ChromeDriver 경로 결정 (팀원 코드 유지)

def resolve_driver_path():
    sys_driver = os.getenv("CHROMEDRIVER")

    # 1) 직접 chromedriver 경로 지정된 경우
    if sys_driver and os.path.exists(sys_driver):
        print(f"🔧 Using system ChromeDriver: {sys_driver}")
        return sys_driver

    # 2) 기본: webdriver_manager 사용
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeDriverManager().install()   # path 제거 (에러 방지)
    except Exception as e:
        print("❌ webdriver_manager failed:", e)
        raise


# 3) 최종 Chrome driver 생성

def create_driver():
    options = build_options()
    service = Service(resolve_driver_path())
    return webdriver.Chrome(service=service, options=options)



# 4) session-level driver

@pytest.fixture(scope="session")
def driver():
    d = create_driver()
    yield d
    d.quit()



# 5) 메인 계정 로그인 (module-level)

@pytest.fixture(scope="module")
def logged_in_driver(driver):
    login_page = LoginFunction(driver)
    login_page.open()
    login_page.login(
        os.getenv("MAIN_EMAIL"),
        os.getenv("MAIN_PASSWORD")
    )

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]'))
        )
    except TimeoutException:
        Utils(driver).wait_for(timeout=15)

    yield driver



# 6) 서브 계정 로그인 (별도 driver 생성)

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
