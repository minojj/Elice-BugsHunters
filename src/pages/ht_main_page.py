# src/pages/ht_main_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .ht_base_page import BasePage
from .ht_composer import Composer

MAIN_URL = "https://qaproject.elice.io/ai-helpy-chat"

class MainPage(BasePage):
    URL = MAIN_URL

    def open(self):
        self.drv.get(self.URL)
        composer = Composer(self.drv)
        composer.wait_ready()
