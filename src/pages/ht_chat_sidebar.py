from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from .ht_base_page import BasePage
import time


SEL_NEW_CHAT_BTN = (
    By.XPATH, "//aside//div[@role='button'][.//span[normalize-space()='새 대화'] or .//span[normalize-space()='New chat']]"
)
SEL_TOP_THREAD          = (By.CSS_SELECTOR, "aside a[href^='/ai-helpy-chat/thread/'][data-index='0']")
SEL_TOP_THREAD_MENU_BTN = (By.CSS_SELECTOR, "aside a[href^='/ai-helpy-chat/thread/'][data-index='0'] .menu-button button")
SEL_MENU_UL             = (By.CSS_SELECTOR, "ul.MuiMenu-list[role='menu']")
XPATH_MENU_RENAME       = ".//li[.//*[normalize-space()='이름 변경'] or .//*[normalize-space()='Rename']]"
XPATH_MENU_DELETE       = ".//li[.//*[normalize-space()='삭제'] or .//*[normalize-space()='Delete']]"
CSS_MENU_TRASH_ICON     = "li svg[data-icon='trash']"
SEL_SECOND_THREAD       = (By.CSS_SELECTOR, "aside a[href^='/ai-helpy-chat/thread/'][data-index='1']")

# 검색 버튼
SEL_SIDEBAR_SEARCH_BTN = (
    By.XPATH,
    "//aside//div[@role='button'][.//span[normalize-space()='검색'] or .//span[normalize-space()='Search']]"
)

class ChatSidebar(BasePage):
    def click_new_chat(self):
        self.clickable(SEL_NEW_CHAT_BTN).click()

    def top_thread_href(self):
        try:
            el = self.present(SEL_TOP_THREAD, sec=3)
            return el.get_attribute("href")
        except TimeoutException:
            return None

    def top_thread_title(self):
        top = self.visible(SEL_TOP_THREAD, sec=10)
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
                top = self.present(SEL_TOP_THREAD, sec=5)
                self.scroll_center(top)

                # 2) hover 한번 해주고
                ActionChains(self.drv).move_to_element(top).pause(0.2).perform()

                # 3) 그 순간의 메뉴 버튼을 가져와서 클릭
                btn = self.clickable(SEL_TOP_THREAD_MENU_BTN, sec=5)
                btn.click()
                return  # 성공하면 바로 종료

            except StaleElementReferenceException as e:
                # top이나 btn이 리렌더 중이면 여기로 옴 → 잠깐 쉬고 다시 시도
                last_exc = e
                time.sleep(0.2)

            except TimeoutException as e:
                # hover 인식 실패 시 기존처럼 폴백 한번 더 시도
                last_exc = e
                try:
                    self.drv.execute_script("""
                        const el = arguments[0];
                        el.dispatchEvent(new MouseEvent('mouseover',{bubbles:true}));
                        el.dispatchEvent(new MouseEvent('mouseenter',{bubbles:true}));
                        el.dispatchEvent(new MouseEvent('mousemove',{bubbles:true}));
                    """, top)
                    btn = self.present(SEL_TOP_THREAD_MENU_BTN, sec=5)
                    self.js_click(btn)
                    return
                except StaleElementReferenceException as e2:
                    last_exc = e2
                    time.sleep(0.2)

        # 여기까지 오면 여러 번 시도해도 실패한 것
        raise last_exc or TimeoutException("최상단 쓰레드 옵션 메뉴 버튼 클릭 실패")

    def click_menu_rename(self):
        menu = self.visible(SEL_MENU_UL, sec=5)
        try:
            item = menu.find_element(By.XPATH, XPATH_MENU_RENAME)
        except NoSuchElementException:
            # 펜 아이콘 폴백
            try:
                pen = menu.find_element(By.CSS_SELECTOR, "li svg[data-icon='pen']")
                item = pen.find_element(By.XPATH, "./ancestor::li[1]")
            except Exception:
                raise AssertionError("메뉴에 '이름 변경'이 없습니다.")
        self.scroll_center(item)
        try:
            self.clickable((By.XPATH, XPATH_MENU_RENAME), sec=5)
            item.click()
        except TimeoutException:
            self.js_click(item)

    def click_menu_delete(self):
        menu = self.visible(SEL_MENU_UL, sec=5)
        try:
            item = menu.find_element(By.XPATH, XPATH_MENU_DELETE)
        except NoSuchElementException:
            try:
                icon = menu.find_element(By.CSS_SELECTOR, CSS_MENU_TRASH_ICON)
                item = icon.find_element(By.XPATH, "./ancestor::li[1]")
            except Exception:
                raise AssertionError("메뉴에 '삭제'가 없습니다.")
        self.scroll_center(item)
        try:
            self.clickable((By.XPATH, XPATH_MENU_DELETE), sec=5)
            item.click()
        except TimeoutException:
            self.js_click(item)

    def click_search_button(self):
        try:
            self.clickable(SEL_SIDEBAR_SEARCH_BTN, sec=5).click()
            return
        except TimeoutException:
            pass
        # 아이콘 폴백
        icon = self.present((By.CSS_SELECTOR, "aside svg[data-testid='magnifying-glassIcon']"), sec=5)
        btn = icon.find_element(By.XPATH, "./ancestor::div[@role='button'][1]")
        self.scroll_center(btn)
        try:
            self.clickable(btn, sec=2)  # type: ignore
            btn.click()
        except Exception:
            self.js_click(btn)

    def click_second_thread(self):
        self.clickable(SEL_SECOND_THREAD).click()
