from src.pages.agent_page import AgentPage

def test_agent_chat(driver):
    page = AgentPage(driver)
    page.open()
    page.send_message("안녕하세요, 테스트 메시지입니다.")
    assert "안녕하세요" in driver.page_source
