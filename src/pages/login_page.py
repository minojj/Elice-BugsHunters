import logging
from math import log  
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)    
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
            "email_error": (By.XPATH, "//p[contains(text(), 'already registered')]"),
            "remove_history" : (By.XPATH, "//a[text()='Remove history']"),
            "avatar_btn" : (By.CSS_SELECTOR, "button:has(svg[data-testid='PersonIcon'])"),
            "logout_btn" : (By.XPATH, "//p[text()='Logout']")
        }

    # === Page Actions ===

    def open(self):
        # 페이지 열기
        self.driver.get(self.locators["main"])
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.debug(f"페이지 로드 완료: {self.driver.current_url}")



    def login(self, email, password):
        wait = WebDriverWait(self.driver, 10)
    # 이메일 입력 필드 또는 비밀번호 필드가 먼저 나타날 수 있기 때문에
    # 두 가지 중 하나가 나타날 때까지 기다림
        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located(self.locators["email"]),
                    EC.presence_of_element_located(self.locators["password"])
                )
            )
        except TimeoutException:
            print("❌ 로그인 페이지 요소를 찾지 못했습니다.")
            return

        # remove 버튼 존재 여부 체크
        try:    
            remove_btn = wait.until(EC.element_to_be_clickable(self.locators["remove_history"]))
            remove_btn.click()
            print("저장된 계정 초기화 완료")
        except TimeoutException:
            print("저장된 계정이 없어 제거 단계 생략")

        # 이메일 입력 가능 상태 만들기
        try:
            email_input = wait.until(EC.element_to_be_clickable(self.locators["email"]))
            email_input.clear()
            email_input.send_keys(email)
        except TimeoutException:
            print("⚠️ 이메일 입력 필드를 찾지 못해, 비밀번호 필드만 활성화된 상태로 보입니다.")
            # 이메일 입력창이 숨겨진 경우, 로그인 이메일 선택 화면일 수 있음
            try:
                email_select = self.driver.find_element(*self.locators["email"])
                email_select.click()
                email_input = wait.until(EC.presence_of_element_located(self.locators["email"]))
                email_input.send_keys(email)
            except (Exception, NoSuchElementException):
                print("이메일 입력 필드를 활성화할 수 없습니다.")
                return

        # 비밀번호 입력
        try:
            password_input = wait.until(EC.presence_of_element_located(self.locators["password"]))
            password_input.clear()
            password_input.send_keys(password)
        # 로그인 버튼 클릭
            wait.until(EC.element_to_be_clickable(self.locators["submit_btn"])).click()
            return

        except TimeoutException:
            print("❌ 비밀번호 입력 필드를 찾지 못했습니다.")
            return  

    def is_logged_in(self):
        # 로그인 성공 여부 확인
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.locators["billing"])
            )
            print("✅ 로그인 성공!")
            return True
        except TimeoutException:
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
        
        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(self.locators["name"])
        )

        print("✅ 'Create account with email' 클릭 완료")

    def check_name_field(self):
        # 회원가입 창 정상적으로 (이름)필드를 통해서 정상 동작 확인
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.locators["name"])
            )
            print("✅ 이름 입력 필드가 표시되었습니다.")
            return True
        except TimeoutException:
            print("❌ 이름 입력 필드가 표시되지 않았습니다.")
            return False
        
    def fill_signup_form(self, email):
        # 회원가입 폼 입력 (현재는 이메일만 입력하지만, 추가 입력 필드가 있을 경우 확장 가능)
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.locators["email"])
        )
        email_input.send_keys(email)
        print("✅ 이메일 입력 완료")
    
    def email_error(self):
        # 중복 이메일 에러 메시지 확인
        try:
            error_el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.locators["email_error"])
            )
            return error_el
        except TimeoutException:
            return None
       
    def clear_login_session(self):
        #브라우저 세션 초기화
        self.driver.delete_all_cookies()
        self.driver.refresh()
        print("로그인 세션 초기화 완료")
        
    def remove_history(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located(self.locators["remove_history"])).click()
        
    def clear_element(self):
        self.driver.find_element(*self.locators["email"]).clear()
        self.driver.find_element(*self.locators["password"]).clear()
        
    def logout(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located(self.locators["avatar_btn"])).click()
        wait.until(EC.presence_of_element_located(self.locators["logout_btn"])).click()
        print("✅ 로그아웃 클릭 완료")
        
    def logout_check(self):
        try:
            # 이메일이나 비밀번호 입력 필드 등장 대기
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    EC.visibility_of_element_located(self.locators["email"]),
                    EC.visibility_of_element_located(self.locators["password"])
                )
            
            )
            print("✅ 정상 로그아웃")
            return True
        
        except TimeoutException:
            print("❌ 비정상 로그아웃")
            return False
        
    
        
