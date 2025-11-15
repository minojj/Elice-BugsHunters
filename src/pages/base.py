from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class BasePage:
    LOCATORS = {}

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def get_element(self, key, wait_type="visible", timeout=10):
        #요소 키워드(agent_explorer_btn, create_btn 등)를 받아 element 반환
        locator = self.LOCATORS[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)
    
    
    def get_elements(self, key, timeout=10):
        locator = self.LOCATORS[key]
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)
    

    def click_safely(self, key, timeout=10):
        locator = self.LOCATORS[key]
        wait = WebDriverWait(self.driver, timeout)

        element = wait.until(EC.presence_of_element_located(locator))
        wait.until(EC.element_to_be_clickable(locator))

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

        self.driver.execute_script("arguments[0].click();", element)

        return element
