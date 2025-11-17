import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from .base import BasePage

class ChatPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 30)  # ChatPage만 30초로 확장

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
            search_box = self.get_element("search_box", wait_type="clickable", timeout=30)
            search_box.send_keys(message)

            self.click_safely("chat_submit", timeout=30)
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[role="article"]')))
            return True

        except TimeoutException:
            return False

    def get_ai_response(self, expected_text):
        """AI 응답 메시지 확인 (동적 XPath)"""
        try:
            ai_response_xpath = self.locators["ai_response"].format(text=expected_text)
            return self.wait.until(
                EC.presence_of_element_located((By.XPATH, ai_response_xpath))
            )

        except Exception:
            return False

    def check_image_exists(self):
        """AI 응답에 이미지가 있는지 확인"""
        try:
            return self.get_element("image", wait_type="visible", timeout=30)
        except TimeoutException:
            return None

    def upload_file(self, file_path):
        """파일 업로드"""
        try:
            if not os.path.exists(file_path):
                return False

            file_input = self.get_element("file_input", wait_type="presence", timeout=30)

            abs_path = os.path.abspath(file_path)
            file_input.send_keys(abs_path)

            return True

        except Exception:
            return False

    def copy_message(self, ai_response_element=None):
        """메시지 복사 버튼 클릭"""
        try:
            if ai_response_element:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        copy_btn = ai_response_element.find_element(*self.locators["copy_btn"])
                        break
                    except:
                        if attempt < max_retries - 1:
                            time.sleep(0.5)
                            continue
                        copy_btn = self.get_element("copy_btn", wait_type="clickable", timeout=30)
            else:
                copy_btn = self.get_element("copy_btn", wait_type="clickable", timeout=30)

            copy_btn.click()
            time.sleep(0.5)
            return True

        except TimeoutException:
            return False

    def edit_message(self, original_message, new_message):
        try:
            short_wait = WebDriverWait(self.driver, 5)

            message_element = short_wait.until(
                EC.presence_of_element_located(self.locators["message_bubble"])
            )

            actions = ActionChains(self.driver)
            actions.move_to_element(message_element).perform()

            edit_btn = short_wait.until(
                EC.element_to_be_clickable(self.locators["edit_btn"])
            )
            edit_btn.click()

            edit_input = short_wait.until(
                EC.presence_of_element_located(self.locators["edit_input"])
            )
            edit_input.clear()
            edit_input.send_keys(new_message)

            confirm_btn = short_wait.until(
                EC.element_to_be_clickable(self.locators["edit_confirm_btn"])
            )
            confirm_btn.click()

            return True

        except Exception:
            return False

    def scroll_to_top(self):
        try:
            first_message = self.get_element("first_article", wait_type="presence", timeout=10)

            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});",
                first_message
            )
            time.sleep(1)

            return True

        except:
            return False

    def click_scroll_to_latest_button(self):
        """최신 답변으로 이동하는 버튼 클릭"""
        try:
            self.click_safely("scroll_latest_btn", timeout=30)
            return True

        except:
            return False