import pytest
from src.pages.billing_page import BillingPage, PaymentMethodsPage, DanalCardPage, UsagePage


@pytest.fixture
def usage_page_loaded(logged_in_driver):
    driver = logged_in_driver
    driver.get("https://qaproject.elice.io/cloud/usage")
    return UsagePage(driver)





def test_bu_001_credit_usage_section_exists(logged_in_driver):

    drv = logged_in_driver
    billing = BillingPage(drv)

    billing.open()

    table_el = billing.wait_usage_table_loaded(timeout=20)

    assert table_el is not None
    assert table_el.tag_name.lower() == "table"

    
def test_bu_002_danal_card_payment_iframe_appears(logged_in_driver):

    drv = logged_in_driver
    methods = PaymentMethodsPage(drv)
    methods.open()

    methods.click_register_method()
    methods.select_currency_krw()
    methods.confirm_currency_selection()

    danal = DanalCardPage(drv)
    danal.switch_to_danal_iframe(timeout=15)

    assert danal.is_loaded(timeout=10), "danal 신용카드 결제창이 정상적으로 로드되지 않았습니다."






def test_bu_003_click_usage_history(logged_in_driver):
    driver = logged_in_driver
    usage_page = UsagePage(driver)

    usage_page.usage_history_click()

    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
    
    driver.save_screenshot("/tmp/🔥after_usage_click.png")

    assert usage_page.is_usage_history_page(), "❌ Usage History 페이지로 이동 실패"



def test_bu_004_click_ml_api(usage_page_loaded):
    page = usage_page_loaded
    page.click_ml_api_tab()
    assert page.is_ml_api_selected()

def test_bu_005_click_severless_status(usage_page_loaded):
    page = usage_page_loaded
    page.click_serverless_status()
    assert page.is_serverless_status_page()


def test_bu_006_click_api_key_manage(usage_page_loaded):
    page = usage_page_loaded
    page.click_api_key_manage()
    assert page.is_api_key_manage_page()
