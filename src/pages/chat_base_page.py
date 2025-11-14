import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class ChatPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    locators = {
        "chat_submit": (By.ID, "chat-submit"),
        "search_box": (By.CSS_SELECTOR, "div.MuiInputBase-root.MuiInputBase-multiline textarea"),
        "search_box2": (By.CSS_SELECTOR, 'textarea[placeholder="Enter your message..."]'),
        "copy_btn": (By.CSS_SELECTOR, 'button[data-state="closed"]'),
        "file_input": (By.CSS_SELECTOR, 'input[type="file"]'),
        "message_bubble": (By.CSS_SELECTOR, r'div.bg-accent.rounded-3xl.py-2\.5'),
        "edit_btn": (By.CSS_SELECTOR, 'button.edit-message'),
        "edit_input": (By.CSS_SELECTOR, '#edit-chat-input'),
        "edit_confirm_btn": (By.CSS_SELECTOR, 'button.confirm-edit'),
        "image": (By.CSS_SELECTOR, 'img.inline-image'),
        "first_article": (By.XPATH, '(//div[@role="article"])[1]'),
        "scroll_latest_btn": (By.CSS_SELECTOR, 'button.h-9.w-9.rounded-full'),
        "ai_response": "//div[@role='article'][contains(text(), '{text}')]",
    }

    # === Page Actions ===

    def send_message(self, message):
        """메시지 입력 및 전송"""
        try:
            # 검색창에 메시지 입력
            search_box = self.wait.until(
                EC.element_to_be_clickable(self.locators["search_box"])
            )
            search_box.send_keys(message)
            
            # 전송 버튼 클릭
            search_btn = self.wait.until(
                EC.element_to_be_clickable(self.locators["chat_submit"])
            )
            search_btn.click()
            return True
        except TimeoutException as e:
            return False

    def get_ai_response(self, expected_text):
        """AI 응답 메시지 확인"""
        try:
            ai_response_xpath = self.locators["ai_response"].format(text=expected_text)
            last_ai_response = self.wait.until(
                EC.presence_of_element_located((By.XPATH, ai_response_xpath))
            )
            return last_ai_response
        except Exception as e:
            return False

    def check_image_exists(self):
        """AI 응답에 이미지가 있는지 확인"""
        try:
            image_element = self.wait.until(
                EC.presence_of_element_located(self.locators["image"])
            )
            return image_element
        except TimeoutException:
            return None

    def upload_file(self, file_path):
        """파일 업로드"""
        try:
            # 파일 존재 확인
            if not os.path.exists(file_path):
                return False
            
            # 파일 입력 요소 대기
            file_input = self.wait.until(
                EC.presence_of_element_located(self.locators["file_input"])
            )
            
            # 절대 경로로 변환
            abs_path = os.path.abspath(file_path)
            file_input.send_keys(abs_path)
            
            return True
        except TimeoutException:
            return False
        except NoSuchElementException:
            return False
        except Exception as e:
            return False

    def copy_message(self, ai_response_element=None):
        """메시지 복사 버튼 클릭"""
        try:
            if ai_response_element:
                # 특정 AI 응답 요소 내에서 복사 버튼 찾기
                # StaleElementReferenceException 대응: 재시도 로직
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        copy_btn = ai_response_element.find_element(*self.locators["copy_btn"])
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(0.5)
                            continue
                        # 마지막 시도 실패 시 일반 복사 버튼 찾기
                        copy_btn = self.wait.until(
                            EC.element_to_be_clickable(self.locators["copy_btn"])
                        )
            else:
                # 일반적인 복사 버튼 찾기
                copy_btn = self.wait.until(
                    EC.element_to_be_clickable(self.locators["copy_btn"])
                )
            
            copy_btn.click()
            
            # 클립보드 준비 대기 (명시적 대기)
            time.sleep(0.5)
            return True
        except TimeoutException as e:
            return False

    def edit_message(self, original_message, new_message):
        try:
            # 짧은 대기 시간 설정
            short_wait = WebDriverWait(self.driver, 5)
            
            # 1. 수정할 메시지 찾기
            message_element = short_wait.until(
                EC.presence_of_element_located(self.locators["message_bubble"])
            )
            print(f" 수정할 메시지 찾기 완료: {original_message}")
            
            # 2. 메시지에 마우스 오버하여 수정 버튼 표시
            actions = ActionChains(self.driver)
            actions.move_to_element(message_element).perform()
            print(" 메시지에 마우스 오버 완료")
            
            # 3. 수정 버튼 클릭
            edit_btn = short_wait.until(
                EC.element_to_be_clickable(self.locators["edit_btn"])
            )
            edit_btn.click()
            print(" 수정 버튼 클릭 완료")
            
            # 4. 수정 입력창이 나타날 때까지 대기
            edit_input = short_wait.until(
                EC.presence_of_element_located(self.locators["edit_input"])
            )
            print(" 수정 입력창 표시 완료")
            
            # 5. 기존 텍스트 지우고 새 메시지 입력
            edit_input.clear()
            edit_input.send_keys(new_message)
            print(f" 새 메시지 입력 완료: {new_message}")
            
            # 6. 확인 버튼 클릭
            confirm_btn = short_wait.until(
                EC.element_to_be_clickable(self.locators["edit_confirm_btn"])
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

    def scroll_to_top(self):
        try:
            # 방법 1: 첫 번째 메시지로 직접 스크롤
            first_message = self.driver.find_element(*self.locators["first_article"])
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", first_message)
            time.sleep(1)
            print(" 첫 번째 메시지로 스크롤 완료")
            return True
            
        except NoSuchElementException:
            print(" 첫 번째 메시지를 찾을 수 없음")
            return False
        except Exception as e:
            print(f" 스크롤 실패: {e}")
            return False

    def click_scroll_to_latest_button(self):
        """최신 답변으로 이동하는 버튼 클릭"""
        try:
            # 최신 답변으로 이동하는 버튼 찾기
            scroll_button = self.wait.until(
                EC.element_to_be_clickable(self.locators["scroll_latest_btn"])
            )
            scroll_button.click()
            print(" 최신 답변으로 이동 버튼 클릭 완료")
            return True
                
        except TimeoutException as e:
            print(f" 최신 답변으로 이동 버튼을 찾을 수 없음: {e}")
            return False
        except Exception as e:
            print(f" 최신 답변으로 이동 버튼 클릭 실패: {e}")
            return False