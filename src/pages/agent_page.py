from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.helpers import wait_for

class AgentPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat"

    def open(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 사이트 접속 성공")
    
    def login(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginId']"))
        )
        self.driver.find_element(By.CSS_SELECTOR, "input[name='loginId']").send_keys("team3@elice.com")
        self.driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys("team3elice!@") 
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()  
        
        print("✅ 아이디 비번 입력완료")
        
    def is_logged_in(self):
        try:
            # 로그인 성공 후 나타나는 화면 요소 (예시: 채팅창)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='billing/payments/credit']"))
            )
            print("✅ 로그인 성공! 테스트 종료합니다.")
            self.driver.quit()  # ✅ 브라우저 종료
            return True
        except:
            print("❌ 로그인 실패 또는 화면 미출력")
            self.driver.quit()  # 실패 시에도 브라우저 닫기
            return False