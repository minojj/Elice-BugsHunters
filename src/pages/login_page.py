from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC 


class LoginFunction:
    def __init__(self, driver):
        self.driver = driver

    locators = {
        "main": "https://qaproject.elice.io/ai-helpy-chat",
        "email": (By.CSS_SELECTOR, "input[name='loginId']"),
        "password": (By.CSS_SELECTOR, "input[name='password']"),
        "submit_btn": (By.CSS_SELECTOR, "button[type='submit']"),
        "billing": (By.CSS_SELECTOR, "a[href*='billing/payments/credit']"),
        "create_acc_btn": (By.CSS_SELECTOR, "a[href*='/accounts/signup']"),
        "create_email_btn": (By.XPATH, '//button[@type="button" and contains(@class, "MuiButton-containedPrimary")]'),
        "name": (By.CSS_SELECTOR, "input[name='fullname']"),
        "email_error": (By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error"),
        "remove_history" : (By.XPATH, "//a[text()='Remove history']")
    }

    # === Page Actions ===

    def open(self):
        # 페이지 열기
        self.driver.get(self.locators["main"])
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 사이트 접속 성공")

    def login(self, email = "team3@elice.com", password = "team3elice!@"):
        # 로그인 수행
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.locators["email"])
        )
        self.driver.find_element(*self.locators["email"]).send_keys(email)
        self.driver.find_element(*self.locators["password"]).send_keys(password)
        self.driver.find_element(*self.locators["submit_btn"]).click()
        print("✅ 아이디/비밀번호 입력 및 로그인 버튼 클릭 완료")

    def is_logged_in(self):
        # 로그인 성공 여부 확인
        try:
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.locators["billing"])
            )
            print("✅ 로그인 성공! 테스트 종료합니다.")
            return True
        except Exception:
            print("❌ 로그인 실패")
            return False

    def create_acc(self):
        # 회원가입 → 이메일로 계정 생성 페이지 이동
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.locators["create_acc_btn"])
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.locators["create_email_btn"])
        ).click()

        print("✅ 'Create account with email' 클릭 완료")

    def check_name_field(self):
        # 회원가입 창 정상적으로 (이름)필드를 통해서 정상 동작 확인
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.locators["name"])
            )
            print("✅ 이름 입력 필드가 표시되었습니다.")
            return True
        except Exception:
            print("❌ 이름 입력 필드가 표시되지 않았습니다.")
            return False
        
    def fill_signup_form(self, email):
        # 회원가입 폼 입력 (이메일만 입력)
        
        self.driver.find_element(*self.locators["email"]).send_keys(email)
        
        print("✅ 이메일 입력 완료")
    
    def email_error(self):
        return self.driver.find_element(*self.locators["email_error"])
    
    def clear_login_session(self):
        #브라우저 세션 초기화
        self.driver.delete_all_cookies()
        self.driver.refresh()
        print("로그인 세션 초기화 완료")
        
    def remove_history(self):
        self.driver.find_element(*self.locators["remove_history"]).click()
        
