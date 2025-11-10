from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

# --- 설정 정보 ---
BASE_URL = "https://qatrack.elice.io/ai-helpy-chat"

# TEST 로그인 정보 (기존 코드의 USER_ID/USER_PW 대신 사용)
testID = "97minho97@daum.net"
testPW = "wkdalsgh97!"

# 로그인 필드 로케이터
ID_FIELD_LOCATOR = (By.NAME, "loginId")
PW_FIELD_LOCATOR = (By.NAME, "password")
LOGIN_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[type="submit"]')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# --- 테스트 함수 ---

def TEST_CB_001():

    try:
        # 브라우저 최대화 및 페이지 접속
        driver.maximize_window()
        driver.get(BASE_URL)
        print(f"'{BASE_URL}' 접속 완료.")

        # Explicit Wait 설정 (최대 10초 대기)
        wait = WebDriverWait(driver, 10)

        # 1. ID 입력 필드 찾기 및 ID 입력
        print("ID 필드를 찾고 ID를 입력합니다...")
        id_field = wait.until(EC.presence_of_element_located(ID_FIELD_LOCATOR))
        id_field.send_keys(testID)

        # 2. 비밀번호 입력 필드 찾기 및 비밀번호 입력
        print("PW 필드를 찾고 비밀번호를 입력합니다...")
        pw_field = wait.until(EC.presence_of_element_located(PW_FIELD_LOCATOR))
        pw_field.send_keys(testPW)

        # 3. 로그인 버튼 찾기 및 클릭
        print("로그인 버튼을 찾고 클릭합니다...")
        login_button = wait.until(EC.element_to_be_clickable(LOGIN_BUTTON_LOCATOR))
        login_button.click()

        # 로그인 후 다음 페이지 로드를 위해 잠시 대기
        time.sleep(3)

        # 4. 로그인 성공/실패 확인
        # 로그인 성공 시 URL이 BASE_URL과 다르거나 특정 성공 요소가 나타나야 함
        # 여기서는 BASE_URL(로그인 페이지)에서 벗어났는지 확인
        current_url = driver.current_url

        if "login" not in current_url and "accounts/signin" not in current_url:
            print(f"\n:white_check_mark: 테스트 통과: 로그인 성공, 현재 URL: {current_url}")
        else:
            print(f"\n:x: 테스트 실패: URL이 변경되지 않았거나 로그인 페이지에 남아있습니다. 현재 URL: {current_url}")

    except Exception as e:
        print(f"\n:x: 테스트 실패: 오류 발생 - {e}")

# --- 메인 실행 ---
if __name__ == "__main__":
    TEST_CB_001()

    # 모든 테스트 완료 후 브라우저 종료 (TEST_AC_001 코드 스타일을 따름)
    if 'driver' in globals() and driver is not None:
        print("\n테스트 완료. 브라우저를 종료합니다.")
        driver.quit()
