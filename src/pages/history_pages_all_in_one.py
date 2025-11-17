# src/pages/ht_pages_all_in_one.py

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

DEFAULT_TIMEOUT = 10
MAIN_URL = "https://qaproject.elice.io/ai-helpy-chat"


# =====================================================================
# BasePage
# =====================================================================

class BasePage:
    def __init__(self, drv, timeout=DEFAULT_TIMEOUT):
        self.drv = drv
        self.timeout = timeout

    # locator / WebElement / 문자열 키(self.locators[]용) 모두 지원
    def _resolve(self, target):
        # 이미 WebElement면 그대로 사용
        if hasattr(target, "is_displayed"):
            return target

        # (By, value) 튜플이면 그대로
        if isinstance(target, tuple):
            return target

        # 문자열이면 self.locators 딕셔너리에서 조회
        if isinstance(target, str) and hasattr(self, "locators"):
            locs = getattr(self, "locators", {})
            if target in locs:
                return locs[target]

        # 그 외에는 그대로 반환 (EC가 처리하도록)
        return target

    def wait(self, sec=None):
        return WebDriverWait(self.drv, sec or self.timeout)

    def visible(self, locator, sec=None):
        target = self._resolve(locator)
        if hasattr(target, "is_displayed"):  # WebElement
            return self.wait(sec).until(EC.visibility_of(target))
        return self.wait(sec).until(EC.visibility_of_element_located(target))

    def present(self, locator, sec=None):
        target = self._resolve(locator)
        if hasattr(target, "is_displayed"):  # 이미 찾은 Element
            return target
        return self.wait(sec).until(EC.presence_of_element_located(target))

    def clickable(self, locator, sec=None):
        target = self._resolve(locator)
        return self.wait(sec).until(EC.element_to_be_clickable(target))

    def js_click(self, el):
        self.drv.execute_script("arguments[0].click();", el)

    def scroll_center(self, el):
        self.drv.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            el,
        )


# =====================================================================
# MainPage
# =====================================================================

class MainPage(BasePage):
    URL = MAIN_URL

    def open(self):
        self.drv.get(self.URL)
        # 메인 도착 확인: Composer 준비될 때까지 대기
        composer = Composer(self.drv)
        composer.wait_ready()


# =====================================================================
# ChatSidebar
# =====================================================================

class ChatSidebar(BasePage):
    locators = {
        "new_chat_btn": (
            By.XPATH,
            "//aside//div[@role='button'][.//span[normalize-space()='새 대화'] "
            "or .//span[normalize-space()='New chat']]",
        ),
        "top_thread": (
            By.CSS_SELECTOR,
            "aside a[href^='/ai-helpy-chat/thread/'][data-index='0']",
        ),
        "top_thread_menu_btn": (
            By.CSS_SELECTOR,
            "aside a[href^='/ai-helpy-chat/thread/'][data-index='0'] .menu-button button",
        ),
        "menu_ul": (By.CSS_SELECTOR, "ul.MuiMenu-list[role='menu']"),
        "menu_rename_item": (
            By.XPATH,
            ".//li[.//*[normalize-space()='이름 변경'] or .//*[normalize-space()='Rename']]",
        ),
        "menu_delete_item": (
            By.XPATH,
            ".//li[.//*[normalize-space()='삭제'] or .//*[normalize-space()='Delete']]",
        ),
        "menu_trash_icon": (
            By.CSS_SELECTOR,
            "li svg[data-icon='trash']",
        ),
        "menu_pen_icon": (
            By.CSS_SELECTOR,
            "li svg[data-icon='pen']",
        ),
        "second_thread": (
            By.CSS_SELECTOR,
            "aside a[href^='/ai-helpy-chat/thread/'][data-index='1']",
        ),
        "sidebar_search_btn": (
            By.XPATH,
            "//aside//div[@role='button'][.//span[normalize-space()='검색'] "
            "or .//span[normalize-space()='Search']]",
        ),
        "sidebar_search_icon": (
            By.CSS_SELECTOR,
            "aside svg[data-testid='magnifying-glassIcon']",
        ),
    }

    def click_new_chat(self):
        self.clickable(self.locators["new_chat_btn"]).click()

    def top_thread_href(self):
        try:
            el = self.present(self.locators["top_thread"], sec=3)
            return el.get_attribute("href")
        except TimeoutException:
            return None

    def top_thread_title(self):
        top = self.visible(self.locators["top_thread"], sec=10)
        try:
            return top.find_element(By.CSS_SELECTOR, "p").text.strip()
        except Exception:
            return (top.text or "").strip()

    def open_top_options(self, timeout: int = 10):
        """
        최상단 쓰레드의 점3개 옵션 메뉴를 여는 메서드.
        리렌더/가상 스크롤로 인한 stale을 피하기 위해 여러 번 재시도한다.
        """
        end = time.time() + timeout
        last_exc = None

        while time.time() < end:
            try:
                # 1) 그 시점의 최신 top thread 요소 가져오기
                top = self.present(self.locators["top_thread"], sec=5)
                self.scroll_center(top)

                # 2) hover 한번 해주고
                ActionChains(self.drv).move_to_element(top).pause(0.2).perform()

                # 3) 그 순간의 메뉴 버튼을 가져와서 클릭
                btn = self.clickable(self.locators["top_thread_menu_btn"], sec=5)
                btn.click()
                return  # 성공하면 바로 종료

            except StaleElementReferenceException as e:
                last_exc = e
                time.sleep(0.2)

            except TimeoutException as e:
                last_exc = e
                try:
                    self.drv.execute_script(
                        """
                        const el = arguments[0];
                        el.dispatchEvent(new MouseEvent('mouseover',{bubbles:true}));
                        el.dispatchEvent(new MouseEvent('mouseenter',{bubbles:true}));
                        el.dispatchEvent(new MouseEvent('mousemove',{bubbles:true}));
                    """,
                        top,
                    )
                    btn = self.present(self.locators["top_thread_menu_btn"], sec=5)
                    self.js_click(btn)
                    return
                except StaleElementReferenceException as e2:
                    last_exc = e2
                    time.sleep(0.2)

        # 여기까지 오면 여러 번 시도해도 실패한 것
        raise last_exc or TimeoutException("최상단 쓰레드 옵션 메뉴 버튼 클릭 실패")

    def click_menu_rename(self):
        menu = self.visible(self.locators["menu_ul"], sec=5)
        try:
            item = menu.find_element(*self.locators["menu_rename_item"])
        except NoSuchElementException:
            # 펜 아이콘 폴백
            try:
                pen = menu.find_element(*self.locators["menu_pen_icon"])
                item = pen.find_element(By.XPATH, "./ancestor::li[1]")
            except Exception:
                raise AssertionError("메뉴에 '이름 변경'이 없습니다.")
        self.scroll_center(item)
        try:
            item = self.clickable(self.locators["menu_rename_item"], sec=5)
            item.click()
        except TimeoutException:
            self.js_click(item)

    def click_menu_delete(self):
        menu = self.visible(self.locators["menu_ul"], sec=5)
        try:
            item = menu.find_element(*self.locators["menu_delete_item"])
        except NoSuchElementException:
            try:
                icon = menu.find_element(*self.locators["menu_trash_icon"])
                item = icon.find_element(By.XPATH, "./ancestor::li[1]")
            except Exception:
                raise AssertionError("메뉴에 '삭제'가 없습니다.")
        self.scroll_center(item)
        try:
            item = self.clickable(self.locators["menu_delete_item"], sec=5)
            item.click()
        except TimeoutException:
            self.js_click(item)

    def click_search_button(self):
        try:
            self.clickable(self.locators["sidebar_search_btn"], sec=5).click()
            return
        except TimeoutException:
            pass
        # 아이콘 폴백
        icon = self.present(self.locators["sidebar_search_icon"], sec=5)
        btn = icon.find_element(By.XPATH, "./ancestor::div[@role='button'][1]")
        self.scroll_center(btn)
        try:
            self.clickable(btn, sec=2)  # type: ignore
            btn.click()
        except Exception:
            self.js_click(btn)

    def click_second_thread(self):
        self.clickable(self.locators["second_thread"]).click()


# =====================================================================
# Composer
# =====================================================================

class Composer(BasePage):
    locators = {
        "textarea": (
            By.CSS_SELECTOR,
            "#message-composer .MuiInputBase-root textarea.MuiInputBase-input"
            ":not([aria-hidden='true']):not([readonly])",
        ),
        "submit_enabled": (
            By.CSS_SELECTOR,
            "button#chat-submit:not([disabled])",
        ),
    }

    def wait_ready(self, sec=None):
        # 처음 준비 + 응답 끝난 뒤 “다시” 준비 둘 다 여기로
        self.visible(self.locators["textarea"], sec)

    def send(self, text: str):
        ta = self.clickable(self.locators["textarea"])
        try:
            ta.click()
            ta.send_keys(text)
        except Exception:
            self.drv.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                ta,
                text,
            )
        self.wait(20).until(
            EC.element_to_be_clickable(self.locators["submit_enabled"])
        ).click()


# =====================================================================
# Dialogs
# =====================================================================

class Dialogs(BasePage):
    locators = {
        "dialog": (
            By.CSS_SELECTOR,
            "div[role='dialog']",
        ),
        "dialog_delete_btn": (
            By.XPATH,
            ".//button[@type='button' and "
            " (normalize-space()='삭제' or normalize-space()='Delete' or "
            "  .//*[normalize-space()='삭제'] or .//*[normalize-space()='Delete'])]",
        ),
        "dialog_delete_btn_fallback": (
            By.CSS_SELECTOR,
            "button.MuiButton-containedError, button.MuiButton-colorError",
        ),
    }

    def confirm_delete(self):
        dlg = self.visible(self.locators["dialog"], sec=10)

        try:
            btn = dlg.find_element(*self.locators["dialog_delete_btn"])
        except NoSuchElementException:
            btn = dlg.find_element(*self.locators["dialog_delete_btn_fallback"])

        try:
            self.wait(10).until(lambda d: btn.is_enabled() and btn.is_displayed())
            btn.click()
        except Exception:
            self.js_click(btn)

        # 🔽 여기서부터는 dlg를 신뢰하지 않고, 매번 새로 찾음
        def _dialog_closed(drv):
            try:
                el = drv.find_element(*self.locators["dialog"])
                return not el.is_displayed()
            except (NoSuchElementException, StaleElementReferenceException):
                # 못 찾거나 stale이면 이미 닫힌 것으로 본다
                return True

        self.wait(10).until(_dialog_closed)


# =====================================================================
# SearchOverlay
# =====================================================================

class SearchOverlay(BasePage):
    locators = {
        "search_input_strict": (
            By.CSS_SELECTOR,
            "input[cmdk-input][role='combobox'][type='text'][placeholder='대화 검색...']",
        ),
    }

    def type_query(self, text, sec=10):
        inp = self.visible(self.locators["search_input_strict"], sec=sec)
        try:
            inp.click()
        except Exception:
            self.js_click(inp)

        # 기존 값 지우기
        try:
            inp.clear()
        except Exception:
            pass

        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)

        # 값 입력
        try:
            inp.send_keys(text)
        except Exception:
            self.drv.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                inp,
                text,
            )

        # 실제 value가 세팅될 때까지 대기
        self.wait(5).until(lambda d: (inp.get_attribute("value") or "") == text)

    def wait_result_has_prefix(self, prefix: str, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            ok = self.drv.execute_script(
                """
                const prefix = arguments[0];
                const nodes = document.querySelectorAll("[cmdk-item][role='option']");
                return Array.from(nodes).some(
                    n => (n.getAttribute("data-value") || "").startsWith(prefix)
                );
            """,
                prefix,
            )
            if ok:
                return
            time.sleep(0.1)
        raise TimeoutException(f"검색 결과에 prefix '{prefix}' 없음")

    def get_values(self, timeout=10):
        end = time.time() + timeout
        last = []
        while time.time() < end:
            vals = self.drv.execute_script(
                """
                const nodes = document.querySelectorAll("[cmdk-item][role='option']");
                return Array.from(nodes)
                    .map(n => (n.getAttribute("data-value") || "").trim())
                    .filter(Boolean);
            """
            )
            last = vals or []
            if last:
                return last
            time.sleep(0.1)
        return last


# =====================================================================
# AgentExplorerPage
# =====================================================================

class AgentExplorerPage(BasePage):
    locators = {
        "agent_explorer_link": (
            By.CSS_SELECTOR,
            "aside a[href='/ai-helpy-chat/agent']",
        ),
        "agent_search_input": (
            By.CSS_SELECTOR,
            "input[placeholder='Search AI agents'][type='text']",
        ),
        "agent_titles": (
            By.CSS_SELECTOR,
            "[data-testid='virtuoso-item-list'] "
            "a[href^='/ai-helpy-chat/agent/'] p.MuiTypography-body1",
        ),
    }

    def open(self):
        self.clickable(self.locators["agent_explorer_link"]).click()
        self.wait().until(lambda d: "/ai-helpy-chat/agent" in d.current_url)

    def search(self, text: str):
        inp = self.clickable(self.locators["agent_search_input"])
        inp.click()
        try:
            inp.clear()
        except Exception:
            pass

        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        inp.send_keys(text)

        self.wait(5).until(lambda d: inp.get_attribute("value") == text)

    def assert_all_titles_contain(self, query: str, timeout: int = 10):
        q = (query or "").strip().lower()
        end = self.drv.execute_script("return Date.now();") + timeout * 1000
        last = []

        while self.drv.execute_script("return Date.now();") < end:
            try:
                elems = self.drv.find_elements(*self.locators["agent_titles"])
                titles = [el.text.strip() for el in elems]
            except StaleElementReferenceException:
                time.sleep(0.1)
                continue

            if not titles or any(not t for t in titles):
                time.sleep(0.1)
                continue

            last = titles

            if all(q in t.lower() for t in titles):
                return

            time.sleep(0.1)

        raise AssertionError(f"전부 포함 실패: query='{query}', titles={last}")
