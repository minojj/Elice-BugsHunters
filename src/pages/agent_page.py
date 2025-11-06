from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.utils.helpers import wait_for

class AgentPage:
    URL = "https://qatrack.elice.io/ai-helpy-chat/agent"

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def send_message(self, text):
        textarea = wait_for(self.driver, By.TAG_NAME, "textarea")
        textarea.send_keys(text)
        textarea.send_keys(Keys.ENTER)
