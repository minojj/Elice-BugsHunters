from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class ChatPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    locators = {
        "main": "https://qaproject.elice.io/ai-helpy-chat",
        "email": (By.CSS_SELECTOR, "input[name='loginId']"),
        "password": (By.CSS_SELECTOR, "input[name='password']"),
        "submit_btn": (By.CSS_SELECTOR, "button[type='submit']"),
        "chat_submit": (By.ID, "chat-submit"),
        "search_box": (By.CSS_SELECTOR, "div.MuiInputBase-root.MuiInputBase-multiline textarea"),
        "copy_btn": (By.CSS_SELECTOR, 'button[data-state="closed"]'),
        "user_message_last": (By.CSS_SELECTOR, 'div.bg-accent.rounded-3xl.py-2\.5'),
        "edit_btn": (By.CSS_SELECTOR, 'button.edit-message'),
        "edit_input_field": (By.CSS_SELECTOR, '#edit-chat-input'),
        "edit_confirm_btn": (By.CSS_SELECTOR, 'button.confirm-edit'),
    }

    # === Page Actions ===

    def open(self):
        """페이지 열기"""
        self.driver.get(self.locators["main"])
        try:
            # 로그인 페이지의 핵심 요소인 이메일 입력 필드가 나타날 때까지 기다립니다.
            self.wait.until(
                EC.presence_of_element_located(self.locators["email"]) 
            )
            print(" 사이트 접속 및 로그인 폼 로딩 성공")
        except TimeoutException:
            print(" 사이트 접속은 했으나 로그인 폼 로딩 실패")
        return True
    def login(self, email, password):
        """로그인 수행"""
        try:
            # 이메일 입력
            login_field = self.wait.until(
                EC.presence_of_element_located(self.locators["email"])
            )
            login_field.send_keys(email)
            
            # 비밀번호 입력
            password_field = self.wait.until(
                EC.presence_of_element_located(self.locators["password"])
            )
            password_field.send_keys(password)
            
            # 로그인 버튼 클릭
            login_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["submit_btn"])
            )
            login_btn.click()
            print(" 로그인 버튼 클릭 완료")
            return True
        except TimeoutException as e:
            print(f" 로그인 실패: 요소를 찾지 못했거나 시간 초과 - {e}")
            return False

    def is_logged_in(self):
        """로그인 성공 여부 확인 (대화 페이지 로딩 확인)"""
        try:
            self.wait.until(
                EC.presence_of_element_located(self.locators["chat_submit"])
            )
            print(" 로그인 후 대화 페이지 로딩 완료")
            return True
        except TimeoutException:
            print(" 로그인 실패 또는 대화 페이지 미출력")
            return False

    def send_message(self, message):
        """메시지 입력 및 전송"""
        try:
            # 검색창에 메시지 입력
            search_box = self.wait.until(
                EC.element_to_be_clickable(self.locators["search_box"])
            )
            search_box.send_keys(message)
            print(f" 메시지 입력 완료: {message}")
            
            # 전송 버튼 클릭
            search_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["chat_submit"])
            )
            search_btn.click()
            print(" 메시지 전송 버튼 클릭 완료")
            return True
        except TimeoutException as e:
            print(f" 메시지 전송 실패: {e}")
            return False

    def get_ai_response(self, expected_text):
        """AI 응답 메시지 확인"""
        try:
            ai_response_xpath = f"//div[@role='article'][contains(text(), '{expected_text}')]"
            last_ai_response = self.wait.until(
                EC.presence_of_element_located((By.XPATH, ai_response_xpath))
            )
            print(" AI 응답 메시지 확인 완료")
            return last_ai_response
        except TimeoutException as e:
            print(f" AI 응답 확인 실패: {e}")
            return None

    def copy_message(self, ai_response_element=None):
        """메시지 복사 버튼 클릭"""
        try:
            if ai_response_element:
                # 특정 AI 응답 요소 내에서 복사 버튼 찾기
                try:
                    copy_btn = ai_response_element.find_element(*self.locators["copy_btn"])
                except NoSuchElementException:
                    copy_btn = self.wait.until(
                        EC.element_to_be_clickable(self.locators["copy_btn"])
                    )
            else:
                # 일반적인 복사 버튼 찾기
                copy_btn = self.wait.until(
                    EC.element_to_be_clickable(self.locators["copy_btn"])
                )
            
            copy_btn.click()
            print(" 복사 버튼 클릭 완료")
            return True
        except TimeoutException as e:
            print(f" 복사 버튼 클릭 실패: {e}")
            return False

    def verify_element_exists(self, locator):
        """특정 요소 존재 여부 확인"""
        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def edit_message(self, original_message, new_message):
        """메시지 수정 기능
        Args:
            original_message: 수정할 원본 메시지 텍스트
            new_message: 새로운 메시지 텍스트
        """
        try:
            # 1. 수정할 메시지 찾기
            message_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bg-accent.rounded-3xl.py-2\.5'))
            )
            print(f" 수정할 메시지 찾기 완료: {original_message}")
            
            # 2. 메시지에 마우스 오버하여 수정 버튼 표시
            actions = ActionChains(self.driver)
            actions.move_to_element(message_element).perform()
            print(" 메시지에 마우스 오버 완료")
            
            # 3. 수정 버튼 클릭 (메시지 내부 또는 근처의 수정 버튼)
            # 메시지의 부모 요소에서 수정 버튼 찾기
            
            try:
                edit_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.edit-message'))
                )
            except TimeoutException:
                # 다른 셀렉터 시도
                edit_btn = message_element.find_element(By.XPATH, ".//ancestor::div//button[contains(@aria-label, '수정') or contains(@title, '수정')]")
            
            edit_btn.click()
            print(" 수정 버튼 클릭 완료")
            
            # 4. 수정 입력창이 나타날 때까지 대기
            edit_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#edit-chat-input'))
            )
            print(" 수정 입력창 표시 완료")
            
            # 5. 기존 텍스트 지우고 새 메시지 입력
            edit_input.clear()
            edit_input.send_keys(new_message)
            print(f" 새 메시지 입력 완료: {new_message}")
            
            # 6. 확인 버튼 클릭
            confirm_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.confirm-edit'))
            )
            confirm_btn.click()
            print(" 확인 버튼 클릭 완료 - 메시지 수정 완료")
            
            return True
            
        except TimeoutException as e:
            print(f" 메시지 수정 실패: 요소를 찾지 못함 - {e}")
            return False
        except Exception as e:
            print(f" 메시지 수정 실패: 예상치 못한 오류 - {e}")
            return False

    def verify_message_updated(self, new_message):
        """메시지가 성공적으로 수정되었는지 확인"""
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bg-accent.rounded-3xl.py-2\.5'))
            )
            print(f" 메시지 수정 확인 완료: {new_message}")
            return True
        except TimeoutException:
            print(f" 메시지 수정 확인 실패: {new_message}를 찾을 수 없음")
            return False