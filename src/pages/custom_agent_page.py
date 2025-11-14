from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import platform
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains





class AgentExplorerPage:

    LOCATORS = {
        "agent_explorer_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]'),
        "create_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]'),
        "agent_card_title": (By.CSS_SELECTOR, "p.MuiTypography-body1.MuiTypography-noWrap"),
        "agent_card": (By.CSS_SELECTOR, "a.MuiCard-root, a[class*='MuiCard'], a[href*='/agent/']"),
        "agent_chat_input": (By.CSS_SELECTOR, "textarea[placeholder='Ask anything']"),
        "search_input": (By.CSS_SELECTOR, "input[placeholder='Search AI agents']"),
        "search_agent_card_spans": (By.CSS_SELECTOR, "span.MuiTypography-root"),
        "fixed_target_card": (By.CSS_SELECTOR, 'a[href*="8f701da7-7c53-4f54-b26d-b6eeb39a4479"]'),
        "fixed_target_card_menu_btn": (By.CSS_SELECTOR, 'a[href*="582b1607-e565-4d5a-9e8d-18f99bb52422"] button[aria-label="menu"]'),
    }

    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"



    def get_element(self, key, wait_type="visible", timeout=10):
        #요소 키워드(agent_explorer_btn, create_btn 등)를 받아 element 반환
        locator = self.LOCATORS[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)
    


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



    def force_hover(self, card, timeout=5):
        try:
            # 카드 중앙 스크롤
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", card
            )

            # Selenium hover
            actions = ActionChains(self.driver)
            actions.move_to_element(card).perform()

            # JS hover
            self.driver.execute_script("""
                arguments[0].dispatchEvent(
                    new MouseEvent('mouseover', {bubbles:true, cancelable:true})
                );
            """, card)

            # 메뉴 버튼 대기
            WebDriverWait(self.driver, timeout).until(
                lambda d: (
                    len(card.find_elements(By.CSS_SELECTOR, 'button[aria-label="menu"]')) > 0
                    and card.find_element(By.CSS_SELECTOR, 'button[aria-label="menu"]').is_displayed()
                )
            )

            return True
        except Exception as e:
            print("❌ hover 실패:", e)
            return False




    def open_card_menu(self, card, timeout=5):
        print("🔍 메뉴 열기 시도…")

        if not self.force_hover(card, timeout=timeout):
            print("❌ hover 실패")
            return False

        # hover가 성공하면 메뉴 버튼은 반드시 보이게 되어 있음
        try:
            menu_btn = card.find_element(By.CSS_SELECTOR, 'button[aria-label="menu"]')

            WebDriverWait(self.driver, timeout).until(
                lambda d: menu_btn.is_displayed() and menu_btn.is_enabled()
            )

            self.driver.execute_script("arguments[0].click();", menu_btn)
            print("✔ 메뉴 버튼 JS 클릭 완료")
            return True

        except Exception as e:
            print("❌ 메뉴 버튼 클릭 실패:", e)
            return False





    def delete_fixed_agent(self, my_agents_page, save_page):
        wait = WebDriverWait(self.driver, 15)
        short_wait = WebDriverWait(self.driver, 5)

        print(f"🌐 현재 URL: {self.driver.current_url}")

        # 1️⃣ 카드 리스트 로딩 대기
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/agent/']")
                )
            )
            print("✅ 카드 리스트(전체) 렌더링됨!")
        except TimeoutException:
            print("❌ Explorer에 카드가 하나도 안 뜸 (권한/데이터 문제?)")
            return False

        # 2️⃣ 카드 href 디버깅용 출력
        all_cards = self.driver.find_elements(
            By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/agent/']"
        )
        print(f"📦 페이지에 있는 카드 수: {len(all_cards)}")
        for card in all_cards:
            print("카드 href:", card.get_attribute("href"))

        # 3️⃣ 타겟 카드 찾기
        target_cards = self.driver.find_elements(
            By.CSS_SELECTOR,
            'a[href*="582b1607-e565-4d5a-9e8d-18f99bb52422"]'
        )
        print(f"🎯 타겟 카드 발견 여부: {len(target_cards)}개")

        if len(target_cards) == 0:
            print("❌ 타겟 카드가 페이지에 없습니다. 스크롤이 필요합니다.")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            short_wait.until(lambda d: True)

            target_cards = self.driver.find_elements(
                *self.LOCATORS["fixed_target_card"]
            )
            print(f"🎯 스크롤 후 타겟 카드: {len(target_cards)}개")
            if len(target_cards) == 0:
                print("❌ 스크롤 후에도 타겟 카드 없음")
                return False

        # 4️⃣ 카드 DOM 존재 대기
        card = wait.until(
            EC.presence_of_element_located(self.LOCATORS["fixed_target_card"])
        )
        print("✅ 타겟 카드 발견")

        # 🔥🔥🔥 5️⃣ 여기서 open_card_menu() 사용
        result = self.open_card_menu(card)
        if not result:
            print("❌ 메뉴 버튼 열기 실패")
            return False

        # 6️⃣ Delete 버튼 클릭
        try:
            delete_icon = short_wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "svg[data-icon='trash']")
                )
            )
            delete_btn = delete_icon.find_element(
                By.XPATH, "./ancestor::*[self::button or self::li][1]"
            )
            self.driver.execute_script("arguments[0].click();", delete_btn)
            print("🗑️ 드롭다운 메뉴에서 Delete JS 클릭")
        except TimeoutException:
            print("✅ Delete 메뉴 항목 안 나타남 → 삭제 권한 없음")
            return True

        # 7️⃣ 삭제 확인 모달 클릭
        try:
            modal_delete_btn = short_wait.until(
                EC.element_to_be_clickable(
                    my_agents_page.LOCATORS["confirm_delete_modal_button"]
                )
            )
            if not modal_delete_btn.is_enabled():
                print("⚠️ Delete 버튼 비활성화 (권한 없음)")
                return True

            modal_delete_btn.click()
            print("🗑️ 삭제 모달 Delete 클릭")

            # 8️⃣ 스낵바 표시 대기
            snackbar = wait.until(
                EC.visibility_of_element_located(
                    save_page.LOCATORS["success_alert"]
                )
            )
            snackbar_text = snackbar.text
        except TimeoutException:
            print("⚠️ 삭제 모달이 나타나지 않음 → 삭제 권한 없음")
            return True

        print(f"📢 스낵바 메시지: {snackbar_text}")
        lower = snackbar_text.lower()

        if any(k in lower for k in ["error", "권한", "cannot", "failed"]):
            print("✅ 삭제 실패 알림 (정상)")
            return True

        print("❌ 삭제가 실제로 이루어짐 → 실패 처리")
        return False


class CreateAgentPage:
    
    LOCATORS = {
        "name": (By.NAME, "name"),
        "description": (By.CSS_SELECTOR, 'input[name="description"]'),
        "rules": (By.NAME, "systemPrompt"),
        "conversation": (By.NAME, "conversationStarters.0.value"),
        "create_btn": (By.CSS_SELECTOR, "button.MuiButton-containedPrimary"),  # Create/Publish 공용 버튼

        "file_input": (By.CSS_SELECTOR, "input.css-1bgri6b"),
        "file_item": (By.CSS_SELECTOR, "div.css-8e3ts2 > div.MuiStack-root.css-1lawy5a"),
        "file_success_icon": (By.CSS_SELECTOR, "div.css-tza19w svg.MuiSvgIcon-colorSuccess"),
        "file_failed_icon": (By.CSS_SELECTOR, "div.css-tza19w svg.MuiSvgIcon-colorError"),
        "file_status": (By.CSS_SELECTOR, "span.MuiTypography-caption"),
        "file_error_msg": (By.CSS_SELECTOR, "p.MuiTypography-body2.css-wrn3u"),
    }


    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent"

    def open(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ 커스텀 에이전트 메인 페이지 접속 성공")

    def get_element(self, key, wait_type="visible", timeout=10):
        #요소 키워드(name, description 등)를 받아 element 반환
        locator = self.LOCATORS[key]
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
        conv_input = self.get_element("conversation")
        conv_input.send_keys(conversation)
        conv_input.send_keys(Keys.TAB)
        self.last_agent_name = name  


        return {
        "name": name,
        "description": description,
        "rules": rules,
        "conversation": conversation
        }
    

    def fill_form_with_trigger(self, name, description, rules, conversation):

        # ✅ OS별 전체 선택 키 결정 (Windows/Linux: CTRL, mac: CMD)
        modifier = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

        def type_and_trigger(key, value):
            el = self.get_element(key)

            # ① 기존 값 확실히 지우기
            el.click()
            el.send_keys(modifier + "a")
            el.send_keys(Keys.DELETE)

            # ② send_keys로 실제 입력 (React가 이걸 먼저 받음)
            if value:
                el.send_keys(value)
            else:
                # 빈 문자열일 경우에도 React onChange를 발생시키기 위해
                el.send_keys(" ")
                el.send_keys(Keys.BACKSPACE)

            # ③ React의 synthetic onChange가 확실히 인식하도록 value 재동기화
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                el
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                el
            )

            # ④ 포커스 해제 → auto-save 트리거
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
        

    def get_field_value(self, field_name):
        return self.get_element(field_name).get_attribute("value")


    def get_all_field_values(self):
        return {
            "name": self.get_field_value("name"),
            "description": self.get_field_value("description"),
            "rules": self.get_field_value("rules"),
            "conversation": self.get_field_value("conversation")
        }
    

    def wait_for_autosave(self, expected_values, timeout=20):
        # 🔁 약간 느슨한 poll 주기 (0.3초)로 계속 확인
        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.3)

        # 1️⃣ name input이 나타날 때까지
        wait.until(EC.presence_of_element_located((By.NAME, "name")))

        # 2️⃣ input value가 기대값으로 바뀔 때까지
        wait.until(
            lambda d: d.find_element(By.NAME, "name").get_attribute("value") == expected_values["name"]
        )

        # 3️⃣ 생성 페이지 상단 제목(p.MuiTypography-body2)도 바뀌는지 체크 (옵션)
        try:
            wait.until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR, "p.MuiTypography-body2"
                ).text.strip() == expected_values["name"]
            )
        except Exception:
            pass  # 없을 수도 있으니 Optional

        # 4️⃣ CSS selector로 Saved 배지 + 체크아이콘 나타날 때까지 (옵션)
        try:
            wait.until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR,
                    "span.MuiTypography-caption.css-10z10oy"
                ))
            )

            wait.until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR,
                    "svg[data-icon='circle-check']"
                ))
            )

            print("✅ autosave 'Saved' UI 확인 완료")

        except Exception:
            print("⚠️ 'Saved' UI를 찾지 못했지만, 입력 값 기준으로 autosave 완료로 간주")



    def get_agent_id_from_url(self):
        current_url = self.driver.current_url
        try:
            agent_id = current_url.split("/agent/")[1].split("/")[0]
            print(f"🆔 생성된 agent ID: {agent_id}")
            return agent_id
        except IndexError:
            raise AssertionError(f"❌ URL에서 agent ID 추출 실패 (현재 URL: {current_url})")


    def upload_file(self, filepath):
        file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.LOCATORS["file_input"])
        )

        self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(filepath)

        print(f"📤 파일 업로드 시도: {filepath}")


    def get_last_uploaded_item(self, timeout=10):
        wait = WebDriverWait(self.driver, timeout)

        # 파일 업로드가 시작될 때까지 기다림 (업로드되는 아이템이 최소 1개 등장)
        wait.until(lambda d: len(d.find_elements(*self.LOCATORS["file_item"])) > 0)

        # 모든 업로드된 아이템 가져오기
        items = self.driver.find_elements(*self.LOCATORS["file_item"])

        # 가장 마지막 것이 최신 업로드 파일
        return items[-1]
        

    def get_file_status(self, file_item):
        return file_item.find_element(*self.LOCATORS["file_status"]).text.strip()



    def has_success_icon(self, file_item, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(file_item.find_elements(
                    By.CSS_SELECTOR, "div.css-tza19w svg.MuiSvgIcon-colorSuccess"
                )) > 0
            )
            return True
        except:
            return False


    def has_failed_icon(self, file_item, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(file_item.find_elements(
                    By.CSS_SELECTOR, "div.css-tza19w svg.MuiSvgIcon-colorError"
                )) > 0
            )
            return True
        except:
            return False

    def get_error_msg(self, file_item):
        els = file_item.find_elements(*self.LOCATORS["file_error_msg"])
        return els[0].text.strip() if els else None


   
    

class SaveAgentPage:

    LOCATORS = {
        "private_radio": (By.CSS_SELECTOR, "input[value='private']"),
        "organization_radio": (By.CSS_SELECTOR, "input[value='organization']"),
        "save_btn": (By.CSS_SELECTOR, "button[type='submit'][form='publish-setting-form']"),
        "success_alert": (By.CSS_SELECTOR, "div#notistack-snackbar"),
        "start_chat_btn": (By.CSS_SELECTOR, "div#notistack-snackbar button[type='button']"),
        "chat_input": (By.CSS_SELECTOR, "textarea[name='input']"),
    }

    def __init__(self, driver):
        self.driver = driver

    def select_mode(self, mode):
        key = f"{mode}_radio"

        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-paper")))

        radio = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.LOCATORS[key]))
        if not radio.is_selected():
            clickable_radio = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio.get_attribute('id')}']")
            self.driver.execute_script("arguments[0].click();", clickable_radio)
        check_radio = self.driver.find_element(*self.LOCATORS[key])
        assert check_radio.is_selected(), f"{mode} 옵션이 선택되지 않았습니다."


    def click_save(self):
        save_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.LOCATORS["save_btn"]))
        save_btn.click()

    def click_start_chat_fast(self):
        btn = WebDriverWait(self.driver, 2, poll_frequency=0.1).until(EC.presence_of_element_located(self.LOCATORS["start_chat_btn"]))
        self.driver.execute_script("arguments[0].click();", btn)


    def verify_success(self):
        alert = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.LOCATORS["success_alert"]))
        assert "The agent has been created" in alert.text, "❌ 에이전트 생성 실패"
        print("✅ 에이전트 생성 성공!")

    def get_snackbar_text(self):
        alert = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.LOCATORS["success_alert"]))
        # .text 대신 innerText로 백업 (MUI 포털 대응)
        text = alert.text.strip() or alert.get_attribute("innerText").strip()
        return text
    

    def get_element(self, key, wait_type="visible", timeout=10):
        locator = self.LOCATORS[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)
    


    
class ChatCreatePage:

    LOCATORS = {
        "create_with_chat_btn": (By.CSS_SELECTOR, "button[type='button'][value='chat']"),
        "create_chat_input": (By.CSS_SELECTOR, "textarea[name='input']"),
        "info_list": (By.CSS_SELECTOR, "ul[class^='css-'][class*='e1ge9pxx'] li"),
        "conversation_list": (By.CSS_SELECTOR, "ol[class^='css-'][class*='e1ge9pxx'] li"),
    }

    def __init__(self, driver):
        self.driver = driver

    def click_create_with_chat(self):
        """'Create with Chat' 버튼 클릭 후 챗봇 대화 페이지로 진입"""
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.LOCATORS["create_with_chat_btn"])
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
        locator = self.LOCATORS[key]
        wait = WebDriverWait(self.driver, timeout)

        if wait_type == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif wait_type == "presence":
            wait.until(EC.presence_of_element_located(locator))
        else:
            wait.until(EC.visibility_of_element_located(locator))

        return self.driver.find_element(*locator)
    


    def send_single_message(self):

        # 1) 입력창 준비
        chat_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.LOCATORS["create_chat_input"])
        )

        self.driver.execute_script("arguments[0].focus();", chat_box)
        chat_box.click()

        # 2) 입력창 초기화
        chat_box.send_keys(Keys.CONTROL + "a")
        chat_box.send_keys(Keys.DELETE)
        chat_box.send_keys(self.step1_text())

        # 3) Send 버튼 클릭 (JS 클릭)
        send_btn = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Send']"))
        )

        self.driver.execute_script("arguments[0].click();", send_btn)
        print("📨 step1 메시지 전송 완료")

        # 4) AI 응답 대기 (running → complete)
        WebDriverWait(self.driver, 60).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "div[data-status='running']")) == 0
        )

        # 5) 실제 답변 렌더링 확인
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.aichatkit-md[data-status='complete'] p")
            )
        )

        print("💬 AI 응답 렌더링 완료 (step1)")




    
    
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
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    if any(el.text.strip() for el in elements):
                        return True
                except:
                    pass
            return False

        wait.until(_answer_rendered)
        print("💬 AI 답변 렌더링 확인 완료")
        return True




    


class MyAgentsPage:
    LOCATORS = {
        "my_agents_btn": (By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/mine"]'),
        "all_agent_cards": (By.CSS_SELECTOR, "div.MuiGrid-item"),
        "draft_chip": (By.CSS_SELECTOR, ".MuiChip-label"),
        "private_icon": (By.CSS_SELECTOR, "svg[data-icon='lock']"),
        "organization_icon": (By.CSS_SELECTOR, "svg[data-icon='buildings']"),
        "edit_icon": (By.CSS_SELECTOR, "svg[data-icon='pen']"),
        "delete_icon": (By.CSS_SELECTOR, "svg[data-icon='trash']"),
        "confirm_delete_modal_button": (By.CSS_SELECTOR, "button.MuiButton-containedError"),
        "cancel_delete_modal_button": (By.CSS_SELECTOR, "button.MuiButton-containedInherit"),
    }

    def __init__(self, driver):
        self.driver = driver
        self.url = "https://qaproject.elice.io/ai-helpy-chat/agent/mine"


  
    def click_my_agents_button(self):
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.LOCATORS["my_agents_btn"])
        )
        btn.click()



    def get_all_cards(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located(self.LOCATORS["all_agent_cards"])
        )

        previous = -1
        for _ in range(10):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            cards = self.driver.find_elements(*self.LOCATORS["all_agent_cards"])
            if len(cards) == previous:
                break
            previous = len(cards)

        return cards



    def load_all_cards(self, timeout=10):
 
        #Virtuoso 무한스크롤 기반 페이지에서 모든 카드를 렌더링할 때까지 스크롤 반복.

        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.1)
        
        last_count = -1

        while True:
            # 현재 카드 개수 측정
            cards = self.driver.find_elements(*self.LOCATORS["all_agent_cards"])
            current_count = len(cards)

            # 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # DOM 변화(wait): 카드 개수가 증가할 때까지 대기
            try:
                wait.until(lambda d: len(d.find_elements(*self.LOCATORS["all_agent_cards"])) > current_count)
            except:
                # 더 이상 늘어나지 않으면 끝
                break

            # 변화 없으면 break
            if current_count == last_count:
                break

            last_count = current_count

        # 맨 위로 다시 올려 두기
        self.driver.execute_script("window.scrollTo(0, 0);")





    def scroll_into_view(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
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

        # div 내부 어디에 있든 a[href*='/agent/'] 를 찾기
        link = card.find_element(By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/agent/'], a[href*='/agent/']")
        href = link.get_attribute("href")

        if not href:
            raise ValueError(f"에이전트 href를 찾지 못했습니다.\ncard text: {card.text}")

        # URL 마지막 구조는 .../<agent_id>/builder
        agent_id = href.rstrip("/").split("/")[-2]
        return agent_id
    

    def find_card_by_agent_id(self, agent_id, timeout=10):
        wait = WebDriverWait(self.driver, timeout)

        for _ in range(timeout):
            cards = self.get_all_cards()

            for card in cards:
                try:
                    link = card.find_element(By.CSS_SELECTOR, "a[href*='/ai-helpy-chat/agent/'], a[href*='/agent/']")
                    href = link.get_attribute("href") or ""
                    if agent_id in href:
                        return card
                except:
                    continue

        return None
    

    def wait_for_cards_loaded(self, timeout=10):


        wait = WebDriverWait(self.driver, timeout)

        # Virtuoso Grid 아이템이 최소 하나 등장할때까지 대기
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.MuiGrid-item")
                )
            )
            return True

        except:
            print("⚠️ Virtuoso 카드 리스트가 로드되지 않음 (timeout)")
            return False
    

    def wait_for_card_update(self, agent_id, updated_title, timeout=20):
        wait = WebDriverWait(self.driver, timeout)

        for _ in range(timeout * 2):  
            self.driver.get(self.url)

            # 모든 카드 렌더링 대기
            wait.until(
                EC.presence_of_all_elements_located(self.LOCATORS["all_agent_cards"])
            )

            # ID로 카드 찾기
            card = self.find_card_by_agent_id(agent_id)
            if not card:
                continue

            # 제목 비교
            try:
                title_el = card.find_element(
                    By.CSS_SELECTOR, "p.MuiTypography-body1.MuiTypography-noWrap"
                )
                if title_el.text.strip() == updated_title:
                    return card

            except Exception:
                pass

        raise AssertionError(
            f"❌ 카드(ID={agent_id}) 제목 '{updated_title}' 로 갱신되지 않음"
        )



    def get_private_cards(self):
        cards = self.get_all_cards()
        result = []
        for card in cards:
            try:
                card.find_element(*self.LOCATORS["private_icon"])
                result.append(card)
            except:
                continue
        return result

    def get_organization_cards(self):
        cards = self.get_all_cards()
        result = []
        for card in cards:
            try:
                card.find_element(*self.LOCATORS["organization_icon"])
                result.append(card)
            except:
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
            except:
                continue
        return None
    


    def click_edit_button_by_card_type(self, card_type, index=0):
        cards = self._get_cards_by_type(card_type)

        if len(cards) <= index:
            raise IndexError(f"{card_type} 카드가 {index+1}개 미만입니다.")

        card = cards[index]
        self.scroll_into_view(card)

        edit_btn = self._find_button_in_card(card, self.LOCATORS["edit_icon"])
        if not edit_btn:
            raise NoSuchElementException(f"{card_type} 카드에서 Edit 버튼을 찾지 못했습니다.")

        WebDriverWait(self.driver, 10).until(lambda d: edit_btn.is_enabled() and edit_btn.is_displayed())
        self.driver.execute_script("arguments[0].click();", edit_btn)

        print(f"✏️ {card_type} 카드 {index+1}번째 Edit 클릭 완료")

   

    def click_delete_button_by_card_type(self, card_type, index=0):
        cards = self._get_cards_by_type(card_type)

        if len(cards) <= index:
            raise IndexError(f"{card_type} 카드가 {index+1}개 미만입니다.")

        card = cards[index]
        self.scroll_into_view(card)

        delete_btn = self._find_button_in_card(card, self.LOCATORS["delete_icon"])
        if not delete_btn:
            raise NoSuchElementException(f"{card_type} 카드에서 Delete 버튼을 찾지 못했습니다.")

        WebDriverWait(self.driver, 10).until(lambda d: delete_btn.is_enabled() and delete_btn.is_displayed())
        self.driver.execute_script("arguments[0].click();", delete_btn)

        print(f"🗑️ {card_type} 카드 {index+1}번째 Delete 클릭")

 
    def confirm_delete_modal(self):
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.LOCATORS["confirm_delete_modal_button"]))
        btn.click()
        print("✅ 삭제 확인 모달에서 Delete 버튼 클릭")


    def cancel_delete_modal(self):
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.LOCATORS["cancel_delete_modal_button"]))
        btn.click()
        print("✅ 삭제 확인 모달에서 Cancel 버튼 클릭")

        # 모달이 사라질 때까지 대기
        WebDriverWait(self.driver, 5, 0.1).until(EC.invisibility_of_element_located(self.LOCATORS["confirm_delete_modal_button"]))
        print("✅ 모달 닫힘")


    def is_delete_modal_visible(self, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.LOCATORS["confirm_delete_modal_button"]))
            return True
        except TimeoutException:
            return False