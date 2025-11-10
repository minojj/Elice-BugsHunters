from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver 
from selenium.webdriver.chrome.service import Service 
from src.utils.helpers import Utils 
from tests.conftest import driver
import time
import pyautogui


class Chat_Expance:
    """AI Helpy Chat 페이지 객체"""
    
    # 로케이터 정의
    
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[name='loginId']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    PLUS_BUTTON = (By.CSS_SELECTOR, "button[aria-haspopup='true']")
    FILE_UPLOAD_MENU_CSS = (By.CSS_SELECTOR, "div.MuiButtonBase-root.MuiListItemButton-root[role='presentation'][data-action='file-upload']")
    FILE_UPLOAD_MENU_XPATH = (By.XPATH, "//div[contains(text(), 'File Upload')]")
    
    BACKDROP = (By.CSS_SELECTOR, ".MuiBackdrop-root")
    CHAT_INPUT = (By.CSS_SELECTOR, 'div.MuiInputBase-root.MuiInputBase-multiline textarea')
    
    def __init__(self, driver):
        """
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.base_url = "https://qaproject.elice.io/ai-helpy-chat"
    
    def open(self):
        """test URL로 이동"""
        self.driver.get(self.base_url)
        print(f"✅ {self.base_url} 로 이동")
    
    def login(self, username, password):
        """
        로그인 수행
        
        Args:
            username: 로그인 이메일
            password: 비밀번호
        """
        self.open()
        
        # 이메일 입력
        email_input = self.wait.until(EC.presence_of_element_located(self.EMAIL_INPUT))
        email_input.send_keys(username)
        
        # 비밀번호 입력
        password_input = self.wait.until(EC.presence_of_element_located(self.PASSWORD_INPUT))
        password_input.send_keys(password)
        
        # 로그인 버튼 클릭
        login_btn = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
        login_btn.click()
        
        print("✅ 로그인 시도 완료")
        time.sleep(1)
    
    def click_plus_button(self):
        """플러스 버튼 클릭"""
        plus_btn = self.wait.until(EC.element_to_be_clickable(self.PLUS_BUTTON))
        plus_btn.click()
        print("✅ 플러스 버튼 클릭 완료")
        time.sleep(0.5)
    
    def click_file_upload_menu(self):
        """파일 업로드 메뉴 클릭"""
        try:
            file_upload_btn = self.wait.until(
                EC.element_to_be_clickable(self.FILE_UPLOAD_MENU_CSS)
            )
            print("✅ 파일 업로드 메뉴 발견 (CSS)")
        except:
            print("⚠️ CSS 선택자 실패, XPath 시도...")
            file_upload_btn = self.wait.until(
                EC.element_to_be_clickable(self.FILE_UPLOAD_MENU_XPATH)
            )
            print("✅ 파일 업로드 메뉴 발견 (XPath)")
        
        file_upload_btn.click()
        print("✅ 파일 업로드 메뉴 클릭 완료")
    
    def upload_file_via_dialog(self, filepath):
        """
        시스템 파일 대화상자를 통한 파일 업로드
        
        Args:
            filepath: 업로드할 파일의 전체 경로
        """
        print(f"📂 파일 탐색창 대기 중...")
        self.driver.save_screenshot("before_file_input.png")
        
        print(f"🔍 파일 검색 중: {filepath}")
        time.sleep(1)
        
        # 파일 경로 입력
        pyautogui.write(filepath, interval=0.1)
        time.sleep(1)
        
        # 엔터키로 확인
        pyautogui.press('enter')
        time.sleep(2)
        
        self.driver.save_screenshot("after_file_upload.png")
        print("✅ 파일 업로드 완료")
    
    def wait_for_backdrop_disappear(self):
        """백드롭(오버레이)이 사라질 때까지 대기"""
        try:
            WebDriverWait(self.driver, 10).until_not(
                EC.presence_of_element_located(self.BACKDROP)
            )
            print("✅ 백드롭(overlay) 사라짐 확인 완료")
        except:
            print("⚠️ 백드롭 대기 중 오류 — 무시하고 진행")
    
    def send_message_with_enter(self):
        """엔터키로 메시지 전송 (입력창이 비어있어도 가능)"""
        chat_input = self.wait.until(EC.presence_of_element_located(self.CHAT_INPUT))
        print(f"✅ 입력창 발견: {chat_input.tag_name}")
        
        chat_input.click()
        time.sleep(0.5)
        chat_input.send_keys(Keys.RETURN)
        print("✅ 엔터키로 전송 완료")
    
    def send_message(self, message):
        """
        메시지 입력 후 전송
        
        Args:
            message: 전송할 메시지
        """
        chat_input = self.wait.until(EC.presence_of_element_located(self.CHAT_INPUT))
        chat_input.click()
        chat_input.send_keys(message)
        time.sleep(0.5)
        chat_input.send_keys(Keys.RETURN)
        print(f"✅ 메시지 전송 완료: {message}")
    
    def take_screenshot(self, filename):
        """
        스크린샷 저장
        
        Args:
            filename: 저장할 파일명
        """
        self.driver.save_screenshot(filename)
        print(f"📸 스크린샷 저장: {filename}")
    
    def wait_for_response(self, seconds=40):
        """
        AI 응답 대기
        
        Args:
            seconds: 대기 시간(초)
        """
        print(f"⏳ AI 응답 대기 중... ({seconds}초)")
        time.sleep(seconds)
        print("✅ 대기 완료")
    
    def get_current_url(self):
        """현재 URL 반환"""
        return self.driver.current_url
    
    def upload_file_and_send(self, filepath, wait_time=40):
        """
        파일 업로드 및 전송 프로세스 (통합 메서드)
        
        Args:
            filepath: 업로드할 파일 경로
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 파일 업로드 테스트 시작 ===")
            
            # 1. 플러스 버튼 클릭
            self.click_plus_button()
            
            # 2. 파일 업로드 메뉴 클릭
            self.click_file_upload_menu()
            
            # 3. 파일 업로드
            self.upload_file_via_dialog(filepath)
            
            # 4. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 5. 엔터키로 전송
            self.send_message_with_enter()
            
            # 6. 응답 대기
            self.wait_for_response(wait_time)
            
            self.take_screenshot("after_send.png")
            print("=== 테스트 성공 ===")
            return True
            
        except TimeoutException as e:
            print(f"❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.get_current_url()}")
            self.take_screenshot("timeout_error.png")
            return False
            
        except NoSuchElementException as e:
            print(f"❌ 요소를 찾을 수 없음: {str(e)}")
            self.take_screenshot("element_error.png")
            return False
            
        except Exception as e:
            print(f"❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            self.take_screenshot("test_error.png")
            import traceback
            traceback.print_exc()
            return False