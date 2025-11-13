from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from .ht_base_page import BasePage

SEL_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")
XPATH_DIALOG_DELETE_BTN = (
    ".//button[@type='button' and "
    " (normalize-space()='삭제' or normalize-space()='Delete' or "
    "  .//*[normalize-space()='삭제'] or .//*[normalize-space()='Delete'])]"
)

class Dialogs(BasePage):
    def confirm_delete(self):
        dlg = self.visible(SEL_DIALOG, sec=10)

        try:
            btn = dlg.find_element(By.XPATH, XPATH_DIALOG_DELETE_BTN)
        except NoSuchElementException:
            btn = dlg.find_element(
                By.CSS_SELECTOR,
                "button.MuiButton-containedError, button.MuiButton-colorError"
            )

        try:
            self.wait(10).until(lambda d: btn.is_enabled() and btn.is_displayed())
            btn.click()
        except Exception:
            self.js_click(btn)

        # 🔽 여기서부터는 dlg를 신뢰하지 않고, 매번 새로 찾음
        def _dialog_closed(drv):
            try:
                el = drv.find_element(*SEL_DIALOG)
                return not el.is_displayed()
            except (NoSuchElementException, StaleElementReferenceException):
                # 못 찾거나 stale이면 이미 닫힌 것으로 본다
                return True

        self.wait(10).until(_dialog_closed)

