from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

import pyautogui
import time
import os

BASE_URL = "https://qaproject.elice.io/ai-helpy-chat"
TEST_FILENAME = r"C:\Users\josun\Downloads\git.pdf"


def login(driver, username, password):
    """로그인 공통 함수"""
    driver.get(BASE_URL)

    # 이메일 입력 필드 대기 후 입력
    Email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginId']"))
    )
    Email_input.send_keys(username)

    # 비밀번호 입력 필드 대기 후 입력
    Password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
    )
    Password_input.send_keys(password)

    # 로그인 버튼 클릭
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_btn.click()

    print("✅ 로그인 시도 완료")
         # 페이지 안정화 대기
    time.sleep(1)


def test_ce_001(driver,wait,filename):
    
    try:
        print("\n=== 테스트 시작 ===")
        #플러스 버튼 클릭 
        plus_btn =wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-haspopup='true']")))

        plus_btn.click()
        print("✅ 버튼 클릭 완료")
        time.sleep(0.5)
    
    
        #파일 업로드 클릭 ((####css, xpath ,text))
        try:
            file_upload_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.MuiButtonBase-root.MuiListItemButton-root[role='presentation'][data-action='file-upload']"))
            )
            print("✅ 파일 업로드 메뉴 발견 (CSS)")
        except:
            print("⚠️ CSS 선택자 실패, XPath 시도...")
            file_upload_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'File Upload')]"))
            )
            print("✅ 파일 업로드 메뉴 발견 (XPath)")

        file_upload_btn.click()
        print("✅ 파일 업로드 메뉴 클릭 완료")

        print("📂 파일 탐색창 대기 중...")
        
        driver.save_screenshot("before_file_input.png")


        print(f"🔍 파일 검색 중: {filename}")
        time.sleep(1)
        pyautogui.write(filename, interval=0.1)
        time.sleep(1)

        pyautogui.press('enter')

        # 파일 업로드 처리 대기
        time.sleep(2)
        driver.save_screenshot("after_file_upload.png")

        print("✅ 파일 업로드 완료")

        #백드롭 사라질떄까지 대기 
        try:
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiBackdrop-root"))
    )
            print("✅ 백드롭(overlay) 사라짐 확인 완료")
        except:
            print("⚠️ 백드롭 대기 중 오류 — 무시하고 진행")


        # 5. 검색 실행 버튼 클릭  (채팅에 메시지 입력 안할시, send_btn 비활성화 , 엔터 눌러야함)
        chat_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.MuiInputBase-root.MuiInputBase-multiline textarea')))
        print(f"✅ 입력창 발견: {chat_input.tag_name}")

        chat_input.click()
        time.sleep(0.5)
        chat_input.send_keys(Keys.RETURN)   
        print("✅ 엔터키로 전송 완료")           
        
        # 전송 후 처리 대기
        time.sleep(40)
        driver.save_screenshot("after_send.png")
        print("=== 테스트 성공 ===")
        return True


    except TimeoutException as e:
        print(f"❌ 타임아웃 오류: {str(e)}")
        print(f"   현재 URL: {driver.current_url}")
        driver.save_screenshot("timeout_error.png")
        return False
        
    except NoSuchElementException as e:
        print(f"❌ 요소를 찾을 수 없음: {str(e)}")
        driver.save_screenshot("element_error.png")
        return False
        
    except Exception as e:
        print(f"❌ 테스트 실패: {type(e).__name__} - {str(e)}")
        driver.save_screenshot("test_error.png")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":

   
    # driver = webdriver.Chrome()
    # test_ce_001(driver, "steam3@elice.com", "team3elice!@")


    driver = None
    
    try:
        # Chrome 드라이버 설정
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.maximize_window()
        
        wait = WebDriverWait(driver, 10)
        
        # 로그인
        login(driver, "team3@elice.com", "team3elice!@")
        
        # 파일 업로드 테스트
        result = test_ce_001(driver, wait, TEST_FILENAME)
        
        if result:
            print("🎉 테스트 성공!")
        else:
            print("⚠️ 테스트 실패")
    
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        if driver:
            driver.save_screenshot("critical_error.png")
    
    finally:
        if driver:
            print("\n🔄 브라우저 종료 중...")
            time.sleep(2)
            driver.quit()
            print("✅ 테스트 종료")