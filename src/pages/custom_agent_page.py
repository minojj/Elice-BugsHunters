from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import platform
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage




class AgentExplorerPage(BasePage):

    locators = {
        "agent_explorer_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]'),
        "create_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]'),
        "all_agent_cards": (By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/agent/']"),
        "fixed_target_card": (By.CSS_SELECTOR, 'a[href*="8f701da7-7c53-4f54-b26d-b6eeb39a4479"]'),
        "menu_btn_in_card": (By.CSS_SELECTOR, "button[aria-label='menu']"),
        "delete_icon": (By.CSS_SELECTOR, "svg[data-icon='trash']"),
        }

    def __init__(self, driver):
        super().__init__(driver)   
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"


 

    def click_agent_card_by_id(self, agent_id, timeout=15):
        wait = WebDriverWait(self.driver, timeout)
        locator = self.locators["all_agent_cards"]

        patterns = [
            f'a[href="/ai-helpy-chat/agent/{agent_id}"]',
            f'a[href$="/{agent_id}"]',
            f'a[href*="/agent/{agent_id}"]',
        ]


        def find_card():
            for css in patterns:
                elements = self.driver.find_elements(By.CSS_SELECTOR, css)
                if elements:
                    return elements[0]
            return None

        card = None
        prev_count = -1

        while not card:
            card = find_card()
            if card:
                break

            cards = self.driver.find_elements(*locator)
            count = len(cards)

            if count == prev_count:
                break
            prev_count = count


            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )


            try:
                wait.until(lambda d: len(d.find_elements(*locator)) > count)
            except:
                break

        if not card:
            return []

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", card
        )

        wait.until(lambda d: card.is_displayed() and card.is_enabled())
        self.driver.execute_script("arguments[0].click();", card)

        return [card]



 
    def open_card_menu(self, card, timeout=8):
        wait = WebDriverWait(self.driver, timeout)

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            card
        )

        menu_btn = card.find_element(*self.locators["menu_btn_in_card"])

        self.driver.execute_script("""
            arguments[0].style.display='flex';
            arguments[0].style.opacity='1';
            arguments[0].style.visibility='visible';
        """, menu_btn)

        wait.until(lambda d: menu_btn.is_displayed())
        self.driver.execute_script("arguments[0].click();", menu_btn)

        return True




    def delete_fixed_agent(self, my_agents_page, save_page):
        wait = WebDriverWait(self.driver, 15)
        short_wait = WebDriverWait(self.driver, 5)

        try:
            wait.until(
                EC.presence_of_element_located(self.locators["fixed_target_card"])
            )
        except TimeoutException:
            print("❌ 타겟 카드 미발견")
            return False

        card = self.driver.find_element(*self.locators["fixed_target_card"])


        if not self.open_card_menu(card):
            print("❌ 메뉴 열기 실패")
            return False

        try:
            delete_icon = short_wait.until(
                EC.presence_of_element_located(self.locators["delete_icon"])
            )
            delete_btn = delete_icon.find_element(
                By.XPATH, "./ancestor::*[self::button or self::li][1]"
            )
            self.driver.execute_script("arguments[0].click();", delete_btn)
        except TimeoutException:
            return True


        try:
            modal_delete_btn = short_wait.until(
                EC.element_to_be_clickable(
                    my_agents_page.locators["confirm_delete_modal_btn"]
                )
            )

            if not modal_delete_btn.is_enabled():
                return True

            modal_delete_btn.click()

            snackbar = wait.until(
                EC.visibility_of_element_located(
                    save_page.locators["success_alert"]
                )
            )
            msg = snackbar.text.lower()

        except TimeoutException:
            return True

        if any(k in msg for k in ["error", "권한", "cannot", "failed"]):
            return True
        print("❌ 기본제공 에이전트가 실제로 삭제됨 → 실패")
        return False
    





class CreateAgentPage(BasePage):

    locators = {

        "name": (By.NAME, "name"),
        "description": (By.CSS_SELECTOR, 'input[name="description"]'),
        "rules": (By.NAME, "systemPrompt"),
        "conversation": (By.NAME, "conversationStarters.0.value"),

        "create_btn": (By.CSS_SELECTOR, "button.MuiButton-containedPrimary"),

        "file_input": (By.CSS_SELECTOR, "input.css-1bgri6b"),
        "file_item": (By.CSS_SELECTOR, "div.css-8e3ts2 > div.MuiStack-root.css-1lawy5a"),
        "file_success_icon": (By.CSS_SELECTOR, "div.css-tza19w svg.MuiSvgIcon-colorSuccess"),
        "file_failed_icon": (By.CSS_SELECTOR, "div.css-tza19w svg.MuiSvgIcon-colorError"),
        "file_status": (By.CSS_SELECTOR, "span.MuiTypography-caption"),
        "file_error_msg": (By.CSS_SELECTOR, "p.MuiTypography-body2.css-wrn3u"),

        "autosave_saved_badge": (By.CSS_SELECTOR, "span.MuiTypography-caption.css-10z10oy"),
        "autosave_check_icon": (By.CSS_SELECTOR, "svg[data-icon='circle-check']"),
        "top_title_text": (By.CSS_SELECTOR, "p.MuiTypography-body2"),
        }


    def __init__(self, driver):
        super().__init__(driver)   
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"



    def open(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )



    def fill_form(self, name, description, rules, conversation):

        self.get_element("name").send_keys(name)
        self.get_element("description", "clickable").send_keys(description)
        self.get_element("rules").send_keys(rules)

        conv = self.get_element("conversation")
        conv.send_keys(conversation)
        conv.send_keys(Keys.TAB)

        return {
            "name": name,
            "description": description,
            "rules": rules,
            "conversation": conversation
        }


    def fill_form_with_trigger(self, name, description, rules, conversation):

        modifier = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

        def type_and_trigger(key, value):
            el = self.get_element(key, "visible")

            el.click()
            el.send_keys(modifier + "a")
            el.send_keys(Keys.DELETE)

            if value:
                el.send_keys(value)
            else:
                el.send_keys(" ")
                el.send_keys(Keys.BACKSPACE)

            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", el
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", el
            )

            el.send_keys(Keys.TAB)
            self.driver.execute_script("arguments[0].blur();", el)

        type_and_trigger("name", name)
        type_and_trigger("description", description)
        type_and_trigger("rules", rules)
        type_and_trigger("conversation", conversation)

        return {
            "name": name,
            "description": description,
            "rules": rules,
            "conversation": conversation
        }


 
    def get_field_value(self, field):
        return self.get_element(field).get_attribute("value")


    def get_all_field_values(self):
        return {
            "name": self.get_field_value("name"),
            "description": self.get_field_value("description"),
            "rules": self.get_field_value("rules"),
            "conversation": self.get_field_value("conversation")
        }



    def wait_for_autosave(self, expected, timeout=20):

        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.3)
        wait.until(EC.presence_of_element_located((By.NAME, "name")))

        wait.until(
            lambda d: d.find_element(By.NAME, "name").get_attribute("value") == expected["name"]
        )

        try:
            wait.until(
                lambda d: d.find_element(*self.locators["top_title_text"]).text.strip()
                == expected["name"]
            )
        except:
            pass
        try:
            wait.until(
                EC.visibility_of_element_located(self.locators["autosave_saved_badge"])
            )
            wait.until(
                EC.visibility_of_element_located(self.locators["autosave_check_icon"])
            )
        except:
            pass



    def get_agent_id_from_url(self):
        url = self.driver.current_url
        try:
            return url.split("/agent/")[1].split("/")[0]
        except:
            raise AssertionError(f"URL에서 agent ID 추출 실패: {url}")



    def upload_file(self, filepath):
        file_input = self.get_element("file_input", "presence")
        self.driver.execute_script("arguments[0].style.display='block';", file_input)
        file_input.send_keys(filepath)


    def get_last_uploaded_item(self, timeout=10):

        wait = WebDriverWait(self.driver, timeout)

        wait.until(
            lambda d: len(d.find_elements(*self.locators["file_item"])) > 0
        )

        return self.driver.find_elements(*self.locators["file_item"])[-1]


    def get_file_status(self, file_item):
        return file_item.find_element(*self.locators["file_status"]).text.strip()


    def has_success_icon(self, file_item, timeout=15):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: file_item.find_elements(*self.locators["file_success_icon"])
                or "success" in self.get_file_status(file_item).lower()
            )
            return True
        except:
            return False


    def has_failed_icon(self, file_item, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: file_item.find_elements(*self.locators["file_failed_icon"])
            )
            return True
        except:
            return False


    def get_error_msg(self, file_item):
        els = file_item.find_elements(*self.locators["file_error_msg"])
        return els[0].text.strip() if els else None


    def wait_for_new_upload_item(self, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        old = len(self.driver.find_elements(*self.locators["file_item"]))

        wait.until(
            lambda d: len(d.find_elements(*self.locators["file_item"])) > old
        )

        return self.driver.find_elements(*self.locators["file_item"])[-1]


    def wait_for_status(self, file_item, expected, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: expected in self.get_file_status(file_item).lower()
            )
            return True
        except:
            return False


    def wait_for_error_msg(self, file_item, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(
            lambda d: file_item.find_element(*self.locators["file_error_msg"]).text.strip()
        )




   
    

class SaveAgentPage(BasePage):

    locators = {
        "private_radio": (By.CSS_SELECTOR, "input[value='private']"),
        "organization_radio": (By.CSS_SELECTOR, "input[value='organization']"),
        "save_btn": (By.CSS_SELECTOR, "button[type='submit'][form='publish-setting-form']"),
        "success_alert": (By.CSS_SELECTOR, "div#notistack-snackbar"),
        "start_chat_btn": (By.CSS_SELECTOR, "div#notistack-snackbar button[type='button']"),
        "chat_input": (By.CSS_SELECTOR, "textarea[name='input']"),
        }

    def __init__(self, driver):
        super().__init__(driver)



    def select_mode(self, mode):
        key = f"{mode}_radio"

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-paper"))
        )

        radio = self.get_element(key, wait_type="presence")
        if radio.is_selected():
            return

        radio_id = radio.get_attribute("id")
        label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
        self.driver.execute_script("arguments[0].click();", label)

        assert radio.is_selected(), f"{mode} 옵션이 선택되지 않았습니다."

 
    def click_save(self):
        self.click_safely("save_btn")


    def click_start_chat_fast(self):
        btn = self.get_element("start_chat_btn", wait_type="presence", timeout=3)
        self.driver.execute_script("arguments[0].click();", btn)


    def get_snackbar_text(self):
        alert = self.get_element("success_alert", wait_type="visible")
        text = alert.text.strip() or alert.get_attribute("innerText").strip()
        return text


    
class ChatCreatePage(BasePage):

    locators = {
        "create_with_chat_btn": (By.CSS_SELECTOR, "button[type='button'][value='chat']"),
        "create_chat_input": (By.CSS_SELECTOR, "textarea[name='input']"),
        "send_btn": (By.CSS_SELECTOR, "button[aria-label='Send']"),
        "running_status": (By.CSS_SELECTOR, "div[data-status='running']"),
        "complete_msg": (By.CSS_SELECTOR, "div.aichatkit-md[data-status='complete'] p"),
        }

    def __init__(self, driver):
        super().__init__(driver)


    def click_create_with_chat(self):
        self.click_safely("create_with_chat_btn")


    def send_single_message(self):

        chat_box = self.get_element("create_chat_input", wait_type="clickable")

        self.driver.execute_script("arguments[0].focus();", chat_box)
        chat_box.click()

        modifier = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

        chat_box.send_keys(modifier + "a")
        chat_box.send_keys(Keys.DELETE)

        chat_box.send_keys(self.step1_text())

        send_btn = self.get_element("send_btn", wait_type="clickable", timeout=20)
        self.driver.execute_script("arguments[0].click();", send_btn)

        WebDriverWait(self.driver, 60).until(
            lambda d: len(d.find_elements(*self.locators["running_status"])) == 0
        )

        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located(self.locators["complete_msg"])
        )




    def step1_text(self):
        return (
            'I want to create "경제 스토리텔러, 팀03" '
            '(Economics Storyteller, Team03), who breaks down difficult '
            'economic news and concepts into easy and fun stories. '
            "Character "
            "This agent acts like a knowledgeable older peer from a university club or a close friend. "
            "Named 'Team03', it is a storyteller who explains economic principles using relatable analogies "
            "from our daily lives or interesting real-life incidents, instead of using complex jargon or dry graphs. "
            "The main goal is to show how fun it can be to understand the flow of 'money'. "
            "Skills "
            "Translating Concepts into Stories: It explains difficult economic terms like 'inflation', 'interest rates', "
            "and 'quantitative easing' by turning them into everyday stories. "
            "Explaining Recent Economic News: It takes recent news and explains how these might affect our daily lives "
            "in a chatty, friendly manner. "
            "Storytelling of Historical Economic Events: It recounts events like the 1997 IMF crisis or the 2008 crisis "
            "as compelling stories rather than dry facts. "
            "Constraints "
            "No Investment Advice. "
            "No Personal Financial Guidance. "
            "No Predictions. "
        )



    def wait_for_ai_answer(self, timeout=30):
        wait = WebDriverWait(self.driver, timeout)

        def _answer_rendered(_):
            selectors = [
                "ul[class^='css-'][class*='e1ge9pxx'] li",
                "ol[class^='css-'][class*='e1ge9pxx'] li",
                "pre[class^='css-'] code",
                "div.aichatkit-md[data-status='complete']"
            ]
            for sel in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if any(el.text.strip() for el in elements):
                    return True
            return False

        wait.until(_answer_rendered)
        return True




    


class MyAgentsPage(BasePage):
    locators = {
        "my_agents_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/mine"]'),
        "all_agent_cards": (By.CSS_SELECTOR, "div.MuiGrid-item"),
        "draft_chip": (By.CSS_SELECTOR, ".MuiChip-label"),
        "private_icon": (By.CSS_SELECTOR, "svg[data-icon='lock']"),
        "organization_icon": (By.CSS_SELECTOR, "svg[data-icon='buildings']"),
        "edit_icon": (By.CSS_SELECTOR, "svg[data-icon='pen']"),
        "delete_icon": (By.CSS_SELECTOR, "svg[data-icon='trash']"),
        "confirm_delete_modal_btn": (By.CSS_SELECTOR, "button.MuiButton-containedError"),
        "cancel_delete_modal_btn": (By.CSS_SELECTOR, "button.MuiButton-containedInherit"),
        }

    def __init__(self, driver):
        super().__init__(driver)   
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent/mine"

    def get_all_cards(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located(self.locators["all_agent_cards"])
        )

        previous = -1
        for _ in range(10):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            cards = self.driver.find_elements(*self.locators["all_agent_cards"])
            if len(cards) == previous:
                break
            previous = len(cards)

        return cards

    def load_all_cards(self, timeout=10):
 
        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.1)
        last_count = -1

        while True:
            cards = self.driver.find_elements(*self.locators["all_agent_cards"])
            current_count = len(cards)

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                wait.until(
                    lambda d: len(d.find_elements(*self.locators["all_agent_cards"])) > current_count
                )
            except Exception:
                break

            if current_count == last_count:
                break

            last_count = current_count

        self.driver.execute_script("window.scrollTo(0, 0);")



    def scroll_into_view(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )

    def get_draft_cards(self):
        cards = self.get_all_cards()
        result = []
        for card in cards:
            chips = card.find_elements(By.CSS_SELECTOR, ".MuiChip-label")
            for chip in chips:
                if chip.text.strip().lower() == "draft":
                    result.append(card)
                    break
        return result

    def get_agent_id_from_card(self, card):
        link = card.find_element(
            By.CSS_SELECTOR,
            "a[href*='/ai-helpy-chat/agent/'], a[href*='/agent/']"
        )
        href = link.get_attribute("href")

        if not href:
            raise ValueError(f"에이전트 href를 찾지 못했습니다.\ncard text: {card.text}")

        agent_id = href.rstrip("/").split("/")[-2]
        return agent_id

    def wait_for_cards_loaded(self, timeout=10):
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.MuiGrid-item")
                )
            )
            return True
        except Exception:
            return False

    def wait_for_card_update(self, agent_id, updated_title, timeout=20):
        wait = WebDriverWait(self.driver, timeout)

        for _ in range(timeout * 2):
            self.driver.get(self.url)

            wait.until(
                EC.presence_of_all_elements_located(self.locators["all_agent_cards"])
            )

            card = self.find_card_by_agent_id(agent_id)
            if not card:
                continue

            try:
                title_el = card.find_element(
                    By.CSS_SELECTOR,
                    "p.MuiTypography-body1.MuiTypography-noWrap"
                )
                if title_el.text.strip() == updated_title:
                    return card

            except Exception:
                pass

        raise AssertionError(
            f"❌ 카드(ID={agent_id}) 제목 '{updated_title}' 로 갱신되지 않음"
        )

    def find_card_by_agent_id(self, agent_id, timeout=10):
        wait = WebDriverWait(self.driver, timeout)

        for _ in range(timeout):
            cards = self.get_all_cards()

            for card in cards:
                try:
                    link = card.find_element(
                        By.CSS_SELECTOR,
                        "a[href*='/ai-helpy-chat/agent/'], a[href*='/agent/']"
                    )
                    href = link.get_attribute("href") or ""
                    if agent_id in href:
                        return card
                except Exception:
                    continue

        return None

    def get_private_cards(self):
        cards = self.get_all_cards()
        result = []
        for card in cards:
            try:
                card.find_element(*self.locators["private_icon"])
                result.append(card)
            except Exception:
                continue
        return result

    def get_organization_cards(self):
        cards = self.get_all_cards()
        result = []
        for card in cards:
            try:
                card.find_element(*self.locators["organization_icon"])
                result.append(card)
            except Exception:
                continue
        return result

    def _get_cards_by_type(self, card_type):
        if card_type == "draft":
            return self.get_draft_cards()
        elif card_type == "private":
            return self.get_private_cards()
        elif card_type == "organization":
            return self.get_organization_cards()
        else:
            raise ValueError(f"Invalid card_type: {card_type}")

    def is_card_visible(self, card):
        return card.is_displayed()

    def get_card_count(self, card_type):
        mapping = {
            "draft": self.get_draft_cards(),
            "private": self.get_private_cards(),
            "organization": self.get_organization_cards()
        }
        return len(mapping.get(card_type, []))

    def has_cards(self, card_type, minimum=1):
        return self.get_card_count(card_type) >= minimum

    def _find_button_in_card(self, card, icon_locator):
        buttons = card.find_elements(By.CSS_SELECTOR, "button")
        for btn in buttons:
            try:
                btn.find_element(*icon_locator)
                return btn
            except Exception:
                continue
        return None

    def click_edit_button_by_card_type(self, card_type, index=0):
        cards = self._get_cards_by_type(card_type)

        if len(cards) <= index:
            raise IndexError(f"{card_type} 카드가 {index + 1}개 미만입니다.")

        card = cards[index]
        self.scroll_into_view(card)

        edit_btn = self._find_button_in_card(card, self.locators["edit_icon"])
        if not edit_btn:
            raise NoSuchElementException(
                f"{card_type} 카드에서 Edit 버튼을 찾지 못했습니다."
            )

        WebDriverWait(self.driver, 10).until(
            lambda d: edit_btn.is_enabled() and edit_btn.is_displayed()
        )
        self.driver.execute_script("arguments[0].click();", edit_btn)

    def click_delete_button_by_card_type(self, card_type, index=0):
        cards = self._get_cards_by_type(card_type)

        if len(cards) <= index:
            raise IndexError(f"{card_type} 카드가 {index + 1}개 미만입니다.")

        card = cards[index]
        self.scroll_into_view(card)

        delete_btn = self._find_button_in_card(card, self.locators["delete_icon"])
        if not delete_btn:
            raise NoSuchElementException(
                f"{card_type} 카드에서 Delete 버튼을 찾지 못했습니다."
            )

        WebDriverWait(self.driver, 10).until(
            lambda d: delete_btn.is_enabled() and delete_btn.is_displayed()
        )
        self.driver.execute_script("arguments[0].click();", delete_btn)

    def confirm_delete_modal(self):
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.locators["confirm_delete_modal_btn"])
        )
        btn.click()

    def cancel_delete_modal(self):
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.locators["cancel_delete_modal_btn"])
        )
        btn.click()

        WebDriverWait(self.driver, 5, 0.1).until(
            EC.invisibility_of_element_located(
                self.locators["confirm_delete_modal_btn"]
            )
        )

    def is_delete_modal_visible(self, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(
                    self.locators["confirm_delete_modal_btn"]
                )
            )
            return True
        except TimeoutException:
            return False