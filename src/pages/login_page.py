from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_page import BasePage

class LoginFunction(BasePage):
    locators = {
        "main": "https://qaproject.elice.io/ai-helpy-chat",
        "email": (By.CSS_SELECTOR, "input[name='loginId']"),
        "password": (By.CSS_SELECTOR, "input[name='password']"),
        "submit_btn": (By.CSS_SELECTOR, "button[type='submit']"),
        "billing": (By.CSS_SELECTOR, "a[href*='billing/payments/credit']"),
        "create_acc_btn": (By.CSS_SELECTOR, "a[href*='/accounts/signup']"),
        "create_email_btn": (
            By.XPATH,
            '//button[@type="button" and contains(@class, "MuiButton-containedPrimary")]',
        ),
        "name": (By.CSS_SELECTOR, "input[name='fullname']"),
        "email_error": (By.XPATH, "//p[contains(text(), 'already registered')]"),
        "remove_history": (By.XPATH, "//a[text()='Remove history']"),
        "avatar_btn": (By.XPATH, "//button[.//*[@data-testid='PersonIcon']]"),
        "logout_any": (By.XPATH, "//*[text()='Logout' or text()='로그아웃']"),
        }

    


    def __init__(self, driver):
        super().__init__(driver)

    # === Page Actions ===

    def open(self):
        self.driver.get(self.locators["main"])
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def login(self, email, password):
        wait = WebDriverWait(self.driver, 3)

        # 이메일 또는 패스워드 필드 대기
        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located(self.locators["email"]),
                    EC.presence_of_element_located(self.locators["password"]),
                )
            )
        except TimeoutException:
            return

        # remove history 버튼
        try:
            remove_btn = self.get_element("remove_history", wait_type="clickable", timeout=3)
            remove_btn.click()
        except TimeoutException:
            pass

        # email 입력
        try:
            email_input = self.get_element("email", wait_type="clickable", timeout=3)
            email_input.clear()
            email_input.send_keys(email)
        except TimeoutException:
            try:
                email_select = self.driver.find_element(*self.locators["email"])
                email_select.click()
                email_input = self.get_element("email", wait_type="presence", timeout=3)
                email_input.send_keys(email)
            except (Exception, NoSuchElementException):
                return

        # password 입력 + 로그인 버튼 클릭
        try:
            password_input = self.get_element("password", wait_type="presence", timeout=3)
            password_input.clear()
            password_input.send_keys(password)

            self.click_safely("submit_btn", timeout=3)
            return

        except TimeoutException:
            return

    def is_logged_in(self):
        try:
            self.get_element("billing", wait_type="visible", timeout=5)
            return True
        except TimeoutException:
            print("❌ 로그인 실패")
            return False

    def create_acc(self):
        self.click_safely("create_acc_btn", timeout=10)
        self.click_safely("create_email_btn", timeout=10)
        self.get_element("name", wait_type="visible", timeout=10)

    def check_name_field(self):
        try:
            self.get_element("name", wait_type="visible", timeout=10)
            return True
        except TimeoutException:
            print("❌ 이름 입력 필드가 표시되지 않았습니다.")
            return False

    def fill_signup_form(self, email):
        email_input = self.get_element("email", wait_type="presence", timeout=10)
        email_input.send_keys(email)

    def email_error(self):
        try:
            return self.get_element("email_error", wait_type="presence", timeout=5)
        except TimeoutException:
            return False

    def clear_login_session(self):
        self.driver.delete_all_cookies()
        self.driver.refresh()

    def remove_history(self):
        self.click_safely("remove_history", timeout=10)

    def logout(self):
        try:
            self.click_safely("avatar_btn", timeout=10)
            try:
                self.get_element("logout_any", wait_type="presence", timeout=10).click()
            except TimeoutException:
                print("❌ 로그아웃 버튼을 찾지 못했습니다.")
                return
        except TimeoutException:
            print("❌ 아바타 버튼 클릭 실패.")

    def logout_check(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    EC.visibility_of_element_located(self.locators["email"]),
                    EC.visibility_of_element_located(self.locators["password"]),
                )
            )
            return True

        except TimeoutException:
            print("❌ 비정상 로그아웃")
            return False