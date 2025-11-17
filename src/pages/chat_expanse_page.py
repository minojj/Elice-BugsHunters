import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from src.utils.helpers import Utils
from tests.conftest import driver


class ChatExpansePage:
    """AI Helpy Chat 페이지 객체"""
    
    # 로케이터 정의
    locators = {
        "email_input": (By.CSS_SELECTOR, "input[name='loginId']"),
        "password_input": (By.CSS_SELECTOR, "input[name='password']"),
        "login_btn": (By.CSS_SELECTOR, "button[type='submit']"),

        "new_chat_btn": (By.XPATH, "//span[text()='새 대화']"),
        "plus_btn": (By.CSS_SELECTOR, "button[aria-haspopup='true']"),
        "file_upload_menu_css": (By.CSS_SELECTOR, "div.MuiButtonBase-root.MuiListItemButton-root[role='presentation'][data-action='file-upload']"),
        "file_input": (By.CSS_SELECTOR, "input[type='file']"),
        "file_submit_btn": (By.ID, "file-submit"),

        "backdrop": (By.CSS_SELECTOR, ".MuiBackdrop-root"),
        "chat_input": (By.CSS_SELECTOR, "div.MuiInputBase-root.MuiInputBase-multiline textarea"),
        "quiz_create_menu": (By.XPATH, "//span[text()='퀴즈 생성']"),
        # #PPT 생성 관련 로케이터
        "ppt_create_btn": (By.XPATH, "//span[contains(text(), 'PPT 생성')]"),
        "ppt_slide_count": (By.CSS_SELECTOR, "input[type='number'][min='3'][max='50']"),
        "ppt_section_count": (By.CSS_SELECTOR, "input[type='number'][min='1'][max='8']") ,
        "ppt_generate_btn": (By.XPATH, "//button[contains(@class, 'MuiButton-containedPrimary')]"),
        "ppt_cancel_btn": (By.XPATH, "//button[contains(., '취소')]"),

        "image_create_menu": (By.XPATH, "//span[text()='이미지 생성']"),
        "image_generation_indicator": (By.XPATH, "//div[text()='select_one']"),
        "google_search_menu": (By.XPATH, "//span[text()='구글 검색']"),
        "deep_dive_menu": (By.XPATH, "//span[text()='심층 조사']"),
        "deep_dive_create_btn": (By.XPATH, "//button[.//span[text()='시작']]"),
        "loading_indicator": (By.CSS_SELECTOR, "div.thinking-dots-container[role='status']"),
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
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.base_url = "https://qaproject.elice.io/ai-helpy-chat"
    
    def open(self):
        self.driver.get(self.base_url)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def click_plus_button(self):
        plus_btn = self.wait.until(EC.element_to_be_clickable(self.locators["plus_btn"]))
        plus_btn.click()
        self.wait.until(EC.visibility_of_element_located(self.locators["file_upload_menu_css"]))
    
    def click_file_upload_menu(self):
        file_upload_btn = self.wait.until(
            EC.element_to_be_clickable(self.locators["file_upload_menu_css"])
            )
        file_upload_btn.click()
        self.wait.until(EC.presence_of_element_located(self.locators["file_input"]))
    
    def upload_file(self, upload_file: str):
        file_path = str(upload_file)
        file_input = self.wait.until(
            EC.presence_of_element_located(self.locators["file_input"])
    )
        file_input.send_keys(file_path)

    def close_file_dialog(self):
        try:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ESCAPE)
            actions.send_keys(Keys.ESCAPE)
            actions.perform()

            try:
                self.wait.until_not(
                    EC.invisibility_of_element_located(self.locators["backdrop"])
                )
            except TimeoutException:
                pass

        except Exception as e:
            print(f"⚠️ 파일 탐색창 닫기 실패: {str(e)} - 무시하고 진행")    

    def get_uploaded_filename(self):
        try:
            uploaded_file_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "uploaded-files"))
            )
            self.wait.until(lambda d: uploaded_file_element.text.strip() != "")
            return uploaded_file_element.text
        
        except TimeoutException:
            print("⚠️ 업로드된 파일명을 찾을 수 없음")
            return None
        
    def click_file_submit_button(self):
        try:
            submit_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["file_submit_btn"])
        )
            submit_btn.click()

            try:
                self.wait.until_not(
                    EC.invisibility_of_element_located(self.locators["file_submit_btn"])
                )
            except TimeoutException:
                pass

        except TimeoutException:
            print("⚠️ 파일 제출 버튼이 나타나지 않음 — 무시하고 진행")  
    
    def wait_for_backdrop_disappear(self):
        try:
            self.wait.until(
                EC.invisibility_of_element_located(self.locators["backdrop"])
            )

        except TimeoutException:
            print("⚠️ 백드롭 대기 중 오류 — 무시하고 진행")

    def send_message_with_enter(self):
        chat_input = self.wait.until(
            EC.presence_of_element_located(self.locators["chat_input"])
        )
        chat_input.click()
        self.wait.until(EC.element_to_be_clickable(self.locators["chat_input"]))
        chat_input.send_keys(Keys.RETURN)
    
    def send_message(self, message):
        chat_input = self.wait.until(
            EC.element_to_be_clickable(self.locators["chat_input"])
            )
        chat_input.click()
        chat_input.send_keys(message)
        self.wait.until(lambda d: chat_input.get_attribute("value") == message)
        chat_input.send_keys(Keys.RETURN)
    
    def wait_for_response(self, timeout=60):
        loading_locator = self.locators.get("loading_indicator")
        try:
            wait = WebDriverWait(self.driver, timeout)
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(loading_locator)
                )
            except TimeoutException:
                pass
        
            wait.until(
                EC.invisibility_of_element_located(loading_locator)
            )
        except TimeoutException:
            pass
        except Exception as e:
            pass
    
    def get_current_url(self):
        return self.driver.current_url
    
    def click_new_chat_button(self):
        new_chat_btn = self.wait.until(
            EC.element_to_be_clickable(self.locators["new_chat_btn"])
        )
        new_chat_btn.click()
        self.wait.until(EC.presence_of_element_located(self.locators["chat_input"]))
    
    def upload_file_and_send(self, filepath):
        try:
            self.click_plus_button()
            self.click_file_upload_menu()
            self.upload_file(filepath)
            self.close_file_dialog()
            self.wait_for_backdrop_disappear()
            self.send_message_with_enter()
            self.wait_for_response()
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
        
    def upload_file_and_send_new_chat( self, filepath):
        try:
            self.click_new_chat_button()
            self.click_plus_button()
            self.click_file_upload_menu()
            self.upload_file(filepath)
            self.close_file_dialog()
            self.wait_for_backdrop_disappear()
            self.send_message_with_enter()
            self.wait_for_response()
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
        try:
            self.click_plus_button()
            self.click_file_upload_menu()
            self.upload_file(filepath)

            has_error = self.check_for_alert_or_error(timeout=wait_time)
            self.close_file_dialog()
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
        try:
            quiz_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["quiz_create_menu"])
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", quiz_btn)
            self.wait.until(EC.element_to_be_clickable(self.locators["quiz_create_menu"]))
            quiz_btn.click()
            return True
        except Exception as e:
            print(f"   ⚠️ 실패: {str(e)}")
            return False
       
    def create_quiz_and_send(self, wait_time=10):
        try:
            self.click_plus_button()
            
            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            self.wait_for_backdrop_disappear()
            
            quiz_question = "다음 중 파이썬 데이터 타입이 아닌것을 고르시오를 난이도 중 객관식 버전으로 만들어줘."
            chat_input = self.wait.until(
                EC.element_to_be_clickable(self.locators["chat_input"])
            )
            chat_input.clear()
            self.wait.until(lambda d: chat_input.get_attribute("value") == "")
            chat_input.send_keys(quiz_question)
            
            self.send_message_with_enter()
            return True
            
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            return False
            
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False
    
    def create_quiz_and_send_empty(self):
        try:
            self.click_plus_button()

            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            self.wait_for_backdrop_disappear()
            
            chat_input = self.wait.until(
                EC.element_to_be_clickable(self.locators["chat_input"])
            )         
            chat_input.clear()
            self.wait.until(lambda d: chat_input.get_attribute("value") == "")

            self.send_message_with_enter()

            self.wait_for_response()            
            return True
            
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            return False
            
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
             
    def create_quiz_and_send_empty_new_chat(self):
        try:
            self.click_new_chat_button()
            self.click_plus_button()
            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            self.wait_for_backdrop_disappear()
            
            chat_input = self.wait.until(
            EC.element_to_be_clickable(self.locators["chat_input"])
        )
            chat_input.clear()
                          
            self.send_message_with_enter()
            self.wait_for_response()
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
    
    def create_quiz_and_send_special_chars(self):
        try:
            self.click_plus_button()
            
            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            self.wait_for_backdrop_disappear()
            
            special_chars = "!@#$%^&*()_+{}|:\"<>?-=[]\\;',./`~"
            chat_input = self.wait.until(
                EC.element_to_be_clickable(self.locators["chat_input"])
            )
            chat_input.clear()
            self.wait.until(lambda d: chat_input.get_attribute("value") == "")
            chat_input.send_keys(special_chars)
            
            self.send_message_with_enter()
            self.wait_for_response()
            return True
            
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            return False
            
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False
    
    def create_quiz_and_send_no_type(self):
        try:
            self.click_plus_button()

            if not self.click_quiz_create_menu():
                raise Exception("퀴즈 생성 메뉴를 클릭할 수 없습니다.")
            
            self.wait_for_backdrop_disappear()
            
            quiz_question = "다음 중 파이썬 데이터 타입이 아닌것을 고르시오."
            chat_input = self.wait.until(
                EC.element_to_be_clickable(self.locators["chat_input"])
            )
            chat_input.clear()
            self.wait.until(lambda d: chat_input.get_attribute("value") == "")
            chat_input.send_keys(quiz_question)
            
            self.send_message_with_enter()
            
            self.wait_for_response()
            return True
            
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            return False    
            
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False

    def click_ppt_create_menu(self):
        try:
            ppt_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["ppt_create_btn"])
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", ppt_btn)
            self.wait.until(EC.element_to_be_clickable(self.locators["ppt_create_btn"]))
            ppt_btn.click()
        except Exception as e:
            raise Exception("PPT 생성 메뉴를 클릭할 수 없습니다.") from e
        
    def input_ppt_topic(self, topic):
        chat_input = self.wait.until(
            EC.element_to_be_clickable(self.locators["chat_input"])
        )
        chat_input.clear()
        self.wait.until(lambda d: chat_input.get_attribute("value") == "")
        chat_input.send_keys(topic)

    def click_slide_input(self):
        slide_locator = self.locators["ppt_slide_count"]
        slide_input = self.wait.until(EC.element_to_be_clickable(slide_locator))
        slide_input.click()
 
    def click_section_input(self):
        section_locator = self.locators["ppt_section_count"]
        section_input = self.wait.until(EC.element_to_be_clickable(section_locator))
        section_input.click()

    def input_slide_count(self, slide_count):
        try:
            slide_locator = self.locators["ppt_slide_count"]

            def clear_and_input():
                slide_input = self.wait.until(EC.element_to_be_clickable(slide_locator))
                slide_input.send_keys(Keys.CONTROL + "a")
                slide_input.send_keys(Keys.BACKSPACE)

                for _ in range(3):
                    slide_input.send_keys(Keys.BACKSPACE)

                slide_input = self.wait.until(EC.element_to_be_clickable(slide_locator))
                slide_input.send_keys(str(slide_count))
                return slide_input
        
            for attempt in range(3):
                try:
                    slide_input = clear_and_input()
                    self.wait.until(lambda d: d.find_element(*slide_locator).get_attribute("value") == str(slide_count))
                    return True
                except StaleElementReferenceException:
                    if attempt == 2:
                        raise
                    continue
        except Exception as e:
            print(f"❌ 슬라이드 수 입력 중 오류: {str(e)}")
            return False
        
    def input_section_count(self, section_count):
        try:
            section_locator = self.locators["ppt_section_count"]

            def clear_and_input():
                section_input = self.wait.until(EC.element_to_be_clickable(section_locator))
                section_input.send_keys(Keys.CONTROL + "a")
                section_input.send_keys(Keys.BACKSPACE)

                for _ in range(3):
                    section_input.send_keys(Keys.BACKSPACE)

                section_input = self.wait.until(EC.element_to_be_clickable(section_locator))
                section_input.send_keys(str(section_count))
                return section_input
            
            for attempt in range(3):
                try:
                    section_input = clear_and_input()
                    self.wait.until(lambda d: d.find_element(*section_locator).get_attribute("value") == str(section_count))
                    return True
                except StaleElementReferenceException:
                    if attempt == 2:
                        raise
                    continue
        except Exception as e:
            print(f"❌ 섹션 수 입력 중 오류: {str(e)}")
            return False
        
    def input_slide_and_section_count(self, slide_count, section_count):
        try:
            self.click_slide_input()
            self.input_slide_count(slide_count)
            self.click_section_input()
            self.input_section_count(section_count)
            return True
        except Exception as e:
            print(f"❌ 슬라이드 및 섹션 수 입력 중 오류: {str(e)}")
            return False

    def click_generate_button(self):
        generate_btn = self.wait.until(
            EC.element_to_be_clickable(self.locators["ppt_generate_btn"])
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            generate_btn
        )
        try:
            generate_btn.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", generate_btn)

    def create_ppt_and_send(self,wait_time=60,max_retries=3):
        try:
            self.click_plus_button()
            self.click_ppt_create_menu()
            self.wait_for_backdrop_disappear()
            
            ppt_topic = "AI 기술의 발전과 미래 전망"
            self.input_ppt_topic(ppt_topic)
            self.send_message_with_enter()
            
            wait_long = WebDriverWait(self.driver, wait_time)
            slide_input = self.wait.until(
                EC.element_to_be_clickable(self.locators["ppt_slide_count"]))
            section_input = self.wait.until(
                EC.element_to_be_clickable(self.locators["ppt_section_count"]))
            
            input_success = False
            for attempt in range(max_retries):
            
                input_result = self.input_slide_and_section_count(10, 5)
            
                if input_result:
                    input_success = True
                    break  # 성공했으므로 루프 종료
                else:
                    print(f"⚠️ 슬라이드 및 섹션 수 입력 실패, 재시도 {attempt + 1}/{max_retries}...")

            if not input_success:
                return False
            
            self.click_generate_button()
            return True
        
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            return False
        
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
        
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False
        
    def click_image_create_menu(self):
        try:
            image_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.locators["image_create_menu"])
        )
            image_btn.click()
        except Exception as e:
            raise Exception("이미지 생성 메뉴를 클릭할 수 없습니다.") from e

    def input_image_topic(self, topic):
        chat_input = self.wait.until(
            EC.element_to_be_clickable(self.locators["chat_input"])
        )
        chat_input.clear()
        self.wait.until(lambda d: chat_input.get_attribute("value") == "")
        chat_input.send_keys(topic)

    def create_image_and_send(self):
        try:
            self.click_plus_button()
            self.click_image_create_menu()
            self.wait_for_backdrop_disappear()
            
            image_topic = "A futuristic cityscape with flying cars"
            self.input_image_topic(image_topic)
            self.send_message_with_enter()
            self.wait_for_response()
            return True
    
        except TimeoutException as e:
            print(f"\n❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")
            return False
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False
        
    def create_image_and_send_file(self, filepath):
        try:
            self.click_plus_button()
            self.click_image_create_menu()
            self.wait_for_backdrop_disappear()
            
            self.upload_file(filepath)
            self.send_message_with_enter()
            self.wait_for_response()
            
            try:
                long_wait = WebDriverWait(self.driver, 60)
                long_wait.until(
                    EC.presence_of_element_located(self.locators["image_generation_indicator"])
                )
                time.sleep(10)
            except TimeoutException:                
                self.wait_for_response()
            return True
    
        except NoSuchElementException as e:
            print(f"❌ 요소를 찾을 수 없음: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False
    
    def click_google_search_menu(self):
        try:
            google_search_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["google_search_menu"])
            )
            google_search_btn.click()
        except Exception as e:
            raise Exception("구글 검색 메뉴를 클릭할 수 없습니다.") from e
    
    def input_google_search_query(self, query):
        chat_input = self.wait.until(
            EC.element_to_be_clickable(self.locators["chat_input"])
        )
        chat_input.clear()
        self.wait.until(lambda d: chat_input.get_attribute("value") == "")
        chat_input.send_keys(query)

    def google_search_and_send(self):
        try:
            self.click_plus_button()
            self.click_google_search_menu()
            self.wait_for_backdrop_disappear()
            
            search_query = "KPop Demon Hunters"
            self.input_google_search_query(search_query)
            self.send_message_with_enter()
            
            self.wait_for_response()
            return True
    
        except TimeoutException as e:
            print(f"\n ❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")    
            return False
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False
        
    def click_deep_dive_menu(self):
        try:
            deep_dive_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["deep_dive_menu"])
            )
            deep_dive_btn.click()
        except Exception as e:
            raise Exception("심층 조사 메뉴를 클릭할 수 없습니다.") from e
        
    def input_deep_dive_topic(self, topic):
        chat_input = self.wait.until(
            EC.element_to_be_clickable(self.locators["chat_input"])
        )
        chat_input.clear()
        self.wait.until(lambda d: chat_input.get_attribute("value") == "")
        chat_input.send_keys(topic)

    def click_create_deep_dive_button(self):
        create_btn = self.wait.until(
            EC.element_to_be_clickable(self.locators["deep_dive_create_btn"])
        )
        create_btn.click()

    def deep_dive_and_send(self, wait_time=30):
        try:
            self.click_plus_button()
            self.click_deep_dive_menu()
            self.wait_for_backdrop_disappear()
            
            deep_dive_topic = "인공지능의 윤리적 문제"
            self.input_deep_dive_topic(deep_dive_topic)
            self.send_message_with_enter()

            self.wait_for_response()

            long_wait = WebDriverWait(self.driver, 60)
            try:
                long_wait.until(
                 EC.element_to_be_clickable(self.locators["deep_dive_create_btn"])
                )
                self.click_create_deep_dive_button()
            except TimeoutException:
                return True
            
            return True
                
        except TimeoutException as e:
            print(f"\n ❌ 타임아웃 오류: {str(e)}")
            print(f"   현재 URL: {self.driver.current_url}")    
            return False
        except NoSuchElementException as e:
            print(f"\n❌ 요소를 찾을 수 없음: {str(e)}")
            return False
        except Exception as e:
            print(f"\n❌ 테스트 실패: {type(e).__name__} - {str(e)}")
            return False
        
