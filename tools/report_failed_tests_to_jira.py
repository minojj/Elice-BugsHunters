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
    paragraphs = []
    for line in text.split('\n'):
        paragraphs.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": line}]
        })
    
    return {
        "type": "doc",
        "version": 1,
        "content": paragraphs if paragraphs else [{"type": "paragraph"}]
    }

def jira_search_issues(session, jql):
    """
    ✅ 공식 Jira Cloud REST API v3 검색
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """
    url = f"{JIRA_URL}/rest/api/3/search"
    
    params = {
        "jql": jql,
        "maxResults": 50,
        "fields": ["key", "summary", "status"]  # 리스트로 전달
    }
    
    print(f"[DEBUG] 검색 URL: {url}")
    print(f"[DEBUG] JQL: {jql}")
    
    resp = session.get(url, params=params, timeout=30)
    
    if resp.status_code != 200:
        print(f"[ERROR] Jira 검색 실패 ({resp.status_code})")
        print(f"[ERROR] 응답: {resp.text}")
        print(f"[ERROR] 요청 URL: {resp.url}")
        return []
    
    data = resp.json()
    issues = data.get("issues", [])
    print(f"[DEBUG] 검색된 이슈 수: {len(issues)}")
    
    if issues:
        for issue in issues[:3]:  # 처음 3개만 로그
            print(f"[DEBUG] - {issue.get('key')}: {issue.get('fields', {}).get('summary', 'N/A')}")
    
    return issues


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
    """
    JQL 검색용 이스케이프 (summary 필드 전용)
    - 특수문자 제거
    - 공백 정규화
    """
    # 특수문자 제거 (알파벳, 숫자, 공백, 하이픈, 언더스코어만 유지)
    value = re.sub(r'[^\w\s\-:]', ' ', value)
    # 연속 공백 정리
    value = re.sub(r'\s+', ' ', value)
    return value.strip()

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
    
    # ✅ JQL에서는 부분 일치 검색 (~) 사용
    # summary 필드의 핵심 키워드만 추출
    test_identifier = f"{test['classname']} {test['name']}"
    escaped_identifier = escape_jql_value(test_identifier)
    
    jql = (
        f'project = "{JIRA_PROJECT}" '
        f'AND labels = "{LABEL_AUTOTEST}" '
        f'AND summary ~ "{escaped_identifier}" '  # ~ 연산자로 부분 일치
        f'AND statusCategory != Done '
        f'ORDER BY created DESC'
    )
    
    issues = jira_search_issues(session, jql)

    if issues:
        issue = issues[0]
        issue_key = issue.get("key")
        
        if not issue_key:
            print(f"[ERROR] 검색된 이슈에 key가 없습니다: {issue}")
        else:
            print(f"[INFO] 기존 이슈 발견: {issue_key} — 코멘트 추가")
            
            comment_text = (
                f"🚨 자동화 테스트가 다시 실패했습니다!\n\n"
                f"테스트: {test['classname']}::{test['name']}\n"
                f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
                f"링크: {BUILD_URL}\n\n"
                f"실패 요약:\n{test['message'][:500]}"
            )
            
            comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
            resp = session.post(comment_url, json={"body": make_adf_text(comment_text)}, timeout=30)
            
            if resp.status_code >= 400:
                print(f"[ERROR] 코멘트 추가 실패 ({issue_key}): {resp.status_code} {resp.text}")
            else:
                print(f"[INFO] ✅ 코멘트 추가 완료: {issue_key}")
            
            return issue_key

    # 🔁 새로운 이슈 생성
    print(f"[INFO] 기존 이슈 없음 → 새로운 이슈 생성")
    print(f"[INFO] Summary: {summary}")
    
    desc_text = (
        f"테스트 실패 감지됨 🚨\n\n"
        f"테스트: {test['classname']}::{test['name']}\n"
        f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
        f"링크: {BUILD_URL}\n\n"
        f"오류 메시지 요약:\n{test['message'][:500]}"
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
    resp = session.post(create_url, json=payload, timeout=30)
    
    if resp.status_code >= 400:
        print(f"[ERROR] 이슈 생성 실패: {resp.status_code}")
        print(f"[ERROR] 응답: {resp.text}")
        return None
    
    issue_key = resp.json().get("key")
    print(f"[INFO] 🆕 생성된 JIRA 이슈: {issue_key}")
    print(f"[INFO] 링크: {JIRA_URL}/browse/{issue_key}")
    return issue_key


def close_passed_issues(session, passed_tests):
    """✅ 통과된 테스트가 기존 실패 이슈를 닫도록 처리"""
    for test in passed_tests:
        test_identifier = f"{test['classname']} {test['name']}"
        escaped_identifier = escape_jql_value(test_identifier)
        
        jql = (
            f'project = "{JIRA_PROJECT}" '
            f'AND labels = "{LABEL_AUTOTEST}" '
            f'AND summary ~ "{escaped_identifier}" '
            f'AND statusCategory != Done '
            f'ORDER BY created DESC'
        )
        
        issues = jira_search_issues(session, jql)

        for issue in issues:
            issue_key = issue.get("key")
            if not issue_key:
                continue
                
            print(f"[INFO] ✅ 테스트 통과 — 이슈 {issue_key} 닫기 시도 중")

            # 1️⃣ 코멘트 추가
            comment_text = (
                f"✅ 자동화 테스트가 통과했습니다!\n\n"
                f"테스트: {test['classname']}::{test['name']}\n"
                f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
                f"링크: {BUILD_URL}\n\n"
                f"이전 실패 이슈를 자동으로 닫습니다."
            )
            comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
            session.post(comment_url, json={"body": make_adf_text(comment_text)}, timeout=30)

            # 2️⃣ 상태 전환 (Done)
            transition_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
            trans_resp = session.get(transition_url, timeout=30)
            if trans_resp.status_code == 200:
                transitions = trans_resp.json().get("transitions", [])
                done_transition = next((t for t in transitions if "Done" in t["name"]), None)
                if done_transition:
                    transition_id = done_transition["id"]
                    session.post(transition_url, json={"transition": {"id": transition_id}}, timeout=30)
                    print(f"[INFO] 🔒 이슈 {issue_key} → Done 으로 전환 완료")
                else:
                    print(f"[WARN] Done 상태 전환 옵션을 찾지 못했습니다 ({issue_key})")

# 🚀 메인 실행
if __name__ == "__main__":
    # 필수 환경변수 확인
    if not all([JIRA_URL, JIRA_PROJECT, JIRA_USER, JIRA_API_TOKEN]):
        print("[ERROR] 필수 환경변수가 설정되지 않았습니다:")
        print(f"  JIRA_URL: {JIRA_URL}")
        print(f"  JIRA_PROJECT: {JIRA_PROJECT}")
        print(f"  JIRA_USER: {JIRA_USER}")
        print(f"  JIRA_API_TOKEN: {'설정됨' if JIRA_API_TOKEN else '없음'}")
        sys.exit(1)
    
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
