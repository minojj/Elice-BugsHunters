from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .ht_base_page import BasePage

SEL_TEXTAREA = (
    By.CSS_SELECTOR,
    "#message-composer .MuiInputBase-root textarea.MuiInputBase-input:not([aria-hidden='true']):not([readonly])",
)
SEL_SUBMIT_ENABLED = (By.CSS_SELECTOR, "button#chat-submit:not([disabled])")

class Composer(BasePage):
    def wait_ready(self):
        self.visible(SEL_TEXTAREA)

    def send(self, text: str):
        ta = self.clickable(SEL_TEXTAREA)
        try:
            ta.click()
            ta.send_keys(text)
        except Exception:
            self.drv.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                ta, text
            )
        self.wait(20).until(EC.element_to_be_clickable(SEL_SUBMIT_ENABLED)).click()
