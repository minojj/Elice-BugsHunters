import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from src.utils.helpers import Utils
from tests.conftest import driver


class ChatExpancePage:
    """AI Helpy Chat 페이지 객체"""
    
    # 로케이터 정의
    locators = {
        "email_input": (By.CSS_SELECTOR, "input[name='loginId']"),
        "password_input": (By.CSS_SELECTOR, "input[name='password']"),
        "login_button": (By.CSS_SELECTOR, "button[type='submit']"),
        
        "plus_button": (By.CSS_SELECTOR, "button[aria-haspopup='true']"),
        "file_upload_menu_css": (By.CSS_SELECTOR, "div.MuiButtonBase-root.MuiListItemButton-root[role='presentation'][data-action='file-upload']"),
        "file_input": (By.CSS_SELECTOR, "input[type='file']"),
        "file_submit_button": (By.ID, "file-submit"),

        "backdrop": (By.CSS_SELECTOR, ".MuiBackdrop-root"),
        "chat_input": (By.CSS_SELECTOR, "div.MuiInputBase-root.MuiInputBase-multiline textarea"),
    
        "quiz_create_menu": (By.XPATH, "//div[text()='퀴즈 생성']"),

        # #PPT 생성 관련 로케이터
        "ppt_create_btn": (By.XPATH, "//span[contains(text(), 'PPT 생성')]"),
        "ppt_slide_input": (By.XPATH, "//div[text()='슬라이드 수']/following-sibling::div//input"),
        "ppt_section_input": (By.XPATH, "//li[role='button' and .//svg[@data-icon='magnifying-glass']]"),
        "ppt_generate_button": (By.XPATH, "//button[contains(@class, 'MuiButton') and contains(., '생성')]"),
        "ppt_cancel_button": (By.XPATH, "//button[contains(., '취소')]"),

        "image_create_menu": (By.XPATH, "//span[text()='이미지 생성']"),
        
        "google_search_menu_xpath": (By.XPATH, "//span[text()='구글 검색']"),
        "deep_dive_menu_xpath": (By.XPATH, "//span[containstext()='심층 조사']"),
        "deep_dive_create_button": (By.XPATH, "//button[contains(., '심층 조사 생성하기')]"),
    }
    
    error_selectors = [
        # 실제 HTML 구조
        (By.CSS_SELECTOR, "div[data-title]"),
        (By.XPATH, "//div[@data-title]"),
        (By.XPATH, "//*[@data-type='error']"),
        ]
    
    error_keywords = [
        'File type must be one of',
        'image/*', 
        'application/pdf',
    ]

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

    def click_plus_button(self):
        """플러스 버튼 클릭"""
        plus_btn = self.wait.until(EC.element_to_be_clickable(self.locators["plus_button"]))
        plus_btn.click()
        print("✅ 플러스 버튼 클릭 완료")
    
    def click_file_upload_menu(self):
        """파일 업로드 메뉴 클릭"""
        
        file_upload_btn = self.wait.until(
            EC.element_to_be_clickable(self.locators["file_upload_menu_css"])
            )
        
        print("✅ 파일 업로드 메뉴 발견 ")
        
        
        file_upload_btn.click()
        print("✅ 파일 업로드 메뉴 클릭 완료")

    def upload_file(self, upload_file: str):
        """
         파일 업로드
        Args:
            filepath: 업로드할 파일의 전체 경로 
        """
        file_path = str(upload_file)
        print(f"🔍 받은 파일 경로: {file_path}")   

         
        file_input = self.wait.until(
            EC.presence_of_element_located(self.locators["file_input"])
    )
        #파일 경로 전송
        file_input.send_keys(file_path)

        print(f"✅ 파일 업로드 완료: {file_path}")  

    def close_file_dialog(self):
        """파일 다이얼로그 닫기 (ESC)""" 
        #액션체인지
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ESCAPE)
        actions.send_keys(Keys.ESCAPE)
        actions.perform()
        print("✅ 파일 탐색창 닫기 (ESC) - ActionChains")

    def get_uploaded_filename(self):
        """업로드된 파일명 반환"""
        try:
            uploaded_file_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "uploaded-files"))
            )
            filename = uploaded_file_element.text
            print(f"✅ 업로드된 파일명 확인: {filename}")
            return filename
        except TimeoutException:
            print("⚠️ 업로드된 파일명을 찾을 수 없음")
            return None
        
    def click_file_submit_button(self):
        """파일 제출 버튼 클릭"""
        try:
            submit_button = self.wait.until(
                EC.element_to_be_clickable(self.locators["file_submit_button"])
        )
            submit_button.click()
            print("✅ 파일 제출 버튼 클릭 완료")         
        except TimeoutException:
            print("⚠️ 파일 제출 버튼이 나타나지 않음 — 무시하고 진행")  
    
    def wait_for_backdrop_disappear(self):
        """백드롭(오버레이)이 사라질 때까지 대기"""
        try:
            WebDriverWait(self.driver, 10).until_not(
                EC.presence_of_element_located(self.locators["backdrop"])
            )
            print("✅ 백드롭(overlay) 사라짐 확인 완료")
        except TimeoutException:
            print("⚠️ 백드롭 대기 중 오류 — 무시하고 진행")

    def send_message_with_enter(self):
        """엔터키로 메시지 전송 (입력창이 비어있어도 가능)"""
        chat_input = self.wait.until(EC.presence_of_element_located(self.locators["chat_input"]))
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
        chat_input = self.wait.until(EC.presence_of_element_located(self.locators["chat_input"]))
        chat_input.click()
        chat_input.send_keys(message)
        time.sleep(0.5)
        chat_input.send_keys(Keys.RETURN)
        print(f"✅ 메시지 전송 완료: {message}")
    
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
            self.upload_file(filepath)

            #  파일 다이얼로그 닫기
            self.close_file_dialog()
            
            # 4. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 5. 엔터키로 전송
            self.send_message_with_enter()
            
            # 6. 응답 대기
            self.wait_for_response(wait_time)
            print("=== 테스트 성공 ===")
            return True
            
        except TimeoutException as e:
            print(f"❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.get_current_url()}")
            return False
            
        except NoSuchElementException as e:
            print(f"❌ 요소를 찾을 수 없음: {str(e)}")
            return False
            
        except Exception as e:
            print(f"❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
    def check_for_alert_or_error(self,timeout=5):
        """경고창(alert) 또는 에러 메시지 확인"""
        try:
            WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return alert_text
           
        except:
            pass

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                page_source = self.driver.page_source
                for keyword in self.error_keywords:
                    if keyword in page_source:
                        return True
                           
            except :
                pass
               
    def upload_file_expect_failure(self, filepath, wait_time=10):
        """
         파일 업로드 (실패 예상)
        Args:
            filepath: 업로드할 파일의 전체 경로 
        Returns:
            bool: 업로드 실패 여부 (True: 실패 확인, False: 업로드 성공)
        """
        try:
            print("\n=== 위험 파일 업로드 테스트 시작 ===")
            
            # 1. 플러스 버튼 클릭
            self.click_plus_button()
            
            # 2. 파일 업로드 메뉴 클릭
            self.click_file_upload_menu()
            
            # 3. 파일 업로드
            self.upload_file(filepath)

            # 4. 경고창 또는 에러 메시지 확인
            has_error = self.check_for_alert_or_error(timeout=wait_time)

            #  파일 다이얼로그 닫기
            self.close_file_dialog()
            
            # 5. 응답 대기
            self.wait_for_response(wait_time)
            
            if has_error:
                print("✅ 위험 파일 업로드가 차단되었습니다 (예상된 동작)")
                return True  # 업로드 실패 확인
            
            else:
                print("❌ 위험 파일 업로드가 허용되었습니다 (예상과 다른 동작)")
                return False  # 업로드 성공
            
        except TimeoutException as e:
            print(f"❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.get_current_url()}")
            return False
            
        except NoSuchElementException as e:
            print(f"❌ 요소를 찾을 수 없음: {str(e)}")
            return False
            
        except Exception as e:
            print(f"❌ 테스트 실패: {type(e).__name__} - {str(e)}")
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
                EC.element_to_be_clickable((self.locators["quiz_create_menu_alt2"]))
            )
            print("   ✅ 퀴즈 생성 메뉴 발견 (XPath)")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", quiz_btn)
            time.sleep(0.3)
            quiz_btn.click()
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"   ⚠️ 실패: {str(e)}")
                
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
            chat_input = self.wait.until(EC.presence_of_element_located(self.locators["chat_input"]))
            chat_input.clear()
            chat_input.send_keys(quiz_question)
            print(f"✅ 입력 완료: {quiz_question[:30]}...")
            time.sleep(0.5)
            
            # 5. 엔터키로 전송
            print("\n4. 메시지 전송")
            self.send_message_with_enter()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
           

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
            chat_input = self.wait.until(EC.presence_of_element_located(self.locators["chat_input"]))
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
    
    def create_quiz_and_send_no_type(self, wait_time=10):
        """
        퀴즈 생성 및 전송 프로세스 - 유형 미선택 예외케이스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 퀴즈 생성 테스트 (유형 미선택) 시작 ===")
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
            quiz_question = "다음 중 파이썬 데이터 타입이 아닌것을 고르시오."
            chat_input = self.wait.until(EC.presence_of_element_located(self.locators["chat_input"]))
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
        
            self.driver.save_screenshot("after_quiz_send_no_type.png")
            print("\n✅ 퀴즈 생성 및 전송 완료 (유형 미선택)")
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

    def click_ppt_create_menu(self):
        
        """PPT 생성 메뉴 클릭"""
        try:
            ppt_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.locators["ppt_create_btn"])
            )
            print("✅ PPT 생성 메뉴 발견")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", ppt_btn)
            time.sleep(0.3)

            ppt_btn.click()
            print("✅ PPT 생성 메뉴 클릭 완료")

        except Exception as e:
            raise Exception("PPT 생성 메뉴를 클릭할 수 없습니다.") from e
        
    def input_ppt_topic(self, topic):
        """PPT 주제 입력"""
        chat_input = self.wait.until(EC.element_to_be_clickable(self.locators["chat_input"]))
        chat_input.clear()
        chat_input.send_keys(topic)
        print(f"✅ 입력 완료: {topic}")
        time.sleep(0.5)

    def clkick_slide_input(self):
        """슬라이드 수 입력창 클릭"""
        
        slide_input = self.wait.until(EC.element_to_be_clickable(self.locators["ppt_slide_input"]))
        slide_input.click()
        print("✅ 슬라이드 수 입력창 클릭 완료")

    def click_section_input(self):
        """섹션 수 입력창 클릭"""
        section_input = self.wait.until(EC.element_to_be_clickable(self.locators["ppt_section_input"]))
        section_input.click()
        print("✅ 섹션 수 입력창 클릭 완료")

    def input_slide_and_section_count(self, slide_count, section_count):
        """슬라이드 수 및 섹션 수 입력"""
        slide_input = self.wait.until(EC.element_to_be_clickable(self.locators["ppt_slide_input"]))
        self.driver.execute_script("arguments[0].focus();", slide_input)
        
        
        slide_input.send_keys(Keys.CONTROL + "a")
        slide_input.send_keys(Keys.BACKSPACE)
        slide_input.clear()
        time.sleep(0.1)

        slide_input.send_keys(str(slide_count))

        section_input = self.wait.until(EC.element_to_be_clickable(self.locators["ppt_section_input"]))
        self.driver.execute_script("arguments[0].focus();", section_input)
        time.sleep(0.2)
      
        section_input.send_keys(Keys.CONTROL + "a")
        section_input.send_keys(Keys.BACKSPACE)
        section_input.clear()
        time.sleep(0.1)

        section_input.send_keys(str(section_count))
        print("✅ 슬라이드 수 및 섹션 수 입력 완료")
        time.sleep(0.5) #디버깅 목적 실제테스트 시 제거

    def click_generate_button(self):
        """생성하기 버튼 클릭"""
        generate_button = self.wait.until(
            EC.element_to_be_clickable(self.locators["ppt_generate_button"])
        )
        generate_button.click()
        print("✅ 생성하기 버튼 클릭 완료")

    def create_ppt_and_send(self, wait_time=60):
        """
        PPT 생성 및 전송 프로세스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== PPT 생성 테스트 시작 ===")
            print(f"현재 URL: {self.driver.current_url}")
            
            # 1. 플러스 버튼 클릭
            print("\n1. 플러스 버튼 클릭")
            self.click_plus_button()
            time.sleep(2)  # 메뉴가 완전히 나타날 때까지 대기
            
            # 2. PPT 생성 메뉴 클릭
            print("\n2. PPT 생성 메뉴 클릭")
            self.click_ppt_create_menu()

            # 3. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 4. PPT 주제 입력
            print("\n3. PPT 주제 입력")
            ppt_topic = "AI 기술의 발전과 미래 전망"
            self.input_ppt_topic(ppt_topic)

            # 5. 엔터키로 전송
            print("\n4. 메시지 전송")
            self.send_message_with_enter()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)

            # 7.슬라이드수, 섹션 수 입력
            print("\n6. 슬라이드 수 및 섹션 수 입력")
            self.clkick_slide_input()
            self.click_section_input()  
            self.input_slide_and_section_count(10, 5)

        
            # 8. 생성하기 버튼 클릭
            print("\n7. 생성하기 버튼 클릭")
            self.click_generate_button()

            # 9. 응답 대기
            print(f"\n8. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)
            self.driver.save_screenshot("after_ppt_send.png")
            print("\n✅ PPT 생성 및 전송 완료")
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
        
    def click_image_create_menu(self):
        """이미지 생성 메뉴 클릭"""
        try:
            image_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.locators["image_create_menu"])
        )
            image_btn.click()
            print("✅ 이미지 생성 메뉴 클릭 완료")
            time.sleep(0.5)
        except Exception as e:
            raise Exception("이미지 생성 메뉴를 클릭할 수 없습니다.") from e

    def input_image_topic(self, topic):
        """이미지 주제 입력"""
        chat_input = self.wait.until(EC.element_to_be_clickable(self.locators["chat_input"]))
        chat_input.clear()
        chat_input.send_keys(topic)
        print(f"✅ 입력 완료: {topic}")
        time.sleep(0.5) 

    def create_image_and_send(self, wait_time=30):
        """
        이미지 생성 및 전송 프로세스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 이미지 생성 테스트 시작 ===")
            print(f"현재 URL: {self.driver.current_url}")
            
            # 1. 플러스 버튼 클릭
            print("\n1. 플러스 버튼 클릭")
            self.click_plus_button()
            time.sleep(2)  # 메뉴가 완전히 나타날 때까지 대기
            
            # 2. 이미지 생성 메뉴 클릭
            print("\n2. 이미지 생성 메뉴 클릭")
            self.click_image_create_menu()

            # 3. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 4. 이미지 주제 입력
            print("\n3. 이미지 주제 입력")
            image_topic = "A futuristic cityscape with flying cars"
            self.input_image_topic(image_topic)
            print(f"✅ 입력 완료: {image_topic}")
            time.sleep(0.5)
    
            # 5. 엔터키로 전송
            print("\n4. 메시지 전송")
            self.send_message_with_enter()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)
    
            self.driver.save_screenshot("after_image_send.png")
            print("\n✅ 이미지 생성 및 전송 완료")
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
            self.send_message_with_enter()
    
    def click_google_search_menu(self):
        """구글 검색 메뉴 클릭"""
        try:
            google_search_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.locators["google_search_menu_xpath"])
            )
            print("✅ 구글 검색 메뉴 발견")
                       
            google_search_btn.click()
            print("✅ 구글 검색 메뉴 클릭 완료")
            time.sleep(0.5)
        except Exception as e:
            raise Exception("구글 검색 메뉴를 클릭할 수 없습니다.") from e
    
    def input_google_search_query(self, query):
        """구글 검색어 입력"""
        chat_input = self.wait.until(EC.element_to_be_clickable(self.locators["chat_input"]))
        chat_input.clear()
        chat_input.send_keys(query)
        print(f"✅ 입력 완료: {query}")
        time.sleep(0.5)

    def google_search_and_send(self, wait_time=30):
        """
        구글 검색 및 전송 프로세스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 구글 검색 테스트 시작 ===")
            print(f"현재 URL: {self.driver.current_url}")
            
            # 1. 플러스 버튼 클릭
            print("\n1. 플러스 버튼 클릭")
            self.click_plus_button()
            time.sleep(2)  # 메뉴가 완전히 나타날 때까지 대기
            
            # 2. 구글 검색 메뉴 클릭
            print("\n2. 구글 검색 메뉴 클릭")
            self.click_google_search_menu()

            print("✅ 구글 검색 메뉴 클릭 완료")
            time.sleep(0.5)

            # 3. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 4. 검색어 입력
            print("\n3. 검색어 입력")
            search_query = "KPop Demon Hunters"
            self.input_google_search_query(search_query)

            # 5. 엔터키로 전송
            print("\n4. 메시지 전송")
            self.send_message_with_enter()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)
    
            self.driver.save_screenshot("after_google_search_send.png")
            print("\n✅ 구글 검색 및 전송 완료")
            print("=== 테스트 성공 ===\n")
            return True
    
        except TimeoutException as e:
            print(f"\n ❌ 타임아웃 오류: {str(e)}")
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
        
    def click_deep_dive_menu(self):

        """심층 조사 메뉴 클릭"""
        try:
            deep_dive_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.locators["deep_dive_menu_css"])
            )
            print("✅ 심층 조사 메뉴 발견")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", deep_dive_btn)
            time.sleep(0.3)
            deep_dive_btn.click()
            print("✅ 심층 조사 메뉴 클릭 완료")
            time.sleep(0.5)
        except Exception as e:
            raise Exception("심층 조사 메뉴를 클릭할 수 없습니다.") from e
        
    def input_deep_dive_topic(self, topic):
        """심층 조사 주제 입력"""
        chat_input = self.wait.until(EC.element_to_be_clickable(self.locators["chat_input"]))
        chat_input.clear()
        chat_input.send_keys(topic)
        print(f"✅ 입력 완료: {topic}")
        time.sleep(0.5)   

    def click_create_deep_dive_button(self):
        """심층 조사 생성하기 버튼 클릭"""
        create_button = self.wait.until(
            EC.element_to_be_clickable(self.locators["deep_dive_create_button"])
        )
        create_button.click()
        print("✅ 심층 조사 생성하기 버튼 클릭 완료")

    def deep_dive_and_send(self, wait_time=30):
        """
        심층 조사 및 전송 프로세스 (통합 메서드)
        
        Args:
            wait_time: AI 응답 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            print("\n=== 심층 조사 테스트 시작 ===")
            print(f"현재 URL: {self.driver.current_url}")
            
            # 1. 플러스 버튼 클릭
            print("\n1. 플러스 버튼 클릭")
            self.click_plus_button()
            time.sleep(2)  # 메뉴가 완전히 나타날 때까지 대기
            
            # 2. 심층 조사 메뉴 클릭
            print("\n2. 심층 조사 메뉴 클릭")
            self.click_deep_dive_menu()
            time.sleep(0.5)
            print("✅ 심층 조사 메뉴 클릭 완료")
            

            # 3. 백드롭 사라질 때까지 대기
            self.wait_for_backdrop_disappear()
            
            # 4. 심층 조사 주제 입력
            print("\n3. 심층 조사 주제 입력")
            deep_dive_topic = "인공지능의 윤리적 문제"
            self.input_deep_dive_topic(deep_dive_topic)
            print(f"✅ 입력 완료: {deep_dive_topic}")

            print("\n4. 메시지 전송")
            self.send_message_with_enter()

            # 5. 심층 조사 생성하기 버튼 클릭
            print("\n5. 심층 조사 생성하기 버튼 클릭")
            self.click_create_deep_dive_button()
            
            # 6. 응답 대기
            print(f"\n5. AI 응답 대기 ({wait_time}초)")
            time.sleep(wait_time)
    
            self.driver.save_screenshot("after_deep_dive_send.png")
            print("\n✅ 심층 조사 및 전송 완료")
            print("=== 테스트 성공 ===\n")
            return True
        
        except TimeoutException as e:
            print(f"\n ❌ 타임아웃 오류: {str(e)}")
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
        