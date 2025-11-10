from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.chrome.service import Service
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from src.utils.helpers import Utils

class CreateAgentPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"
        self.locators = {
            "name": (By.NAME, "name"),
            "description": (By.CSS_SELECTOR, 'input[name="description"]'),
            "rules": (By.NAME, "systemPrompt"),
            "conversation": (By.NAME, "conversationStarters.0.value"),
            "create_btn": (By.CSS_SELECTOR, "button.MuiButton-containedPrimary"),
        }

    def open(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 커스텀 에이전트 메인 페이지 접속 성공")

    def get_element(self, key, wait_type="visible", timeout=10):
        #요소 키워드(name, description 등)를 받아 element 반환
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)

    def fill_form(self, name, description, rules, conversation):
        self.get_element("name").send_keys(name)
        self.get_element("description", "clickable").send_keys(description)
        self.get_element("rules").send_keys(rules)
        self.get_element("conversation").send_keys(conversation)

   
    
    

class SaveAgentPage:
    def __init__(self, driver):
        self.driver = driver
        self.locators = {
            "private_radio": (By.CSS_SELECTOR, "input[value='private']"),
            "organization_radio": (By.CSS_SELECTOR, "input[value='organization']"),
            "save_btn": (By.CSS_SELECTOR, "button[type='submit'][form='publish-setting-form']"),
            "success_alert": (By.CSS_SELECTOR, "div#notistack-snackbar"),
            "start_chat_btn": (By.CSS_SELECTOR, "div#notistack-snackbar button[type='button']"),
            "chat_input": (By.CSS_SELECTOR, "textarea[name='input']")
        }

    def select_mode(self, mode):
        key = f"{mode}_radio"

        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-paper")))

        radio = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.locators[key]))
        if not radio.is_selected():
            clickable_radio = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio.get_attribute('id')}']")
            self.driver.execute_script("arguments[0].click();", clickable_radio)
        check_radio = self.driver.find_element(*self.locators[key])
        assert check_radio.is_selected(), f"{mode} 옵션이 선택되지 않았습니다."


    def click_save(self):
        save_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.locators["save_btn"]))
        save_btn.click()

    def click_start_chat_fast(self):
        btn = WebDriverWait(self.driver, 2, poll_frequency=0.1).until(EC.presence_of_element_located(self.locators["start_chat_btn"]))
        self.driver.execute_script("arguments[0].click();", btn)


    def verify_success(self):
        alert = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.locators["success_alert"]))
        assert "The agent has been created" in alert.text, "❌ 에이전트 생성 실패"
        print("✅ 에이전트 생성 성공!")

    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)