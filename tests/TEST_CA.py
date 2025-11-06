from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.get("https://qatrack.elice.io/ai-helpy-chat")

test_ca_001_1 = wait.until(EC.presence_of_element_located((By.NAME, "loginId")))

test_ca_001_1.send_keys("ssunull@daum.net")
driver.find_element(By.NAME, "password").send_keys("dorpw-6Gewk")
driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()


test_ca_001_2 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent"]')))

test_ca_001_2.click()


test_ca_001_3 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/ai-helpy-chat/agent/builder"]')))

test_ca_001_3.click()

try: 
    if wait.until(EC.url_contains("builder#form")): 
        print("✅ CA_001_페이지로 이동 완료!") 
except :
    print("❌ 페이지로 이동 실패!")


