import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.utils.helpers import Utils
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from src.pages.login_page import LoginFunction
from src.utils.helpers import Utils 

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
    
@pytest.fixture(scope="session")
def logged_in_driver(driver) :
    try :
        login_page = LoginFunction(driver)
        login_page.open()
        login_page.login("team3@elice.com","team3elice!@")
        print("✅ 로그인 성공")
    except TimeoutException :
        print("✅ 현재 로그인 상태")
        
    Utils(driver).wait_for(timeout=15)
    print("✅ 로그인 대기 완료")

    yield driver

#서브 계정으로 로그인하는 fixture

@pytest.fixture(scope="function")
def logged_in_driver_sub_account():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    sub_driver = webdriver.Chrome(service=service, options=options)
    login_page = LoginFunction(sub_driver)
    login_page.open()
    login_page.login("team3a@elice.com", "team3aelice!@@")
    print("✅ 서브 계정 로그인 성공")

    yield sub_driver
    sub_driver.quit()  # 여기서 닫아도 main driver 영향 없음