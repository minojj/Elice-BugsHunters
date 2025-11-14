import os
import platform
import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from src.utils.helpers import Utils
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from src.pages.login_page import LoginFunction

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)



#  공통 드라이버 생성 (OS / Jenkins 자동 감지)

def create_chrome_driver():
    options = webdriver.ChromeOptions()

    system = platform.system()  # Windows / Linux / Darwin(mac)


    #  1) Jenkins / Docker (Linux headless)

    if os.environ.get("JENKINS_HOME") or system == "Linux":
        print("🌐 Running in Jenkins/Linux environment")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")


    #  2) macOS

    elif system == "Darwin":
        print("🍎 Running on macOS")
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")


    #  3) Windows (local)
  
    else:
        print("🪟 Running on Windows")
        # GUI로 띄울 수도 있고, headless도 가능
        options.add_argument("--headless=new")
        options.add_argument("--force-device-scale-factor=1")
        options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)



#  session-level driver

@pytest.fixture(scope="session")
def driver():
    driver = create_chrome_driver()
    yield driver
    driver.quit()



#  메인 계정 로그인

@pytest.fixture(scope="module")
def logged_in_driver(driver):
    try:
        login_page = LoginFunction(driver)
        login_page.open()
        login_page.login(
            os.getenv("MAIN_EMAIL"),
            os.getenv("MAIN_PASSWORD")
        )
        print("✅ 로그인 성공")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat"]')
            )
        )
        print("✅ 메인 페이지 로드 확인 완료")

    except TimeoutException:
        Utils(driver).wait_for(timeout=15)

    yield driver



#  서브 계정 로그인

@pytest.fixture
def logged_in_driver_sub_account():
    sub_driver = create_chrome_driver()

    login_page = LoginFunction(sub_driver)
    login_page.open()
    login_page.login(
        os.getenv("SUB_EMAIL"),
        os.getenv("SUB_PASSWORD")
    )
    print("✅ 서브 계정 로그인 성공")

    yield sub_driver
    sub_driver.quit()