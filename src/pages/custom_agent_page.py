from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.chrome.service import Service
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# StaleElementReferenceException,
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# from src.utils.helpers import Utils



class AgentExplorerPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"
        self.locators = {
            "agent_explorer_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]'),
            "create_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]'),
            "agent_card_title": (By.CSS_SELECTOR, "p.MuiTypography-body1.MuiTypography-noWrap"),
            "agent_card": (By.CSS_SELECTOR, "a.MuiCard-root, a[class*='MuiCard'], a[href*='/agent/']"),
            "agent_chat_input": (By.CSS_SELECTOR, "textarea[placeholder='Ask anything']"),
            "search_input": (By.CSS_SELECTOR, "input[placeholder='Search AI agents']"),
            "search_agent_card_spans": (By.CSS_SELECTOR, "span.MuiTypography-root"),
        }


    def get_element(self, key, wait_type="visible", timeout=10):
        """요소 키워드(agent_explorer_btn, create_btn 등)를 받아 element 반환"""
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)
    
    def get_elements(self, key, timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)
    
    def navigate_to_agent_explorer(self, timeout=10, force_refresh=False):
        current_url = self.driver.current_url
        self.get_element("agent_explorer_btn", wait_type="presence").click()
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.url_changes(current_url))

        if force_refresh:
            self.driver.refresh()
        
        wait.until(EC.presence_of_all_elements_located(self.locators["agent_card_title"]))

    def click_agent_card_by_id(self, agent_id):

        cards_locator = (By.CSS_SELECTOR, ".MuiCard-root")
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(*cards_locator)) > 0
            )
        except TimeoutException:
            print("⚠️ 카드 리스트 미노출")
            return []
        
        patterns = [
            f'a[href="/ai-helpy-chat/agent/{agent_id}"]',
            f'a[href$="/{agent_id}"]',
            f'a[href*="{agent_id}"]',
            f'a[href*="/agent/{agent_id}"]',
        ]

        card = None
        for css in patterns:
            elements = self.driver.find_elements(By.CSS_SELECTOR, css)
            if elements:
                card = elements[0]
                break

        if not card:
            print(f"⚠️ 에이전트 카드 미노출 (ID: {agent_id})")
            return []

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        WebDriverWait(self.driver, 5).until(lambda d: card.is_displayed())

        if EC.element_to_be_clickable(card)(self.driver):
            card.click()
            print(f"✅ 에이전트 카드 클릭 완료 (ID: {agent_id})")
            return [card]

        print(f"⚠️ 카드가 클릭 불가능한 상태입니다. (ID: {agent_id})")
        return []






class CreateAgentPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"
        self.locators = {
            "name": (By.NAME, "name"),
            "description": (By.CSS_SELECTOR, 'input[name="description"]'),
            "rules": (By.NAME, "systemPrompt"),
            "conversation": (By.NAME, "conversationStarters.0.value"),
            "create_btn": (By.CSS_SELECTOR, "button.MuiButton-containedPrimary"), # Create/Publish 공용 버튼
        }

    def open(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 커스텀 에이전트 메인 페이지 접속 성공")

    def get_element(self, key, wait_type="visible", timeout=10):
        #요소 키워드(name, description 등)를 받아 element 반환
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)

    def fill_form(self, name, description, rules, conversation):
        self.get_element("name").send_keys(name)
        self.get_element("description", "clickable").send_keys(description)
        self.get_element("rules").send_keys(rules)
        self.get_element("conversation").send_keys(conversation)
        self.last_agent_name = name  
        return {
        "name": name,
        "description": description,
        "rules": rules,
        "conversation": conversation
        }
    
    def get_field_value(self, field_name):
        return self.get_element(field_name).get_attribute("value")


    def get_all_field_values(self):
        return {
            "name": self.get_field_value("name"),
            "description": self.get_field_value("description"),
            "rules": self.get_field_value("rules"),
            "conversation": self.get_field_value("conversation")
        }


    def get_agent_id_from_url(self):
        """현재 페이지의 URL에서 agent UUID 추출"""
        current_url = self.driver.current_url
        try:
            agent_id = current_url.split("/agent/")[1].split("/")[0]
            print(f"🆔 생성된 agent ID: {agent_id}")
            return agent_id
        except IndexError:
            raise AssertionError(f"❌ URL에서 agent ID 추출 실패 (현재 URL: {current_url})")

   
    

class SaveAgentPage:
    def __init__(self, driver):
        self.driver = driver
        self.locators = {
            "private_radio": (By.CSS_SELECTOR, "input[value='private']"),
            "organization_radio": (By.CSS_SELECTOR, "input[value='organization']"),
            "save_btn": (By.CSS_SELECTOR, "button[type='submit'][form='publish-setting-form']"),
            "success_alert": (By.CSS_SELECTOR, "div#notistack-snackbar"),
            "start_chat_btn": (By.CSS_SELECTOR, "div#notistack-snackbar button[type='button']"),
            "chat_input": (By.CSS_SELECTOR, "textarea[name='input']")
        }

    def select_mode(self, mode):
        key = f"{mode}_radio"

        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-paper")))

        radio = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.locators[key]))
        if not radio.is_selected():
            clickable_radio = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio.get_attribute('id')}']")
            self.driver.execute_script("arguments[0].click();", clickable_radio)
        check_radio = self.driver.find_element(*self.locators[key])
        assert check_radio.is_selected(), f"{mode} 옵션이 선택되지 않았습니다."


    def click_save(self):
        save_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.locators["save_btn"]))
        save_btn.click()

    def click_start_chat_fast(self):
        btn = WebDriverWait(self.driver, 2, poll_frequency=0.1).until(EC.presence_of_element_located(self.locators["start_chat_btn"]))
        self.driver.execute_script("arguments[0].click();", btn)


    def verify_success(self):
        alert = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.locators["success_alert"]))
        assert "The agent has been created" in alert.text, "❌ 에이전트 생성 실패"
        print("✅ 에이전트 생성 성공!")

    def get_snackbar_text(self):
        alert = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.locators["success_alert"]))
        # .text 대신 innerText로 백업 (MUI 포털 대응)
        text = alert.text.strip() or alert.get_attribute("innerText").strip()
        return text
    

    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)
    


    
class ChatCreatePage:
    def __init__(self, driver):
        self.driver = driver
        self.locators = {
            "create_with_chat_btn": (By.CSS_SELECTOR, "button[type='button'][value='chat']"),
            "create_chat_input": (By.CSS_SELECTOR, "textarea[name='input']"),
            "info_list": (By.CSS_SELECTOR, "ul[class^='css-'][class*='e1ge9pxx'] li"),
            "conversation_list": (By.CSS_SELECTOR, "ol[class^='css-'][class*='e1ge9pxx'] li")
            }

    def click_create_with_chat(self):
        """'Create with Chat' 버튼 클릭 후 챗봇 대화 페이지로 진입"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.locators["create_with_chat_btn"])
        )
        self.driver.execute_script("arguments[0].click();", btn)
        print("✅ 'Create with Chat' 버튼 클릭 완료")


    def get_generated_info(self):

        info = {
            "Name": "",
            "Description": "",
            "System Prompt": "",
            "Conversation Starters": []
        }

        try:
            list_items = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[class^='css-'][class*='e1ge9pxx'] li")))

            for el in list_items:
                text = el.text.strip()
                if not text:
                    continue
                if text.startswith("Name:"):
                    info["Name"] = text.split(":", 1)[-1].strip()
                elif text.startswith("Description:"):
                    info["Description"] = text.split(":", 1)[-1].strip()
                elif "System Prompt" in text:
                    info["System Prompt"] = text.split(":", 1)[-1].strip()

            print("✅ Name/Description/System Prompt(텍스트형) 추출 완료.")
        except Exception:
            print("⚠️ Name/Description/System Prompt 리스트 추출 실패 (ul li 없음)")

     
        try:
            code_block = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "pre[class^='css-'] code")))
            code_text = code_block.text.strip()
            if code_text:
                info["System Prompt"] = code_text
                print("✅ System Prompt를 코드블록에서 추출했습니다.")
        except Exception:
            pass 

        try:
            conv_items = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ol[class^='css-'][class*='e1ge9pxx'] li")))
            info["Conversation Starters"] = [el.text.strip() for el in conv_items if el.text.strip()]
            print(f"✅ Conversation Starters {len(info['Conversation Starters'])}개 추출 완료.")
        except Exception:
            print("⚠️ Conversation Starters 추출 실패.")

        if not any(info.values()):
            print("❌ 생성정보 감지 실패")
        else:
            print("✅ 전체 생성 정보 추출 완료.")

        return info


    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.locators[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)
    
    
    def typing_chat(self):
    
        chat_box = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.locators["create_chat_input"]))

  
        self.driver.execute_script("arguments[0].focus();", chat_box)
        chat_box.click()

   
        def send_message(text):
       
            chat_box.clear()
            chat_box.send_keys(text)
            send_btn = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button'][aria-label='Send']:not([disabled])")))

            self.driver.execute_script("arguments[0].click();", send_btn)
            print(f"📨 메시지 전송 완료: {text[:50]}...")

            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.aichatkit-md[data-status='complete']")))

        send_message(self.step1_text())
        send_message(self.step2_text())
        send_message(self.step3_text())
        send_message(self.step4_text())

        print("✅ 모든 단계 메시지 전송 및 챗봇 응답 완료!")


    def step1_text(self):
        return (
            'I want to create "경제 스토리텔러, 팀03" (Economics Storyteller, Team03), '
            'who breaks down difficult economic news and concepts into easy and fun stories. '
            "Character "
            "This agent acts like a knowledgeable older peer from a university club or a close friend. "
            "Named 'Team03', it is a storyteller who explains economic principles using relatable analogies "
            "from our daily lives or interesting real-life incidents, instead of using complex jargon or dry graphs. "
            "The main goal is to show how fun it can be to understand the flow of 'money'. "
            "Skills "
            "Translating Concepts into Stories: It explains difficult economic terms like 'inflation', 'interest rates', "
            "and 'quantitative easing' by turning them into everyday stories, such as 'the reason why prices at the neighborhood bakery are going up' "
            "or 'why you get more interest when you save money in a bank'. "
            "Explaining Recent Economic News: It takes recent news, like the latest consumer price index or major stock market shifts, "
            "and explains how these might affect our daily lives in a chatty, friendly manner. For example, it might say, "
            "'Do you know why egg prices are so high lately? It's because the bird flu reduced the number of chickens, "
            "which means supply is down. That's the 'supply and demand' principle in action!' "
            "Storytelling of Historical Economic Events: It recounts historical events like the 1997 IMF financial crisis or the 2008 global financial crisis "
            "not as a boring list of facts, but as a compelling drama, complete with stories of the people involved, to make them easier to understand. "
            "Constraints "
            "No Investment Advice: It will absolutely not provide direct investment advice, such as 'buy this stock' or 'invest in this property'. "
            "All information is provided for educational purposes to broaden economic knowledge. "
            "Generality of Information: It does not offer advice tailored to an individual's personal financial situation. "
            "It only discusses general economic principles and facts that apply to everyone. "
            "Explanation, Not Prediction: It does not predict the future of the economy or guarantee the future value of specific assets. "
            "Its role is strictly to explain economic phenomena based on past and present data."
        )

    def step2_text(self):
        return (
            "Primarily, the tone should be casual and humorous, like a witty older sibling who's good at explaining things. "
            "However, when it discusses serious topics like an economic crisis, it should adopt a more empathetic and clear tone. "
            "The goal is to be engaging without making light of important subjects."
        )

    def step3_text(self):
        return (
            '"Heard the stock market went on a rollercoaster ride today? '
            'I can give you the simple, no-jargon explanation of what happened."'
        )

    def step4_text(self):
        return "No"
    

    def transfer_to_create_form(self):
        """Chat 생성 결과를 Create 페이지(Form)로 자동 전송"""
        # 1️⃣ 챗봇 생성 결과 가져오기
        info = self.get_generated_info()

        # 2️⃣ 'Form으로 이동' 버튼 클릭
        form_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button'][value='form']"))
        )
        form_btn.click()

        # 3️⃣ 폼 페이지 로딩 대기 (Name 필드 기준)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "name"))
        )

        # 4️⃣ CreateAgentPage 인스턴스 생성 후 자동 입력
        create_page = CreateAgentPage(self.driver)
        create_page.fill_form(
            name=info["Name"],
            description=info["Description"],
            rules=info["System Prompt"],
            conversation="\n".join(info["Conversation Starters"])
        )

        print("✅ Chat 생성 결과를 Create 페이지(Form)로 자동 전송 완료!")
    


class MyAgentsPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent/mine"
        self.locators = {
            "my_agents_btn" : (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/mine"]'),
            "all_agent_cards": (By.CSS_SELECTOR, "a.MuiCard-root"),
            "draft_chip": (By.CSS_SELECTOR, ".MuiChip-label"),
            "private_icon": (By.CSS_SELECTOR, "svg[data-icon='lock']"),
            "organization_icon": (By.CSS_SELECTOR, "svg[data-icon='buildings']"),
            "edit_button": (By.CSS_SELECTOR, "button svg[data-icon='pen']"),
            "delete_button": (By.CSS_SELECTOR, "button svg[data-icon='trash']"),
            "confirm_delete_modal_button": (By.CSS_SELECTOR, "button.MuiButton-containedError"),
            "cancel_delete_modal_button": (By.CSS_SELECTOR, "button.MuiButton-containedInherit")
        }
    
    def click_my_agents_button(self):
        my_agents_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.locators["my_agents_btn"]))
        my_agents_btn.click()

    def get_all_cards(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(self.locators["all_agent_cards"]))
        self.driver.execute_script("window.scrollTo(0, 0);")
        WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located(self.locators["all_agent_cards"]))
        return self.driver.find_elements(*self.locators["all_agent_cards"])


    def get_draft_cards(self):
        all_cards = self.get_all_cards()
        return [card for card in all_cards if "Draft" in card.text]
    
    def get_private_cards(self):
        all_cards = self.get_all_cards()
        return [card for card in all_cards if "Private" in card.text]
    
    def get_organization_cards(self):
        all_cards = self.get_all_cards()
        return [card for card in all_cards if "Organization" in card.text]
    
    def is_card_visible(self, card):
        return card.is_displayed()

    def get_card_by_title(self, title):
        all_cards = self.get_all_cards()
        for card in all_cards:
            if title in card.text:
                return card
        return None
    
    def get_card_count(self, card_type):
        if card_type == "draft":
            return len(self.get_draft_cards())
        elif card_type == "private":
            return len(self.get_private_cards())
        elif card_type == "organization":
            return len(self.get_organization_cards())
        else:
            return 0
    
    def has_cards(self, card_type, minimum=1):
        count = self.get_card_count(card_type)
        return count >= minimum
    

    def scroll_down_up(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 1).until(lambda d: True)
        self.driver.execute_script("window.scrollTo(0, 0);")


    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        WebDriverWait(self.driver, 5).until(lambda d: element.is_displayed())
    
    

    def click_edit_button_by_card_type(self, card_type, index=0):
        if card_type == "private":
            cards = self.get_private_cards()
        elif card_type == "draft":
            cards = self.get_draft_cards()
        elif card_type == "organization":
            cards = self.get_organization_cards()
        else:
            raise ValueError(f"Invalid card_type: {card_type}")

        if len(cards) <= index:
            raise IndexError(f"{card_type} 카드가 {index+1}개 미만입니다.")

        self.scroll_into_view(cards[index])

        buttons = cards[index].find_elements(By.CSS_SELECTOR, "button")
        edit_btn = None
        for btn in buttons:
            try:
                icon = btn.find_element(By.CSS_SELECTOR, "svg[data-icon='pen']")
                if icon:
                    edit_btn = btn
                    break
            except:
                continue

        if not edit_btn:
            raise NoSuchElementException("Edit 버튼(svg[data-icon='pen'])을 찾지 못했습니다.")

        WebDriverWait(self.driver, 5).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiDialog-container"))
        )
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(edit_btn))
        WebDriverWait(self.driver, 5).until(lambda d: edit_btn.is_displayed())

        try:
            edit_btn.click()
        except:
            self.driver.execute_script("arguments[0].click();", edit_btn)

        print(f"✅ {card_type} 카드 {index + 1}번째 Edit 버튼 클릭 완료")





    def click_delete_button_by_card_type(self, card_type, index=0):
    
        if card_type == "private":
            cards = self.get_private_cards()
        elif card_type == "draft":
            cards = self.get_draft_cards()
            if len(cards) <= index:
                wait = WebDriverWait(self.driver, 5)
                for _ in range(5):
                    if len(cards) > index:
                        break
                    self.driver.execute_script("window.scrollBy(0, 800);")
                    try:
                        wait.until(lambda d: len(self.get_draft_cards()) > len(cards))
                    except TimeoutException:
                        pass
                    cards = self.get_draft_cards()

        elif card_type == "organization":
            cards = self.get_organization_cards()
        else:
            raise ValueError(f"Invalid card_type: {card_type}")
        
        if len(cards) <= index:
            raise IndexError(f"{card_type} 카드가 {index+1}개 미만입니다.")

        self.scroll_into_view(cards[index])
  
        delete_btn = cards[index].find_element(By.CSS_SELECTOR, "button:has(svg[data-icon='trash'])")
        delete_btn.click()
        print(f"✅ {card_type} 카드 Delete 버튼 클릭")




    def confirm_delete_modal(self):
        delete_confirm_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.locators["confirm_delete_modal_button"]))
        delete_confirm_btn.click()
        print("✅ 삭제 확인 모달에서 Delete 버튼 클릭")


    def cancel_delete_modal(self):
        cancel_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.locators["cancel_delete_modal_button"]))
        cancel_btn.click()
        print("✅ 삭제 확인 모달에서 Cancel 버튼 클릭")
        WebDriverWait(self.driver, 5, 0.1).until(EC.invisibility_of_element_located(self.locators["confirm_delete_modal_button"]))
        print("✅ 모달 닫힘")

    def is_delete_modal_visible(self, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.locators["confirm_delete_modal_button"]))
            return True
        except TimeoutException:
            return False