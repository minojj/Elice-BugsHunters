from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 기본 설정
BASE_URL = "https://qaproject.elice.io/ai-helpy-chat"

# 일반 로그인 정보
USERNAME = "team3@elice.com"
PASSWORD = "team3elice!@"

# WebDriver 초기화 및 대기 객체 생성 (전역)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 30)

def TEST_CB_001():
    """로그인 및 기본 검색 기능 테스트"""
    print("--- TEST_CB_001: 로그인 및 기본 검색 테스트 시작 ---")
    try:
        # 페이지 접속
        driver.get(BASE_URL)
        
        # 로그인 입력 필드를 찾고 아이디와 비밀번호를 입력
        login = wait.until(EC.presence_of_element_located((By.NAME, "loginId")))
        login.send_keys(USERNAME)
        
        pw = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        pw.send_keys(PASSWORD)
        
        # 로그인 버튼을 찾아 클릭
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        login_btn.click()
        print("✅ 로그인 버튼 클릭 완료")
        
        # 대화창으로 전환될 때까지 대기 (예: 특정 엘리먼트 확인)
        wait.until(EC.presence_of_element_located((By.ID, 'chat-submit')))
        print("✅ 로그인 후 대화 페이지 로딩 완료")

        # 검색 기능 테스트
        search_term = "안녕하세요."
        
        # 검색창이 입력 가능할 때까지 대기
        search_box = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.MuiInputBase-root.MuiInputBase-multiline textarea')
        ))
        search_box.send_keys(search_term)
        print(f"✅ 검색어 입력 완료: {search_term}")

        # 검색 버튼 클릭
        search_btn = wait.until(EC.element_to_be_clickable((By.ID, 'chat-submit')))
        search_btn.click()
        print("✅ 검색 버튼 클릭 완료")
        
        print("--- TEST_CB_001: 로그인 및 기본 검색 테스트 완료 ---")
        return True # 성공적으로 검색까지 완료했음을 반환

    except TimeoutException as e:
        print("❌ TEST_CB_001 실패: 요소를 찾지 못했거나 시간 초과:", e)
    except Exception as e:
        print("❌ TEST_CB_001 실패: 치명적 오류 발생:", e)
    return False


def TEST_CB_002():
    """AI 응답 내용 복사 기능 테스트"""
    print("\n--- TEST_CB_002: 대화 내용 복사 기능 테스트 시작 ---")
    
    try:
        AI_RESPONSE_XPATH = "//div[@role='article'][contains(text(), '안녕하세요!')]"

        last_ai_response = wait.until(
            EC.presence_of_element_located((By.XPATH, AI_RESPONSE_XPATH))
        )
        print("✅ AI 응답 메시지 확인 완료.")

        COPY_BUTTON_SELECTOR = 'button[data-state="closed"]' 
        
        try:
            copy_btn = last_ai_response.find_element(By.CSS_SELECTOR, COPY_BUTTON_SELECTOR)
        except NoSuchElementException:
            copy_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, COPY_BUTTON_SELECTOR)))
            
        copy_btn.click()
        print("✅ 복사 버튼 클릭 완료.")

        print("--- TEST_CB_002: 대화 내용 복사 기능 테스트 완료 (클립보드 확인 필요) ---")
        return True
        
    except TimeoutException as e:
        print(f"❌ TEST_CB_002 실패: 요소를 찾지 못했거나 시간 초과 (AI 응답 또는 복사 버튼): {e}")
    except Exception as e:
        print(f"❌ TEST_CB_002 실패: 오류 발생: {e}")
    return False

# 메인 실행
if TEST_CB_001():
    TEST_CB_002()
    
# 결과 확인을 위해 사용자 입력 대기 (두 테스트 모두 완료 후)
print("\n--- 모든 테스트 스크립트 실행 완료 ---")
input("Enter 키를 누르면 브라우저가 종료됩니다...")
    
driver.quit()