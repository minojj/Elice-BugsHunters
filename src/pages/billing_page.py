from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage




class BillingPage(BasePage):
    URL = "https://qaproject.elice.io/admin/org/billing/payments/credit"

    locators = {
        "usage_table": (By.CSS_SELECTOR,"table.MuiTable-root"),
            
            }

    def __init__(self, driver):
        super().__init__(driver)

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(lambda d: "/admin/org/billing/payments/credit" in d.current_url)

    def wait_usage_table_loaded(self, timeout: int = 20):
        return self.get_element("usage_table", wait_type="presence", timeout=timeout)



class PaymentMethodsPage(BasePage):
    URL = "https://qaproject.elice.io/admin/org/billing/payments/methods"

    locators = {
        "register_method_btn": (By.XPATH,"//button[normalize-space()='결제 수단 등록']"),
        "currency_krw_radio": (By.XPATH,"//label[.//span[normalize-space()='KRW (₩)']]"),
        "currency_confirm_btn": (By.XPATH, "//button[normalize-space()='확인']"),
            }

    def __init__(self, driver):
        super().__init__(driver)

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(
            lambda d: "/admin/org/billing/payments/methods" in d.current_url
        )

    def click_register_method(self):
        self.click_safely("register_method_btn")

    def select_currency_krw(self):
        self.click_safely("currency_krw_radio")

    def confirm_currency_selection(self):
        self.click_safely("currency_confirm_btn")



class DanalCardPage(BasePage):
    locators = {
    
        "danal_iframe": (By.CSS_SELECTOR,"iframe[src*='danal']"),

        "logo": (By.ID, "H1_LOGO"),

        "title": (By.CSS_SELECTOR, ".danal_tit"),

        "terms_title": (By.XPATH, "//span[normalize-space()='이용약관동의']"),
        
        }

    def __init__(self, driver):
        super().__init__(driver)

    def switch_to_danal_iframe(self, timeout: int = 15):
 
        locator = self.locators["danal_iframe"]
        WebDriverWait(self.driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it(locator)
        )

    def is_loaded(self, timeout: int = 10) -> bool:

        try:
            self.get_element("logo", wait_type="visible", timeout=timeout)
            self.get_element("title", wait_type="visible", timeout=timeout)
            self.get_element("terms_title", wait_type="visible", timeout=timeout)
            return True
        except Exception:
            return False





class UsagePage(BasePage):

    locators = {
        "settings_btn": (By.CSS_SELECTOR, "svg[data-testid='gearIcon']"),
        "usage_history_menu": (By.CSS_SELECTOR, "a.MuiMenuItem-root"),
        "usage_history_title": (By.CSS_SELECTOR, "h4.MuiTypography-h4"),
        "ml_api_tab": (By.CSS_SELECTOR, "button[id$='T-ml_api']"),
        "ml_api_table": (By.CSS_SELECTOR, "table.MuiTable-root"),
        "serverless_status": (By.CSS_SELECTOR, "a[href='/cloud/mlapi/metrics']"),
        "serverless_header": (By.CSS_SELECTOR, "h4.MuiTypography-h4"),
        "api_key_manage": (By.CSS_SELECTOR, "a[href='/cloud/mlapi/keys']"),
        "api_key_manage_header": (By.CSS_SELECTOR, "h4.MuiTypography-h4"),

    }
    


    def __init__(self, driver):
        super().__init__(driver)


    def is_current_url(self, expected: str):
        return expected in self.driver.current_url
    
    
    def click_settings_button(self):
        self.driver.get("https://qaproject.elice.io")
        svg = self.get_element("settings_btn", wait_type="clickable")
        button = svg.find_element(By.XPATH, "./ancestor::button")
        button.click()


    def usage_history_click(self):
        self.click_settings_button()
        self.get_element("usage_history_menu", wait_type="clickable", timeout=5)
        self.click_safely("usage_history_menu")


    def is_usage_history_page(self):
        try:
            if not self.is_current_url("/cloud/usage"):
                return False

            header = self.get_element("usage_history_title", timeout=7)
            return "이용내역" in header.text
        
        except:
            return False
        



    def click_ml_api_tab(self):
        self.click_safely("ml_api_tab")


    def is_ml_api_selected(self):
        try:
            self.get_element("ml_api_table", "presence", timeout=7)
            return True
        except:
            return False
        



    def click_serverless_status(self):
        self.click_safely("serverless_status")


    def is_serverless_status_page(self):
        try:
            if not self.is_current_url("/cloud/mlapi/metrics"):
                return False
            
            header = self.get_element("serverless_header", timeout=7)
            return "Serverless" in header.text
        except:
            return False
        

    def click_api_key_manage(self):
        self.click_safely("api_key_manage")
        WebDriverWait(self.driver, 10).until(lambda d: "/keys/serverless" in d.current_url)


    def is_api_key_manage_page(self):
        try:
            if "/keys/serverless" not in self.driver.current_url:
                return False
            header = self.get_element("api_key_manage_header", timeout=10)
            return "API 키 관리" in header.text
        except:
            return False

    
