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
from src.pages.base_page import BasePage




# =====================================================================
# MainPage
# =====================================================================

class MainPage(BasePage):
    URL = "https://qaproject.elice.io/ai-helpy-chat"

    def __init__(self, driver):
        # BasePage 초기화
        super().__init__(driver)

    def open(self):
        # 메인 URL로 이동
        self.driver.get(self.URL)
        # 메인 도착 확인: Composer 준비될 때까지 대기
        composer = Composer(self.driver)
        composer.wait_ready(sec=15)
        time.sleep(3)  # aside 및 전체 UI 렌더링 대기 (Docker 헤드리스 환경용)

    def wait_ready(self, sec=10):
        """외부에서 main.wait_ready()로도 쓸 수 있게 헬퍼 하나 추가"""
        Composer(self.driver).wait_ready(sec=sec)


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
            By.CSS_SELECTOR,
            "button.MuiButton-containedPrimary[type='button']",
        ),
        "sidebar_search_icon": (
            By.CSS_SELECTOR,
            "aside svg[data-testid='magnifying-glassIcon']",
        ),
    }

    def __init__(self, driver):
        # BasePage.__init__ 사용
        super().__init__(driver)

    # --- BasePage.get_element를 감싸는 헬퍼들 ---
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
        """새 대화 버튼 클릭 (4-방법 fallback)"""
        success = False
        last_error = None
        
        # 방법 1: 원래 XPath (aside 포함)
        try:
            self.click_safely("new_chat_btn", timeout=8)
            success = True
            return
        except Exception as e:
            last_error = e
            pass
        
        # 방법 2: aside 없이 더 넓은 범위로 검색
        if not success:
            try:
                btn = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//div[@role='button'][.//span[normalize-space()='새 대화'] "
                        "or .//span[normalize-space()='New chat']]"))
                )
                self.driver.execute_script("arguments[0].click();", btn)
                success = True
                return
            except Exception as e:
                last_error = e
                pass
        
        # 방법 3: 모든 span 중 '새 대화' 또는 'New chat' 텍스트 찾기
        if not success:
            try:
                end = time.time() + 10
                while time.time() < end:
                    spans = self.driver.find_elements(By.XPATH, "//span")
                    for span in spans:
                        try:
                            text = span.text.strip()
                            if text in ['새 대화', 'New chat']:
                                # 부모 button 또는 div[role='button'] 찾기
                                try:
                                    btn = span.find_element(By.XPATH, "ancestor::button[1]")
                                except:
                                    btn = span.find_element(By.XPATH, "ancestor::div[@role='button'][1]")
                                self.driver.execute_script("arguments[0].click();", btn)
                                success = True
                                return
                        except:
                            continue
                    if not success:
                        time.sleep(0.5)
            except Exception as e:
                last_error = e
                pass
        
        # 방법 4: JavaScript로 텍스트 기반 클릭
        if not success:
            try:
                self.driver.execute_script("""
                    const spans = Array.from(document.querySelectorAll('span'));
                    const target = spans.find(s => s.textContent.trim() === '새 대화' || s.textContent.trim() === 'New chat');
                    if (target) {
                        let btn = target.closest('button') || target.closest('[role="button"]');
                        if (btn) btn.click();
                    }
                """)
                success = True
                return
            except Exception as e:
                last_error = e
                pass
        
        if not success:
            raise TimeoutException(f"새 대화 버튼을 찾을 수 없습니다")

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
            top = None
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
                if top is None:
                    # top 자체가 못 잡힌 경우 → 다시 루프
                    time.sleep(0.2)
                    continue

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
        """검색 버튼 클릭 (overlay 확인 포함)"""
        end = time.time() + 30  # 최대 30초 시도
        last_error = None
        
        while time.time() < end:
            success = False
            
            # 1차 시도: 텍스트 기반 버튼
            try:
                self.click_safely("sidebar_search_btn", timeout=3)
                success = True
            except TimeoutException:
                pass

            # 2차 시도: 아이콘 → 부모 div[role='button']
            if not success:
                try:
                    icon = self.present("sidebar_search_icon", sec=3)
                    btn = icon.find_element(By.XPATH, "./ancestor::div[@role='button'][1]")
                    self.scroll_center(btn)
                    self.js_click(btn)
                    success = True
                except Exception:
                    pass

            # 3차 시도: 모든 span 중 '검색' 텍스트 찾기
            if not success:
                try:
                    spans = self.driver.find_elements(By.XPATH, "//aside//span")
                    for span in spans:
                        try:
                            text = span.text.strip()
                            if text in ['검색', 'Search']:
                                btn = span.find_element(By.XPATH, "ancestor::div[@role='button'][1]")
                                self.js_click(btn)
                                success = True
                                break
                        except:
                            continue
                except Exception:
                    pass

            # 4차 시도: JavaScript로 검색
            if not success:
                try:
                    self.driver.execute_script("""
                        const spans = Array.from(document.querySelectorAll('span'));
                        const target = spans.find(s => s.textContent.trim() === '검색' || s.textContent.trim() === 'Search');
                        if (target) {
                            let btn = target.closest('[role="button"]');
                            if (btn) btn.click();
                        }
                    """)
                    success = True
                except Exception as e:
                    last_error = e
                    pass
            
            if success:
                # 검색 overlay가 실제로 나타났는지 확인
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[cmdk-input]"))
                    )
                    # overlay가 나타났으면 성공!
                    return
                except TimeoutException:
                    # overlay가 안 나타났으면 다시 시도
                    time.sleep(1)
                    continue
            
            # 클릭 자체에 실패했으면 잠시 대기 후 재시도
            time.sleep(0.5)
        
        raise TimeoutException(f"검색 overlay를 열 수 없습니다 (30초 타임아웃). 마지막 에러: {last_error}")

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
        # BasePage.__init__ 사용
        super().__init__(driver)

    # --- BasePage.get_element를 감싸는 헬퍼들 ---
    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    def clickable(self, key, sec=10):
        return self.get_element(key, wait_type="clickable", timeout=sec)

    # --- 1) Composer 준비 대기 ---
    def wait_ready(self, sec=None):
        # 처음 준비 + 응답 끝난 뒤 “다시” 준비 둘 다 여기로
        self.visible("textarea", sec or 10)

    # --- 2) 메시지 전송 ---
    def send(self, text: str):
        ta = self.clickable("textarea", sec=10)
        try:
            ta.click()
            ta.send_keys(text)
        except Exception:
            self.driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                ta,
                text,
            )

        # submit 버튼 클릭 (명시적 대위 후 클릭)
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(self.locators["submit_enabled"])
        ).click()
        
        # Docker 헤드리스 환경에서 안정성 향상
        time.sleep(1)  # 메시지 전송 후 1초 대기
        
        # textarea가 다시 활성화될 때까지 대기 (응답 완료 신호)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.locators["textarea"])
            )
        except:
            pass
  



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
        # BasePage.__init__ 사용
        super().__init__(driver)

    # --- BasePage.get_element를 감싸는 헬퍼 ---
    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    def js_click(self, el):
        self.driver.execute_script("arguments[0].click();", el)

    def confirm_delete(self):
        # 1) 다이얼로그가 떠 있을 때까지 대기
        dlg = self.visible("dialog", sec=10)

        # 2) 버튼 찾기 (텍스트 기반 → 에러 버튼 스타일 기반 폴백)
        try:
            btn = dlg.find_element(*self.locators["dialog_delete_btn"])
        except NoSuchElementException:
            btn = dlg.find_element(*self.locators["dialog_delete_btn_fallback"])

        # 3) 클릭 가능해질 때까지 대기 후 클릭 (안 되면 JS 클릭)
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: btn.is_enabled() and btn.is_displayed()
            )
            btn.click()
        except Exception:
            self.js_click(btn)

        # 4) 다이얼로그가 실제로 닫힐 때까지 대기
        dialog_locator = self.locators["dialog"]

        def _dialog_closed(drv):
            try:
                el = drv.find_element(*dialog_locator)
                return not el.is_displayed()
            except (NoSuchElementException, StaleElementReferenceException):
                # 못 찾거나 stale이면 이미 닫힌 것으로 간주
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
        # BasePage.__init__ 사용
        super().__init__(driver)

    # --- BasePage.get_element를 감싸는 헬퍼 ---
    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    def js_click(self, el):
        self.driver.execute_script("arguments[0].click();", el)

    # --- 검색어 입력 ---
    def type_query(self, text, sec=10):
        """검색어 입력 (overlay 확인 포함)"""
        # 먼저 overlay가 나타났는지 확인 대기
        WebDriverWait(self.driver, sec).until(
            EC.presence_of_element_located(self.locators["search_input_strict"])
        )
        
        # input 찾기 (더 긴 timeout)
        inp = self.visible("search_input_strict", sec=sec)
        time.sleep(0.5)

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
        # BasePage.__init__ 사용
        super().__init__(driver)

    # --- BasePage.get_element 얇은 래퍼 ---
    def clickable(self, key, sec=10):
        return self.get_element(key, wait_type="clickable", timeout=sec)

    def visible(self, key, sec=10):
        return self.get_element(key, wait_type="visible", timeout=sec)

    # --- 1) 에이전트 탐색 페이지 열기 ---
    def open(self):
        self.clickable("agent_explorer_link", sec=10).click()
        WebDriverWait(self.driver, 10).until(
            lambda d: "/ai-helpy-chat/agent" in d.current_url
        )

    # --- 2) 검색 입력 ---
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

        WebDriverWait(self.driver, 5).until(
            lambda d: (inp.get_attribute("value") or "") == text
        )

    # --- 3) 결과 타이틀 검증 ---
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
