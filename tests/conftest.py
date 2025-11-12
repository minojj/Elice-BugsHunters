import os 
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.utils.helpers import Utils
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from src.pages.login_page import LoginFunction

def pytest_configure(config):
    """pytest_configure hook을 사용하여 사용자 정의 마커 'gui_test'를 등록합니다."""
    config.addinivalue_line(
        "markers", "gui_test: marks test as requiring a GUI (X Display)"
    )

def pytest_runtest_setup(item):
    """
    각 테스트가 실행되기 전에 GUI 필요 여부를 확인합니다.
    """
    # 테스트에 'gui_test' 마커가 붙어 있는지 확인합니다.
    is_gui_test = any(mark.name == "gui_test" for mark in item.iter_markers())

    # 리눅스 시스템이면서, DISPLAY 환경 변수가 설정되지 않은 경우
    if is_gui_test and os.name == "posix" and not os.environ.get("DISPLAY"):
        # GUI 환경이 필요하지만 DISPLAY 변수가 없으므로 테스트를 건너뜁니다.
        pytest.skip("Requires X DISPLAY (GUI). Skipping test in headless environment.", allow_module_level=False)

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    # ✅ headless 모드 비활성화 - 브라우저 창을 보면서 테스트 가능
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")  # 실제 창을 띄울 때는 GPU 사용 가능
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")  # 창 최대화

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
        login_page.login("team3@elice.com", "team3elice!@")
        print("✅ 로그인 성공")
    except TimeoutException :
        Utils(driver).wait_for(timeout=15)
    

    yield driver

#서브 계정으로 로그인하는 fixture

@pytest.fixture
def logged_in_driver_sub_account():
    options = webdriver.ChromeOptions()
    # ✅ 서브 계정도 headless 비활성화 (필요시 주석 해제)
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    sub_driver = webdriver.Chrome(service=service, options=options)
    login_page = LoginFunction(sub_driver)
    login_page.open()
    login_page.login("team3a@elice.com", "team3aelice!@@")
    print("✅ 서브 계정 로그인 성공")

    yield sub_driver
    sub_driver.quit()  # 여기서 닫아도 main driver 영향 없음
