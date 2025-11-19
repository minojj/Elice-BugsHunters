import os
import sys
import re
import requests
import xml.etree.ElementTree as ET

# 🌐 환경변수 설정
JIRA_URL = os.getenv("JIRA_URL")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PARENT_KEY = os.getenv("JIRA_PARENT_KEY", "Q31-174")  # 부모 이슈
JUNIT_PATH = os.getenv("JUNIT_PATH", "reports/test-results.xml")
JOB_NAME = os.getenv("JENKINS_JOB_NAME", "unknown-job")
BUILD_NUMBER = os.getenv("JENKINS_BUILD_NUMBER", "0")
BUILD_URL = os.getenv("JENKINS_BUILD_URL", "")
LABEL_AUTOTEST = "autotest"


# 🧩 유틸 함수
def make_summary(test):
    """테스트 실패 이슈의 요약(Summary) 생성"""
    return f"[AutoTest] Failed: {test['classname']}::{test['name']}"


def make_adf_text(text: str):
    """ADF(Atlassian Document Format) 포맷 변환"""
    paragraphs = []
    for line in text.split('\n'):
        if line.strip():
            paragraphs.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })
    return {
        "type": "doc",
        "version": 1,
        "content": paragraphs if paragraphs else [{"type": "paragraph"}]
    }


def escape_jql_value(value: str) -> str:
    """JQL 검색용 문자열 이스케이프"""
    value = re.sub(r'[^\w\s\-:]', ' ', value)
    value = re.sub(r'\s+', ' ', value)
    return value.strip()


def make_jira_session():
    """Jira API 세션 생성"""
    session = requests.Session()
    session.auth = (JIRA_USER, JIRA_API_TOKEN)
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    return session


# 🔍 Sub-task 이슈타입 탐색
def get_subtask_issuetype_name(session):
    """
    프로젝트에서 사용 가능한 Sub-task 이슈타입 이름 찾기
    실패 시 기본값 'Sub-task' 반환
    """
    try:
        resp = session.get(f"{JIRA_URL}/rest/api/3/issuetype", timeout=30)
        if resp.status_code != 200:
            print(f"[WARN] 이슈타입 조회 실패: {resp.status_code}")
            return "Sub-task"
        
        for issuetype in resp.json():
            if issuetype.get("subtask"):
                name = issuetype.get("name")
                print(f"[INFO] Sub-task 이슈타입 발견: {name}")
                return name
        
        print("[WARN] Sub-task 이슈타입 없음 → 'Sub-task' 사용")
        return "Sub-task"
    
    except requests.exceptions.RequestException as e:
        print(f"[WARN] 이슈타입 조회 오류: {e}")
        return "Sub-task"


# 🔍 JQL 검색
def jira_search_issues(session, jql):
    """Jira JQL 검색"""
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    payload = {
        "jql": jql,
        "maxResults": 50,
        "fields": ["key", "summary", "status"]
    }
    
    print(f"[DEBUG] JQL: {jql}")
    
    try:
        resp = session.post(url, json=payload, timeout=30)
        
        if resp.status_code != 200:
            print(f"[ERROR] Jira 검색 실패 ({resp.status_code}): {resp.text}")
            return []
        
        issues = resp.json().get("issues", [])
        print(f"[DEBUG] 검색된 이슈 수: {len(issues)}")
        
        return issues
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Jira API 요청 실패: {e}")
        return []


# 📄 JUnit XML 파싱
def parse_junit_results(xml_path):
    """JUnit XML 결과 파싱"""
    failed_tests = []
    passed_tests = []
    print(f"[INFO] JUnit 파일 파싱: {xml_path}")

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
            message = failure.attrib.get("message", "")
            text = failure.text or ""
            failed_tests.append({
                "name": name,
                "classname": classname,
                "message": (message + "\n" + text)[:1000]
            })
        else:
            passed_tests.append({
                "name": name,
                "classname": classname
            })

    print(f"[INFO] 실패: {len(failed_tests)}건 / 통과: {len(passed_tests)}건")
    return failed_tests, passed_tests


# 🆕 이슈 생성 또는 코멘트 추가
def create_or_comment_issue(session, test, subtask_type_name):
    """실패 테스트에 대한 Jira Sub-task 생성 또는 기존 이슈에 코멘트"""
    summary = make_summary(test)
    test_identifier = f"{test['classname']} {test['name']}"
    escaped_identifier = escape_jql_value(test_identifier)
    
    # 기존 미완료 Sub-task 검색
    jql = (
        f'parent = "{JIRA_PARENT_KEY}" '
        f'AND issuetype = "{subtask_type_name}" '
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
            return None
        
        status = issue.get("fields", {}).get("status", {}).get("name", "알 수 없음")
        print(f"[INFO] 기존 Sub-task 발견: {issue_key} (상태: {status}) → 코멘트 추가")
        
        comment_text = (
            f"🚨 자동화 테스트 재실패\n\n"
            f"테스트: {test['classname']}::{test['name']}\n"
            f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
            f"링크: {BUILD_URL}\n\n"
            f"실패 메시지:\n{test['message'][:500]}"
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

    # 새 Sub-task 생성
    print(f"[INFO] 기존 이슈 없음 → 새 Sub-task 생성 (parent={JIRA_PARENT_KEY}, type={subtask_type_name})")
    
    desc_text = (
        f"자동화 테스트 실패 감지\n\n"
        f"테스트: {test['classname']}::{test['name']}\n"
        f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
        f"링크: {BUILD_URL}\n\n"
        f"오류 메시지:\n{test['message'][:800]}"
    )
    
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "description": make_adf_text(desc_text),
            "labels": [LABEL_AUTOTEST],
            "issuetype": {"name": subtask_type_name},
            "parent": {"key": JIRA_PARENT_KEY}
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
        print(f"[INFO] 🆕 Sub-task 생성 완료: {issue_key}")
        print(f"[INFO] 링크: {JIRA_URL}/browse/{issue_key}")
        return issue_key
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Sub-task 생성 중 오류: {e}")
        return None


# 🔒 이슈 닫기 (다단계 전환 지원)
def attempt_close_issue(session, issue_key):
    """
    이슈를 완료(Done) 상태로 전환 시도
    직접 전환 불가능하면 중간 단계(진행 중) 경유
    """
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    
    def fetch_transitions():
        """사용 가능한 전환 목록 조회"""
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f"[WARN] 전환 조회 실패 {issue_key}: {resp.status_code}")
                return []
            transitions = resp.json().get("transitions", [])
            print(f"[DEBUG] {issue_key} 사용 가능 전환: {[t.get('name') for t in transitions]}")
            return transitions
        except requests.exceptions.RequestException as e:
            print(f"[WARN] 전환 조회 오류 {issue_key}: {e}")
            return []
    
    def apply_transition(transition):
        """전환 적용"""
        tid = transition["id"]
        try:
            resp = session.post(url, json={"transition": {"id": tid}}, timeout=30)
            if resp.status_code >= 300:
                print(f"[WARN] 전환 실패 {issue_key}: {transition.get('name')} ({resp.status_code})")
                return False
            to_status = transition.get("to", {}).get("name", "알 수 없음")
            print(f"[INFO] 전환 적용 {issue_key}: {transition.get('name')} → {to_status}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[WARN] 전환 적용 오류 {issue_key}: {e}")
            return False

    # 1단계: 직접 Done 전환 시도
    transitions = fetch_transitions()
    if not transitions:
        return

    # statusCategory가 'done'인 전환 찾기
    done_transition = next(
        (t for t in transitions 
         if t.get("to", {}).get("statusCategory", {}).get("key") == "done"),
        None
    )
    
    # 이름 패턴으로 찾기 (다국어 지원)
    if not done_transition:
        done_transition = next(
            (t for t in transitions 
             if re.search(r'(Done|완료|종료|Closed|Resolved|해결|닫힘)', t.get("name", ""), re.I)),
            None
        )
    
    if done_transition:
        if apply_transition(done_transition):
            print(f"[INFO] 🔒 이슈 완료 처리 성공: {issue_key}")
            return
        else:
            print(f"[WARN] Done 전환 실패했지만 계속 시도: {issue_key}")

    # 2단계: 중간 상태(진행 중) 경유 후 재시도
    print(f"[INFO] 직접 완료 불가 → 중간 단계 경유 시도: {issue_key}")
    
    progress_transition = next(
        (t for t in transitions 
         if t.get("to", {}).get("statusCategory", {}).get("key") in ("in-progress", "indeterminate")),
        None
    )
    
    if not progress_transition:
        progress_transition = next(
            (t for t in transitions 
             if re.search(r'(In Progress|진행|Start|시작)', t.get("name", ""), re.I)),
            None
        )
    
    if progress_transition:
        if apply_transition(progress_transition):
            # 재조회 후 Done 전환 시도
            transitions = fetch_transitions()
            
            done_transition = next(
                (t for t in transitions 
                 if t.get("to", {}).get("statusCategory", {}).get("key") == "done"
                 or re.search(r'(Done|완료|종료|Closed|Resolved|해결|닫힘)', t.get("name", ""), re.I)),
                None
            )
            
            if done_transition:
                if apply_transition(done_transition):
                    print(f"[INFO] 🔒 이슈 완료 처리 성공 (2단계): {issue_key}")
                    return
            else:
                print(f"[WARN] 2단계 후에도 완료 전환 없음: {issue_key}")
        return
    
    print(f"[WARN] 완료/진행 전환 모두 없음 → 수동 처리 필요: {issue_key}")


# ✅ 통과 테스트 이슈 닫기
def close_passed_issues(session, passed_tests, subtask_type_name):
    """통과된 테스트의 기존 실패 Sub-task 닫기"""
    for test in passed_tests:
        test_identifier = f"{test['classname']} {test['name']}"
        escaped_identifier = escape_jql_value(test_identifier)
        
        jql = (
            f'parent = "{JIRA_PARENT_KEY}" '
            f'AND issuetype = "{subtask_type_name}" '
            f'AND summary ~ "{escaped_identifier}" '
            f'AND statusCategory != Done '
            f'ORDER BY created DESC'
        )
        
        issues = jira_search_issues(session, jql)
        
        if not issues:
            continue
        
        for issue in issues:
            issue_key = issue.get("key")
            if not issue_key:
                continue
            
            print(f"[INFO] 테스트 통과 → 종료 처리 시도: {issue_key}")
            
            # 코멘트 추가
            comment_text = (
                f"✅ 자동화 테스트 통과\n\n"
                f"테스트: {test['classname']}::{test['name']}\n"
                f"빌드: {JOB_NAME} #{BUILD_NUMBER}\n"
                f"링크: {BUILD_URL}\n\n"
                f"이전 실패 이슈를 자동으로 닫습니다."
            )
            
            comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
            try:
                session.post(
                    comment_url, 
                    json={"body": make_adf_text(comment_text)}, 
                    timeout=30
                )
            except requests.exceptions.RequestException as e:
                print(f"[WARN] 코멘트 추가 실패: {e}")
            
            # 이슈 닫기 시도
            attempt_close_issue(session, issue_key)


# 🚀 메인 실행
if __name__ == "__main__":
    # 필수 환경변수 확인
    if not all([JIRA_URL, JIRA_PROJECT, JIRA_USER, JIRA_API_TOKEN, JIRA_PARENT_KEY]):
        print("[ERROR] 필수 환경변수가 설정되지 않았습니다")
        print("[ERROR] JIRA_URL, JIRA_PROJECT, JIRA_USER, JIRA_API_TOKEN, JIRA_PARENT_KEY 확인 필요")
        sys.exit(1)
    
    print(f"[INFO] 부모 이슈 {JIRA_PARENT_KEY} 아래 Sub-task 관리 시작")
    
    # JUnit 결과 파싱
    failed_tests, passed_tests = parse_junit_results(JUNIT_PATH)
    
    # Jira 세션 생성
    session = make_jira_session()
    
    # Sub-task 이슈타입 이름 조회
    subtask_type_name = get_subtask_issuetype_name(session)
    
    # 실패 테스트 처리
    if failed_tests:
        print(f"[INFO] 🚨 실패 테스트 처리: {len(failed_tests)}건")
        for test in failed_tests:
            create_or_comment_issue(session, test, subtask_type_name)
    else:
        print("[INFO] 실패한 테스트 없음")
    
    # 통과 테스트 처리 (이슈 닫기)
    if passed_tests:
        print(f"[INFO] ✅ 통과 테스트 처리 (닫기): {len(passed_tests)}건")
        close_passed_issues(session, passed_tests, subtask_type_name)
    else:
        print("[INFO] 통과한 테스트 없음")
    
    print("[INFO] 모든 처리 완료")
