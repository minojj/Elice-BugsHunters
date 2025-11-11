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
    
    QUIZ_CREATE_MENU = (By.XPATH, "//div[text()='퀴즈 생성']")
    QUIZ_CREATE_MENU_ALT = (By.XPATH, "//div[contains(@class, 'MuiTypography-root') and contains(text(), '퀴즈 생성')]")    
    
    #PPT 생성 관련 로케이터
    PPT_CREATE_MENU = (By.XPATH, "//span[contains(text(), 'PPT 생성')]")
    PPT_SLIDE_INPUT = (By.CSS_SELECTOR, "input.MuiInputBase-input.MuiOutlinedInput-input[type='number'][min='3'][max='50']")
    PPT_SECTION_INPUT = (By.CSS_SELECTOR, "input.MuiInputBase-input.MuiOutlinedInput-input[type='number'][min='1'][max='8']")
    PPT_GENERATE_BUTTON = (By.XPATH, "//button[contains(@class, 'MuiButton') and contains(., '생성')]")
    PPT_CANCEL_BUTTON = (By.XPATH, "//button[contains(., '취소')]")

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
    
    def upload_file_and_send(self, filepath, wait_time=30):
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
        
    def click_quiz_create_menu(self):
        """퀴즈 생성 메뉴 클릭 (여러 방법 시도)"""
        print("퀴즈 생성 메뉴 찾는 중...")
        self.driver.save_screenshot("before_quiz_menu.png")
        
        #XPath로 정확히 찾기
        try:
            print("   XPath 방법 시도...")
            quiz_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(@class, 'MuiListItemButton') and .//span[contains(text(), '퀴즈')]]"))
            )
            print("   ✅ 퀴즈 생성 메뉴 발견 (XPath)")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", quiz_btn)
            time.sleep(0.3)
            quiz_btn.click()
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"   ⚠️ 방법 2 실패: {str(e)}")
                
        print("   ❌ 모든 방법 실패")
        self.driver.save_screenshot("quiz_menu_not_found.png")
        return False

    def create_quiz_and_send(self, wait_time=10):
        """
        퀴즈 생성 및 전송 프로세스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 퀴즈 생성 테스트 시작 ===")
            print(f"현재 URL: {self.driver.current_url}")
            
            # 1. 플러스 버튼 클릭
            print("\n1. 플러스 버튼 클릭")
            self.click_plus_button()
            time.sleep(2)  # 메뉴가 완전히 나타날 때까지 대기
            
            # 2. 퀴즈 생성 메뉴 클릭
            print("\n2. 퀴즈 생성 메뉴 클릭")
            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            print("✅ 퀴즈 생성 메뉴 클릭 완료")
            time.sleep(1)
            
            # 3. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 4. 퀴즈 내용 입력
            print("\n3. 퀴즈 질문 입력")
            quiz_question = "다음 중 파이썬 데이터 타입이 아닌것을 고르시오를 난이도 중 객관식 버전으로 만들어줘."
            chat_input = self.wait.until(EC.presence_of_element_located(self.CHAT_INPUT))
            chat_input.clear()
            chat_input.send_keys(quiz_question)
            print(f"✅ 입력 완료: {quiz_question[:30]}...")
            time.sleep(0.5)
            
            # 5. 엔터키로 전송
            print("\n4. 메시지 전송")
            self.send_message_with_enter()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)
        
            self.driver.save_screenshot("after_quiz_send.png")
            print("\n✅ 퀴즈 생성 및 전송 완료")
            print("=== 테스트 성공 ===\n")
            return True
            
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            self.driver.save_screenshot("timeout_error.png")
            return False
            
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            self.driver.save_screenshot("element_error.png")
            return False
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            self.driver.save_screenshot("test_error.png")
            import traceback
            traceback.print_exc()
            return False
    
    def create_quiz_and_send_empty(self, wait_time=10):
        """
        퀴즈 생성 및 전송 프로세스 - 빈칸 입력 예외케이스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 퀴즈 생성 테스트 (빈칸 입력) 시작 ===")
            print(f"현재 URL: {self.driver.current_url}")
            
            # 1. 플러스 버튼 클릭
            print("\n1. 플러스 버튼 클릭")
            self.click_plus_button()
            time.sleep(2)  # 메뉴가 완전히 나타날 때까지 대기
            
            # 2. 퀴즈 생성 메뉴 클릭
            print("\n2. 퀴즈 생성 메뉴 클릭")
            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            print("✅ 퀴즈 생성 메뉴 클릭 완료")
            time.sleep(1)
            
            # 3. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 4. 퀴즈 내용 입력 (빈칸)
            print("\n3. 퀴즈 질문 입력 (빈칸)")
            chat_input = self.wait.until(EC.presence_of_element_located(self.CHAT_INPUT))
            chat_input.clear()
            print("✅ 빈칸 입력 완료")
            time.sleep(0.5)
            
            # 5. 엔터키로 전송
            print("\n4. 메시지 전송")
            self.send_message_with_enter()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)
        
            self.driver.save_screenshot("after_quiz_send_empty.png")
            print("\n✅ 퀴즈 생성 및 전송 완료 (빈칸 입력)")
            print("=== 테스트 성공 ===\n")
            return True
            
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            self.driver.save_screenshot("timeout_error.png")
            return False
            
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            self.driver.save_screenshot("element_error.png")
            return False
    
    def create_quiz_and_send_special_chars(self, wait_time=10):
        """
        퀴즈 생성 및 전송 프로세스 - 특수문자 입력 예외케이스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 퀴즈 생성 테스트 (특수문자 입력) 시작 ===")
            print(f"현재 URL: {self.driver.current_url}")
            
            # 1. 플러스 버튼 클릭
            print("\n1. 플러스 버튼 클릭")
            self.click_plus_button()
            time.sleep(2)  # 메뉴가 완전히 나타날 때까지 대기
            
            # 2. 퀴즈 생성 메뉴 클릭
            print("\n2. 퀴즈 생성 메뉴 클릭")
            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            print("✅ 퀴즈 생성 메뉴 클릭 완료")
            time.sleep(1)
            
            # 3. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 4. 퀴즈 내용 입력 (특수문자)
            print("\n3. 퀴즈 질문 입력 (특수문자)")
            special_chars = "!@#$%^&*()_+{}|:\"<>?-=[]\\;',./`~"
            chat_input = self.wait.until(EC.presence_of_element_located(self.CHAT_INPUT))
            chat_input.clear()
            chat_input.send_keys(special_chars)
            print(f"✅ 특수문자 입력 완료: {special_chars}")
            time.sleep(0.5)
            
            # 5. 엔터키로 전송
            print("\n4. 메시지 전송")
            self.send_message_with_enter()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)
        
            self.driver.save_screenshot("after_quiz_send_special_chars.png")
            print("\n✅ 퀴즈 생성 및 전송 완료 (특수문자 입력)")
            print("=== 테스트 성공 ===\n")
            return True
            
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            self.driver.save_screenshot("timeout_error.png")
            return False
            
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            self.driver.save_screenshot("element_error.png")
            return False
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            self.driver.save_screenshot("test_error.png")
            import traceback
            traceback.print_exc()
            return False
        

  
    
      