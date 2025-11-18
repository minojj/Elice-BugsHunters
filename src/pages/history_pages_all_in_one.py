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
from .base_page import BasePage

DEFAULT_TIMEOUT = 10
MAIN_URL = "https://qaproject.elice.io/ai-helpy-chat"


# =====================================================================
# MainPage
# =====================================================================

class MainPage(BasePage):
    URL = MAIN_URL

    def __init__(self, driver):
        super().__init__(driver)

    def open(self):
        # 메인 URL로 이동
        self.driver.get(self.URL)

        # 메인 도착 확인: Composer 준비될 때까지 대기
        composer = Composer(self.driver)
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
    def __init__(self, driver):
        super().__init__(driver)

    # --- 0-1) 이 클래스 안에서만 get_element / get_elements 재정의 ---
    # (BasePage 파일은 그대로 두고, ChatSidebar 전용으로 고쳐 쓰는 느낌)
    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            return wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            return wait.until(EC.presence_of_element_located(locator))
        else:
            return wait.until(EC.visibility_of_element_located(locator))

    def get_elements(self, key, timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))

    # --- 0-2) 예전에 쓰던 헬퍼 함수들 ChatSidebar 안에만 정의 ---
    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    def clickable(self, key, sec=10):
        return self.get_element(key, wait_type="clickable", timeout=sec)

    def present(self, key, sec=10):
        return self.get_element(key, wait_type="presence", timeout=sec)

    def scroll_center(self, el):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});", el
        )

    def js_click(self, el):
        self.driver.execute_script("arguments[0].click();", el)

    # --- 1) 새 대화 버튼 ---
    def click_new_chat(self):
        # BasePage.click_safely(key) 재사용
        self.click_safely("new_chat_btn")

    # --- 2) 최상단 스레드 href ---
    def top_thread_href(self):
        try:
            el = self.present("top_thread", sec=3)
            return el.get_attribute("href")
        except TimeoutException:
            return None

    # --- 3) 최상단 스레드 제목 ---
    def top_thread_title(self):
        top = self.visible("top_thread", sec=10)
        try:
            return top.find_element(By.CSS_SELECTOR, "p").text.strip()
        except Exception:
            return (top.text or "").strip()

    # --- 4) 옵션(점3개) 열기 ---
    def open_top_options(self, timeout: int = 10):
        """
        최상단 쓰레드의 점3개 옵션 메뉴를 여는 메서드.
        리렌더/가상 스크롤로 인한 stale을 피하기 위해 여러 번 재시도한다.
        """
        end = time.time() + timeout
        last_exc = None

        while time.time() < end:
            try:
                top = self.present("top_thread", sec=5)
                self.scroll_center(top)

                # hover
                ActionChains(self.driver).move_to_element(top).pause(0.2).perform()

                # 메뉴 버튼 클릭
                btn = self.clickable("top_thread_menu_btn", sec=5)
                btn.click()
                return

            except StaleElementReferenceException as e:
                last_exc = e
                time.sleep(0.2)

            except TimeoutException as e:
                last_exc = e
                try:
                    # JS로 hover 이벤트 강제
                    self.driver.execute_script(
                        """
                        const el = arguments[0];
                        el.dispatchEvent(new MouseEvent('mouseover',{bubbles:true}));
                        el.dispatchEvent(new MouseEvent('mouseenter',{bubbles:true}));
                        el.dispatchEvent(new MouseEvent('mousemove',{bubbles:true}));
                        """,
                        top,
                    )
                    btn = self.present("top_thread_menu_btn", sec=5)
                    self.js_click(btn)
                    return
                except StaleElementReferenceException as e2:
                    last_exc = e2
                    time.sleep(0.2)

        raise last_exc or TimeoutException("최상단 쓰레드 옵션 메뉴 버튼 클릭 실패")

    # --- 5) 메뉴 - 이름 변경 ---
    def click_menu_rename(self):
        menu = self.visible("menu_ul", sec=5)
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
            # locator 기준으로 clickable 대기
            item = self.clickable("menu_rename_item", sec=5)
            item.click()
        except TimeoutException:
            self.js_click(item)

    # --- 6) 메뉴 - 삭제 ---
    def click_menu_delete(self):
        menu = self.visible("menu_ul", sec=5)
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
            item = self.clickable("menu_delete_item", sec=5)
            item.click()
        except TimeoutException:
            self.js_click(item)

    # --- 7) 사이드바 검색 버튼 ---
    def click_search_button(self):
        # 1차 시도: 텍스트 버튼
        try:
            self.click_safely("sidebar_search_btn", timeout=5)
            return
        except TimeoutException:
            pass

        # 2차 시도: 아이콘 → 부모 div[role='button']
        icon = self.present("sidebar_search_icon", sec=5)
        btn = icon.find_element(By.XPATH, "./ancestor::div[@role='button'][1]")
        self.scroll_center(btn)

        try:
            WebDriverWait(self.driver, 2).until(lambda d: btn.is_enabled())
            btn.click()
        except Exception:
            self.js_click(btn)

    # --- 8) 두 번째 스레드 클릭 ---
    def click_second_thread(self):
        self.click_safely("second_thread")



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

    def __init__(self, driver):
        super().__init__(driver)

    # --- 이 클래스 안에서만 get_element / visible / clickable 재정의 ---
    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            return wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            return wait.until(EC.presence_of_element_located(locator))
        else:
            return wait.until(EC.visibility_of_element_located(locator))

    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    def clickable(self, key, sec=10):
        return self.get_element(key, wait_type="clickable", timeout=sec)

    # --- 실제 기능 메서드들 ---

    def wait_ready(self, sec=None):
        # 처음 준비 + 응답 끝난 뒤 “다시” 준비 둘 다 여기로
        self.visible("textarea", sec or 10)

    def send(self, text: str):
        ta = self.clickable("textarea")
        try:
            ta.click()
            ta.send_keys(text)
        except Exception:
            # BasePage는 self.driver를 쓰니까 여기서도 driver 사용
            self.driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                ta,
                text,
            )

        # BasePage.wait()는 속성 이름 충돌나서 직접 WebDriverWait 사용
        WebDriverWait(self.driver, 20).until(
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

    def __init__(self, driver):
        super().__init__(driver)
    # --- 이 클래스 안에서만 사용할 헬퍼들 ---

    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            return wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            return wait.until(EC.presence_of_element_located(locator))
        else:
            return wait.until(EC.visibility_of_element_located(locator))

    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    def js_click(self, el):
        self.driver.execute_script("arguments[0].click();", el)

    # --- 실제 기능 ---

    def confirm_delete(self):
        # ✅ 여기서부터는 key 문자열 사용
        dlg = self.visible("dialog", sec=10)

        try:
            btn = dlg.find_element(*self.locators["dialog_delete_btn"])
        except NoSuchElementException:
            btn = dlg.find_element(*self.locators["dialog_delete_btn_fallback"])

        try:
            # BasePage.wait 대신 WebDriverWait 직접 사용
            WebDriverWait(self.driver, 10).until(
                lambda d: btn.is_enabled() and btn.is_displayed()
            )
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

        WebDriverWait(self.driver, 10).until(_dialog_closed)


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

    def __init__(self, driver):
        super().__init__(driver)



    # --- 이 클래스 안에서만 쓸 헬퍼들 ---

    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            return wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            return wait.until(EC.presence_of_element_located(locator))
        else:
            return wait.until(EC.visibility_of_element_located(locator))

    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    def js_click(self, el):
        self.driver.execute_script("arguments[0].click();", el)

    # --- 실제 기능 메서드들 ---

    def type_query(self, text, sec=10):
        # 🔹 key 문자열로 사용
        inp = self.visible("search_input_strict", sec=sec)

        # 클릭 (안 되면 JS 클릭)
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
            self.driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                inp,
                text,
            )

        # 실제 value가 세팅될 때까지 대기
        WebDriverWait(self.driver, 5).until(
            lambda d: (inp.get_attribute("value") or "") == text
        )

    def wait_result_has_prefix(self, prefix: str, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            ok = self.driver.execute_script(
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
            vals = self.driver.execute_script(
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

    def __init__(self, driver):
        super().__init__(driver)

    # --- 이 클래스 전용 헬퍼들 ---

    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            return wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            return wait.until(EC.presence_of_element_located(locator))
        else:  # visible
            return wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, key, sec=10):
        return self.get_element(key, wait_type="clickable", timeout=sec)

    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    # --- 실제 기능 메서드들 ---

    def open(self):
        # 예전: self.clickable(self.locators["agent_explorer_link"]).click()
        self.clickable("agent_explorer_link").click()
        WebDriverWait(self.driver, 10).until(
            lambda d: "/ai-helpy-chat/agent" in d.current_url
        )

    def search(self, text: str):
        inp = self.clickable("agent_search_input", sec=10)

        inp.click()
        try:
            inp.clear()
        except Exception:
            pass

        # 기존 값 삭제
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)

        # 검색어 입력
        inp.send_keys(text)

        # 실제 value가 세팅될 때까지 대기
        WebDriverWait(self.driver, 5).until(
            lambda d: (inp.get_attribute("value") or "") == text
        )

    def assert_all_titles_contain(self, query: str, timeout: int = 10):
        q = (query or "").strip().lower()
        end = self.driver.execute_script("return Date.now();") + timeout * 1000
        last = []

        while self.driver.execute_script("return Date.now();") < end:
            try:
                elems = self.driver.find_elements(*self.locators["agent_titles"])
                titles = [el.text.strip() for el in elems]
            except StaleElementReferenceException:
                time.sleep(0.1)
                continue

            # 결과 없거나 빈 텍스트가 있으면 다시 시도
            if not titles or any(not t for t in titles):
                time.sleep(0.1)
                continue

            last = titles

            # 전부 query 포함하면 성공
            if all(q in t.lower() for t in titles):
                return

            time.sleep(0.1)

        # 여기까지 오면 실패
        raise AssertionError(f"전부 포함 실패: query='{query}', titles={last}")
