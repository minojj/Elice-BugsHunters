from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_TIMEOUT = 10

class BasePage:
    def __init__(self, drv, timeout=DEFAULT_TIMEOUT):
        self.drv = drv
        self.timeout = timeout

    def wait(self, sec=None):
        return WebDriverWait(self.drv, sec or self.timeout)

    def visible(self, locator, sec=None):
        return self.wait(sec).until(EC.visibility_of_element_located(locator))

    def present(self, locator, sec=None):
        return self.wait(sec).until(EC.presence_of_element_located(locator))

    def clickable(self, locator, sec=None):
        return self.wait(sec).until(EC.element_to_be_clickable(locator))

    def js_click(self, el):
        self.drv.execute_script("arguments[0].click();", el)

    def scroll_center(self, el):
        self.drv.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

    