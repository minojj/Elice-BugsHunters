import os
import sys
import requests
import re
import xml.etree.ElementTree as ET

# 🌐 환경변수 설정
JIRA_URL = os.getenv("JIRA_URL")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JUNIT_PATH = os.getenv("JUNIT_PATH", "reports/test-results.xml")
JOB_NAME = os.getenv("JENKINS_JOB_NAME", "unknown-job")
BUILD_NUMBER = os.getenv("JENKINS_BUILD_NUMBER", "0")
BRANCH_NAME = os.getenv("JENKINS_BRANCH_NAME", "unknown")
BUILD_URL = os.getenv("JENKINS_BUILD_URL", "")
LABEL_AUTOTEST = "autotest"


# 🧩 유틸 함수
def make_summary(test):
    return f"[AutoTest] Failed: {test['classname']}::{test['name']}"

def make_adf_text(text: str):
    """ADF(Atlassian Document Format) 포맷 변환"""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ],
    }
def jira_search_issues(session, jql: str):
    """
    Jira Cloud용 신규 검색 API:
    POST /rest/api/3/search/jql
    """
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    payload = {
        "jql": jql,
        "maxResults": 10
    }
    resp = session.post(url, json=payload)

    if resp.status_code != 200:
        print(f"[WARN] Jira 검색 실패 ({resp.status_code}): {resp.text}")
        return []

    data = resp.json()
    return data.get("issues", [])


# 🧩 JUnit XML 파싱
def parse_junit_results(xml_path):
    failed_tests = []
    passed_tests = []
    print(f"[INFO] Parsing JUnit file: {xml_path}")

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"[ERROR] XML 파싱 실패: {e}")
        return failed_tests, passed_tests

    for testcase in root.iter("testcase"):
        name = testcase.attrib.get("name")
        classname = testcase.attrib.get("classname")
        failure = testcase.find("failure")

        if failure is not None:
            failed_tests.append({
                "name": name,
                "classname": classname,
                "message": failure.attrib.get("message", "")[:1000]
            })
        else:
            passed_tests.append({
                "name": name,
                "classname": classname
            })

    print(f"[INFO] Found {len(failed_tests)} failed tests, {len(passed_tests)} passed tests.")
    return failed_tests, passed_tests

def escape_jql_value(value: str) -> str:
    """JQL에서 특수문자 이스케이프"""
    # Jira JQL 문법상 이스케이프해야 하는 문자: \ " ' [ ] ( ) : ,
    return re.sub(r'(["\'\[\]\(\):,])', r'\\\1', value)

# 🧩 JIRA 세션 생성
def make_jira_session():
    session = requests.Session()
    session.auth = (JIRA_USER, JIRA_API_TOKEN)
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    return session


# 🧩 JIRA 이슈 생성 / 코멘트 / 종료
def create_or_comment_issue(session, test):
    summary = make_summary(test)
    escaped_summary = escape_jql_value(summary)

    # 🔍 1️⃣ 기존 오픈 이슈 정확 검색 (새 API 사용)
    jql = f'project = "{JIRA_PROJECT}" AND summary = "{escaped_summary}" AND statusCategory != Done ORDER BY created DESC'
    issues = jira_search_issues(session, jql)

    if issues:
        issue_key = issues[0]["key"]
        print(f"[INFO] 기존 이슈 발견: {issue_key} — 코멘트 추가")

        comment_text = (
            f"🚨 *자동화 테스트가 다시 실패했습니다!*\n\n"
            f"*테스트:* `{test['classname']}::{test['name']}`\n"
            f"*빌드:* [{JOB_NAME} #{BUILD_NUMBER}]({BUILD_URL})\n\n"
            f"*실패 요약:*\n{test['message'][:500]}..."
        )

        comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
        resp = session.post(comment_url, json={"body": make_adf_text(comment_text)})
        if resp.status_code >= 400:
            print(f"[ERROR] 코멘트 추가 실패 ({issue_key}): {resp.status_code} {resp.text}")
        else:
            print(f"[INFO] ✅ 코멘트 추가 완료: {issue_key}")
        return issue_key

    # 🔁 2️⃣ 여기까지 왔으면 기존 이슈 없음 → 새로 생성
    print(f"[INFO] 새로운 이슈 생성: {summary}")

    desc_text = (
        f"테스트 실패 감지됨 🚨\n\n"
        f"*테스트:* `{test['classname']}::{test['name']}`\n"
        f"*빌드:* [{JOB_NAME} #{BUILD_NUMBER}]({BUILD_URL})\n\n"
        f"*오류 메시지 요약:*\n{test['message'][:500]}..."
    )

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "description": make_adf_text(desc_text),
            "labels": [LABEL_AUTOTEST],
            "issuetype": {"name": "Bug"},
        }
    }

    create_url = f"{JIRA_URL}/rest/api/3/issue"
    resp = session.post(create_url, json=payload)

    if resp.status_code >= 400:
        print(f"[ERROR] Failed to create issue for {summary}: {resp.status_code} {resp.text}")
        return None

    issue_key = resp.json().get("key")
    print(f"[INFO] 🆕 Created JIRA issue: {issue_key}")
    return issue_key


def close_passed_issues(session, passed_tests):
    """✅ 통과된 테스트가 기존 실패 이슈를 닫도록 처리"""
    for test in passed_tests:
        summary = f"[AutoTest] Failed: {test['classname']}::{test['name']}"
        escaped_summary = escape_jql_value(summary)

        jql = f'project = "{JIRA_PROJECT}" AND summary = "{escaped_summary}" AND statusCategory != Done ORDER BY created DESC'
        issues = jira_search_issues(session, jql)

        for issue in issues:
            issue_key = issue["key"]
            print(f"[INFO] ✅ 테스트 통과 — 이슈 {issue_key} 닫기 시도 중")

            # 1️⃣ 코멘트 추가
            comment_text = (
                f"✅ *자동화 테스트가 통과했습니다!*\n\n"
                f"*테스트:* `{test['classname']}::{test['name']}`\n"
                f"*빌드:* [{JOB_NAME} #{BUILD_NUMBER}]({BUILD_URL})\n\n"
                f"이전 실패 이슈를 자동으로 닫습니다."
            )
            comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
            session.post(comment_url, json={"body": make_adf_text(comment_text)})

            # 2️⃣ 상태 전환 (Done)
            transition_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
            trans_resp = session.get(transition_url)
            if trans_resp.status_code == 200:
                transitions = trans_resp.json().get("transitions", [])
                done_transition = next((t for t in transitions if "Done" in t["name"]), None)
                if done_transition:
                    transition_id = done_transition["id"]
                    session.post(transition_url, json={"transition": {"id": transition_id}})
                    print(f"[INFO] 🔒 이슈 {issue_key} → Done 으로 전환 완료")
                else:
                    print(f"[WARN] Done 상태 전환 옵션을 찾지 못했습니다 ({issue_key})")

# 🚀 메인 실행

if __name__ == "__main__":
    failed_tests, passed_tests = parse_junit_results(JUNIT_PATH)
    session = make_jira_session()

    if failed_tests:
        print(f"[INFO] 🚨 {len(failed_tests)}개의 실패 테스트 이슈 생성/갱신 중...")
        for t in failed_tests:
            create_or_comment_issue(session, t)
    else:
        print("[INFO] No failed tests found.")

    if passed_tests:
        print(f"[INFO] ✅ {len(passed_tests)}개의 통과 테스트 이슈 닫기 중...")
        close_passed_issues(session, passed_tests)
