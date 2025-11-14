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



# 1) HEADLESS 설정

def is_headless():
    """
    macOS는 기본값 false
    Windows/Linux/Jenkins 기본값 true
    (사용자가 .env 에서 override 가능)
    """
    system = platform.system()

    default = "false" if system == "Darwin" else "true"
    return os.getenv("HEADLESS", default).lower() == "true"




# 2) Chrome OPTIONS (환경별 완전 분기)


def build_options():
    opts = webdriver.ChromeOptions()

    # page_load_strategy → mac headless 안정화를 위해 eager 제거
    opts.page_load_strategy = "normal"

    system = platform.system()

    # 🔥 Headless 설정
    if is_headless():
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")  # headless 안정화
        opts.add_argument("--disable-software-rasterizer")  # mac 렌더링 버그 해결
        opts.add_argument("--use-gl=swiftshader")  # mac headless WebGL 강화

  
    # 공통 옵션

    for a in [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--disable-extensions",
        "--disable-infobars"
    ]:
        opts.add_argument(a)


    # macOS ONLY 옵션
 
    if system == "Darwin":
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-software-rasterizer")
        opts.add_argument("--use-angle=metal")


    # 이미지 로딩 비활성화

    opts.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    return opts



# 3) ChromeDriver 경로 결정 (팀원 기능 그대로 유지)


def resolve_driver_path():
    sys_driver = os.getenv("CHROMEDRIVER")

    # 1) 환경변수로 시스템 chromedriver 지정한 경우
    if sys_driver and os.path.exists(sys_driver):
        print(f"🔧 Using system ChromeDriver: {sys_driver}")
        return sys_driver

    # 2) webdriver_manager 사용 (path 파라미터 제거!)
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeDriverManager().install()
    except Exception as e:
        print("❌ webdriver_manager failed:", e)
        raise


# 4) Driver 생성 + 환경 메시지


def create_driver():
    system = platform.system()

    if os.getenv("JENKINS_HOME"):
        print("🌐 Running on Jenkins (Linux CI)")
    else:
        print(f"💻 Running on {system} | headless={is_headless()}")

    options = build_options()
    service = Service(resolve_driver_path())
    return webdriver.Chrome(service=service, options=options)


# 5) macOS headless 안정화 → wait 2배 증가


def get_wait(driver):
    if platform.system() == "Darwin" and is_headless():
        return WebDriverWait(driver, 20)
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
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]')
            )
        )
    except TimeoutException:
        Utils(driver).wait_for(timeout=15)

    yield driver


# 8) 로그인 (서브 계정)


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
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]')
            )
        )
    except TimeoutException:
        Utils(d).wait_for(timeout=15)

    yield d
    d.quit()