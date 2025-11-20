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
JIRA_EPIC_KEY = os.getenv("JIRA_EPIC_KEY", "Q31-174")  # ✅ 에픽 키
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
    """✅ Jira Cloud REST API v3 검색 (POST 방식)"""
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    
    payload = {
        "jql": jql,
        "maxResults": 50,
        "fields": ["key", "summary", "status"]
    }
    
    print(f"[DEBUG] 검색 URL: {url}")
    print(f"[DEBUG] JQL: {jql}")
    
    try:
        resp = session.post(url, json=payload, timeout=30)
        
        if resp.status_code != 200:
            print(f"[ERROR] Jira 검색 실패 ({resp.status_code})")
            print(f"[ERROR] 응답: {resp.text}")
            return []
        
        data = resp.json()
        issues = data.get("issues", [])
        print(f"[DEBUG] 검색된 이슈 수: {len(issues)}")
        
        if issues:
            for issue in issues[:3]:
                print(f"[DEBUG] - {issue.get('key')}: {issue.get('fields', {}).get('summary', 'N/A')}")
        
        return issues
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Jira API 요청 실패: {e}")
        return []


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
    """JQL 검색용 이스케이프"""
    value = re.sub(r'[^\w\s\-:]', ' ', value)
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


# 🧩 JIRA 이슈 생성 / 코멘트
def create_or_comment_issue(session, test):
    summary = make_summary(test)
    test_identifier = f"{test['classname']} {test['name']}"
    escaped_identifier = escape_jql_value(test_identifier)
    
    # ✅ Q31-174의 Sub-task 검색
    jql = (
        f'parent = {JIRA_EPIC_KEY} '
        f'AND summary ~ "{escaped_identifier}" '
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
            print(f"[INFO] {JIRA_EPIC_KEY}의 Sub-task 발견: {issue_key} — 코멘트 추가")
            
            comment_text = (
                f"🚨 자동화 테스트가 다시 실패했습니다!\n\n"
                f"테스트: {test['classname']}::{test['name']}\n"
                f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
                f"링크: {BUILD_URL}\n\n"
                f"실패 요약:\n{test['message'][:500]}"
            )
            
            comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
            try:
                resp = session.post(comment_url, json={"body": make_adf_text(comment_text)}, timeout=30)
                
                if resp.status_code >= 400:
                    print(f"[ERROR] 코멘트 추가 실패 ({issue_key}): {resp.status_code} {resp.text}")
                else:
                    print(f"[INFO] ✅ 코멘트 추가 완료: {issue_key}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] 코멘트 추가 중 오류: {e}")
            
            return issue_key

    # ✅ Q31-174의 Sub-task로 새 이슈 생성
    print(f"[INFO] {JIRA_EPIC_KEY}의 기존 Sub-task 없음 → 새 Sub-task 생성")
    print(f"[INFO] Summary: {summary}")
    
    desc_text = (
        f"테스트 실패 감지됨 🚨\n\n"
        f"테스트: {test['classname']}::{test['name']}\n"
        f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
        f"링크: {BUILD_URL}\n\n"
        f"오류 메시지:\n{test['message'][:500]}"
    )
    
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "description": make_adf_text(desc_text),
            "labels": [LABEL_AUTOTEST],
            "issuetype": {"name": "Bug"},  # ✅ Bug로 생성
            "parent": {"key": JIRA_EPIC_KEY}     # ✅ 부모 이슈 지정
        }
    }
    
    create_url = f"{JIRA_URL}/rest/api/3/issue"
    try:
        resp = session.post(create_url, json=payload, timeout=30)
        
        if resp.status_code >= 400:
            print(f"[ERROR] Sub-task 생성 실패: {resp.status_code}")
            print(f"[ERROR] 응답: {resp.text}")
            return None
        
        issue_key = resp.json().get("key")
        print(f"[INFO] 🆕 {JIRA_EPIC_KEY}의 Sub-task 생성: {issue_key}")
        print(f"[INFO] 링크: {JIRA_URL}/browse/{issue_key}")
        return issue_key
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Sub-task 생성 중 오류: {e}")
        return None


def close_passed_issues(session, passed_tests):
    """✅ 통과된 테스트의 Sub-task 닫기 (개선 버전)"""
    print(f"\n[INFO] === 통과된 테스트 처리 시작 ({len(passed_tests)}개) ===")
    
    closed_count = 0
    
    for test in passed_tests:
        test_identifier = f"{test['classname']} {test['name']}"
        escaped_identifier = escape_jql_value(test_identifier)
        
        # ✅ Q31-174의 열린 Sub-task 검색
        jql = (
            f'parent = {JIRA_EPIC_KEY} '
            f'AND summary ~ "{escaped_identifier}" '
            f'AND statusCategory != Done '  # Done이 아닌 것만
            f'ORDER BY created DESC'
        )
        
        print(f"\n[INFO] 테스트 확인: {test['classname']}::{test['name']}")
        issues = jira_search_issues(session, jql)

        if not issues:
            print(f"[INFO] → 열린 Sub-task 없음 (이미 완료되었거나 존재하지 않음)")
            continue

        for issue in issues:
            issue_key = issue.get("key")
            if not issue_key:
                continue
            
            current_status = issue.get("fields", {}).get("status", {}).get("name", "Unknown")
            print(f"[INFO] → Sub-task 발견: {issue_key} (현재 상태: {current_status})")

            # 1. 코멘트 추가
            comment_text = (
                f"✅ 자동화 테스트가 통과했습니다!\n\n"
                f"테스트: {test['classname']}::{test['name']}\n"
                f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
                f"브랜치: {BRANCH_NAME}\n"
                f"링크: {BUILD_URL}\n\n"
                f"이전 실패 이슈를 자동으로 닫습니다."
            )
            
            comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
            try:
                resp = session.post(comment_url, json={"body": make_adf_text(comment_text)}, timeout=30)
                if resp.status_code >= 400:
                    print(f"[WARN] 코멘트 추가 실패 ({issue_key}): {resp.status_code}")
                else:
                    print(f"[INFO] → 코멘트 추가 완료")
            except requests.exceptions.RequestException as e:
                print(f"[WARN] 코멘트 추가 중 오류: {e}")

            # 2. 사용 가능한 전환(transition) 조회
            transition_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
            try:
                trans_resp = session.get(transition_url, timeout=30)
                
                if trans_resp.status_code != 200:
                    print(f"[ERROR] 전환 옵션 조회 실패 ({issue_key}): {trans_resp.status_code}")
                    continue
                
                transitions = trans_resp.json().get("transitions", [])
                print(f"[DEBUG] 사용 가능한 전환: {[t['name'] for t in transitions]}")
                
                # Done, Close, Resolve, Complete 등 완료 상태 찾기
                done_keywords = ["Done", "Close", "Closed", "Resolve", "Resolved", "Complete", "Completed", "완료"]
                done_transition = None
                
                for keyword in done_keywords:
                    done_transition = next(
                        (t for t in transitions if keyword.lower() in t["name"].lower()), 
                        None
                    )
                    if done_transition:
                        break
                
                if done_transition:
                    transition_id = done_transition["id"]
                    transition_name = done_transition["name"]
                    
                    # 3. 상태 전환 실행
                    transition_payload = {
                        "transition": {"id": transition_id}
                    }
                    
                    trans_post_resp = session.post(
                        transition_url, 
                        json=transition_payload, 
                        timeout=30
                    )
                    
                    if trans_post_resp.status_code >= 400:
                        print(f"[ERROR] 상태 전환 실패 ({issue_key}): {trans_post_resp.status_code}")
                        print(f"[ERROR] 응답: {trans_post_resp.text}")
                    else:
                        print(f"[INFO] 🔒 Sub-task {issue_key} → {transition_name}")
                        closed_count += 1
                else:
                    print(f"[WARN] 완료 상태 전환 옵션을 찾을 수 없음 ({issue_key})")
                    print(f"[WARN] 사용 가능한 전환: {[t['name'] for t in transitions]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] 상태 전환 중 오류 ({issue_key}): {e}")
    
    print(f"\n[INFO] === 통과 처리 완료: {closed_count}개 이슈 닫음 ===\n")
    return closed_count

# 🚀 메인 실행
if __name__ == "__main__":
    if not all([JIRA_URL, JIRA_PROJECT, JIRA_USER, JIRA_API_TOKEN, JIRA_EPIC_KEY]):
        print("[ERROR] 필수 환경변수가 설정되지 않았습니다")
        print("[ERROR] JIRA_URL, JIRA_PROJECT, JIRA_USER, JIRA_API_TOKEN, JIRA_EPIC_KEY 확인 필요")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"[INFO] Jira 자동 이슈 관리 시작")
    print(f"[INFO] Epic: {JIRA_EPIC_KEY}")
    print(f"[INFO] Job: {JOB_NAME} #{BUILD_NUMBER}")
    print(f"[INFO] Branch: {BRANCH_NAME}")
    print(f"{'='*60}\n")
    
    failed_tests, passed_tests = parse_junit_results(JUNIT_PATH)
    session = make_jira_session()

    # 실패한 테스트 처리
    if failed_tests:
        print(f"[INFO] 🚨 {len(failed_tests)}개의 실패 테스트 처리 중...")
        for t in failed_tests:
            create_or_comment_issue(session, t)
    else:
        print("[INFO] ✅ 실패한 테스트 없음")

    # 통과한 테스트 처리
    if passed_tests:
        closed = close_passed_issues(session, passed_tests)
        print(f"[INFO] 최종: {closed}개 이슈 닫음")
    else:
        print("[INFO] 통과한 테스트 없음")
    
    print(f"\n{'='*60}")
    print(f"[INFO] 완료!")
    print(f"{'='*60}\n")
