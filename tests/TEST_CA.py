from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

def test_ca_001(driver, email, password):
    wait = WebDriverWait(driver, 10)

    # 1️⃣ 접속
    driver.get("https://qatrack.elice.io/ai-helpy-chat")

    # 2️⃣ 로그인
    wait.until(EC.presence_of_element_located((By.NAME, "loginId"))).send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # 3️⃣ Agent Explorer 클릭
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]'))).click()

    # 4️⃣ Builder 클릭
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]'))).click()

    # 5️⃣ 페이지 전환 확인
    try:
        if wait.until(EC.url_contains("builder#form")):
            print("✅ CA_001_페이지로 이동 완료!")
    except TimeoutException:
        print("❌ 페이지로 이동 실패!")


# 실행
if __name__ == "__main__":
    driver = webdriver.Chrome()
    test_ca_001(driver, "ssunull@daum.net", "dorpw-6Gewk")


