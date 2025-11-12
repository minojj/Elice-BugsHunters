import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.utils.helpers import Utils
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from src.pages.login_page import LoginFunction


@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # ✅ 최신 버전 방식
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    yield driver
    driver.quit()
    
@pytest.fixture
def logged_in_driver(driver) :
    try :
        login_page = LoginFunction(driver)
        login_page.open()
        login_page.login("team3@elice.com","team3elice!@")
        print("✅ 로그인 성공")
    except TimeoutException :
        Utils(driver).wait_for(timeout=15)
    

    yield driver
