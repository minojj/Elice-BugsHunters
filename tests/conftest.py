from math import log
import os 
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

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # ✅ 최신 버전 방식
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options, keep_alive=True)
    driver.set_page_load_timeout(120)
    
    yield driver
    
    try:
        driver.quit()
    except Exception:
        pass


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

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((login_page.locators["avatar_btn"])))
        print("✅ 메인 페이지 로드 확인 완료")

    except TimeoutException:
        Utils(driver).wait_for(timeout=15)

    yield driver


    


#서브 계정으로 로그인하는 fixture

@pytest.fixture
def logged_in_driver_sub_account():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    sub_driver = webdriver.Chrome(service=service, options=options)
    login_page = LoginFunction(sub_driver)
    login_page.open()
    login_page.login(
        os.getenv("SUB_EMAIL"),
        os.getenv("SUB_PASSWORD")
    )
    print("✅ 서브 계정 로그인 성공")

    yield sub_driver
    sub_driver.quit()