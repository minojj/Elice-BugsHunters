from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By # 요소 찾기 방식(By)을 사용하기 위해 import
from selenium.webdriver.common.keys import Keys # 키보드 입력(Keys)을 사용하기 위해 import
import time

# 검색할 키워드 정의
search_keyword = "selenium"

try:
    # 1. WebDriver 초기화 및 옵션 설정
    chrome_options = Options()
    service = Service() 
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("✅ Chrome WebDriver가 성공적으로 초기화되었습니다.")

    # 2. 웹페이지 접속 및 검색 동작 수행
    test_url = "https://www.google.com"
    print(f"🌐 {test_url}로 접속합니다...")
    driver.get(test_url)
    
    # 접속 후 현재 페이지 제목 출력
    print(f"📄 현재 페이지 제목: {driver.title}")

    # --- 👇 검색 기능 추가된 부분 시작 👇 ---

    print(f"🔎 검색창을 찾고 '{search_keyword}'을(를) 입력합니다...")
    
    # 2-1. 검색창 요소 찾기
    # Google의 검색창은 CSS 선택자 'textarea[name="q"]' 또는 name='q'로 찾을 수 있습니다.
    search_box = driver.find_element(By.NAME, "q")
    
    # 2-2. 검색어 입력
    search_box.send_keys(search_keyword)
    
    # 2-3. 검색 실행 (Enter 키 입력)
    search_box.send_keys(Keys.RETURN)

    # 검색 결과 페이지로 이동했는지 확인하기 위해 5초 대기
    print("⏳ 검색 결과 페이지를 확인하기 위해 5초 대기합니다.")
    time.sleep(5) 
    
    # 검색 후 현재 페이지 제목 출력 (검색 결과가 반영된 제목)
    print(f"📄 검색 후 페이지 제목: {driver.title}")

    # --- 👆 검색 기능 추가된 부분 끝 👆 ---

    # 3. 브라우저 종료
    driver.quit()
    print("❌ 브라우저를 성공적으로 닫았습니다. 테스트 완료.")

except Exception as e:
    print(f"🚨 오류가 발생했습니다: {e}")
    print("❗ **해결 방법 힌트:**")
    print("   1. 웹 요소가 로드되는 데 시간이 걸릴 경우, `time.sleep()` 대신 명시적 대기(`WebDriverWait`)를 사용해 보세요.")
    print("   2. Google의 HTML 구조가 변경되었다면, `By.NAME, 'q'` 대신 다른 선택자(예: `By.CSS_SELECTOR`)를 사용해야 할 수도 있습니다.")