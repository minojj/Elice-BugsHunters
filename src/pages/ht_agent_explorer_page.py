from selenium.webdriver.common.by import By
from .ht_base_page import BasePage
from selenium.common.exceptions import StaleElementReferenceException
import time

SEL_AGENT_EXPLORER_LINK = (By.CSS_SELECTOR, "aside a[href='/ai-helpy-chat/agent']")
SEL_AGENT_SEARCH_INPUT  = (By.CSS_SELECTOR, "input[placeholder='Search AI agents'][type='text']")
SEL_AGENT_TITLES        = (By.CSS_SELECTOR, "[data-testid='virtuoso-item-list'] a[href^='/ai-helpy-chat/agent/'] p.MuiTypography-body1")

class AgentExplorerPage(BasePage):
    def open(self):
        self.clickable(SEL_AGENT_EXPLORER_LINK).click()
        self.wait().until(lambda d: "/ai-helpy-chat/agent" in d.current_url)

    def search(self, text: str):
        inp = self.clickable(SEL_AGENT_SEARCH_INPUT)
        inp.click()
        try:
            inp.clear()
        except Exception:
            pass
        from selenium.webdriver.common.keys import Keys
        inp.send_keys(Keys.CONTROL, "a"); inp.send_keys(Keys.DELETE); inp.send_keys(text)
        self.wait(5).until(lambda d: inp.get_attribute("value") == text)

    def assert_all_titles_contain(self, query: str, timeout: int = 10):
        q = (query or "").strip().lower()
        end = self.drv.execute_script("return Date.now();") + timeout * 1000
        last = []

        while self.drv.execute_script("return Date.now();") < end:
            try:
                # 🔹 요소를 매번 새로 찾고, 그 순간에만 텍스트 읽기
                elems = self.drv.find_elements(*SEL_AGENT_TITLES)
                titles = [el.text.strip() for el in elems]
            except StaleElementReferenceException:
                # 🔹 리렌더 중이면 한 템포 쉬고 다시 시도
                time.sleep(0.1)
                continue

            # 아직 아무 카드도 없거나, 비어있는 타이틀이 있으면 다시 시도
            if not titles or any(not t for t in titles):
                time.sleep(0.1)
                continue

            last = titles

            # 🔹 여기까지 왔으면 titles는 “안정적인 순간”에 읽힌 것
            if all(q in t.lower() for t in titles):
                return

            time.sleep(0.1)  # 너무 빡세게 루프 돌지 않게 살짝 쉬기

        raise AssertionError(f"전부 포함 실패: query='{query}', titles={last}")
