import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from .ht_base_page import BasePage

SEL_SEARCH_INPUT_STRICT = (
    By.CSS_SELECTOR,
    "input[cmdk-input][role='combobox'][type='text'][placeholder='대화 검색...']"
)

class SearchOverlay(BasePage):
    def type_query(self, text, sec=10):
        inp = self.visible(SEL_SEARCH_INPUT_STRICT, sec=sec)
        try:
            inp.click()
        except Exception:
            self.js_click(inp)
        try:
            inp.clear()
        except Exception:
            pass
        from selenium.webdriver.common.keys import Keys
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        try:
            inp.send_keys(text)
        except Exception:
            self.drv.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                inp, text
            )
        self.wait(5).until(lambda d: (inp.get_attribute("value") or "") == text)

    def wait_result_has_prefix(self, prefix: str, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            ok = self.drv.execute_script("""
                const prefix = arguments[0];
                const nodes = document.querySelectorAll("[cmdk-item][role='option']");
                return Array.from(nodes).some(n => (n.getAttribute("data-value")||"").startsWith(prefix));
            """, prefix)
            if ok:
                return
            time.sleep(0.1)
        raise TimeoutException(f"검색 결과에 prefix '{prefix}' 없음")

    def get_values(self, timeout=10):
        end = time.time() + timeout
        last = []
        while time.time() < end:
            vals = self.drv.execute_script("""
                const nodes = document.querySelectorAll("[cmdk-item][role='option']");
                return Array.from(nodes).map(n => (n.getAttribute("data-value")||"").trim()).filter(Boolean);
            """)
            last = vals or []
            if last:
                return last
            time.sleep(0.1)
        return last
