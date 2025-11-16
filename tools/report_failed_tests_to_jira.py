import os
import xml.etree.ElementTree as ET
import requests
from urllib.parse import quote


JIRA_URL        = os.getenv("JIRA_URL")          # e.g. https://your-domain.atlassian.net
JIRA_PROJECT    = os.getenv("JIRA_PROJECT")      # e.g. BUG
JIRA_USER       = os.getenv("JIRA_USER")
JIRA_API_TOKEN  = os.getenv("JIRA_API_TOKEN")
JUNIT_PATH      = os.getenv("JUNIT_PATH", "reports/test-results.xml")

JOB_NAME        = os.getenv("JENKINS_JOB_NAME", "")
BUILD_NUMBER    = os.getenv("JENKINS_BUILD_NUMBER", "")
BRANCH_NAME     = os.getenv("JENKINS_BRANCH_NAME", "")
BUILD_URL       = os.getenv("JENKINS_BUILD_URL", "")

LABEL_AUTOTEST  = "autotest-failure"  # 자동 생성 티켓에 붙일 라벨


def parse_failed_tests(junit_path):
    if not os.path.exists(junit_path):
        print(f"[WARN] JUnit file not found: {junit_path}")
        return []

    tree = ET.parse(junit_path)
    root = tree.getroot()

    failed = []

    for testcase in root.iter("testcase"):
        name = testcase.attrib.get("name")
        classname = testcase.attrib.get("classname")
        failure = testcase.find("failure")
        error = testcase.find("error")

        if failure is None and error is None:
            continue

        msg = ""
        if failure is not None:
            msg = (failure.attrib.get("message", "") or "") + "\n" + (failure.text or "")
        elif error is not None:
            msg = (error.attrib.get("message", "") or "") + "\n" + (error.text or "")

        failed.append({
            "name": name,
            "classname": classname,
            "message": msg.strip()
        })

    return failed


def make_summary(test):
    return f"[AutoTest] Failed: {test['classname']}::{test['name']}"


def jira_session():
    if not (JIRA_URL and JIRA_PROJECT and JIRA_USER and JIRA_API_TOKEN):
        raise RuntimeError("JIRA env vars not set (JIRA_URL, JIRA_PROJECT, JIRA_USER, JIRA_API_TOKEN)")

    s = requests.Session()
    s.auth = (JIRA_USER, JIRA_API_TOKEN)
    s.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    return s


def find_existing_issue(session, summary):
    """
    같은 summary를 가진, 아직 닫히지 않은 자동 생성 이슈가 있는지 JQL로 검색
    """
    jql = (
        f'project = "{JIRA_PROJECT}" '
        f'AND summary ~ "{summary.replace("\"", "\\\"")}" '
        f'AND labels = {LABEL_AUTOTEST} '
        f'AND statusCategory != Done'
    )
    url = f"{JIRA_URL}/rest/api/3/search?jql={quote(jql)}&maxResults=1"
    resp = session.get(url)

    if resp.status_code >= 400:
        print(f"[WARN] JIRA search failed: {resp.status_code} {resp.text}")
        return None

    issues = resp.json().get("issues", [])
    if not issues:
        return None
    return issues[0]["key"]


def create_jira_issue(session, test):
    summary = make_summary(test)

    description_lines = [
        "*자동 생성된 테스트 실패 리포트*",
        "",
        f"*테스트:* `{test['classname']}::{test['name']}`",
        f"*브랜치:* `{BRANCH_NAME}`" if BRANCH_NAME else "",
        f"*잡:* `{JOB_NAME}`",
        f"*빌드 번호:* `{BUILD_NUMBER}`",
        f"*빌드 URL:* {BUILD_URL}" if BUILD_URL else "",
        "",
        "*메시지:*",
        f"{{code}}\n{test['message']}\n{{code}}"
    ]
    description = "\n".join([line for line in description_lines if line != ""])

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "description": description,
            "labels": [LABEL_AUTOTEST],
            "issuetype": {"name": "Bug"}
        }
    }

    url = f"{JIRA_URL}/rest/api/3/issue"
    resp = session.post(url, json=payload)

    if resp.status_code >= 400:
        print(f"[ERROR] Failed to create issue for {summary}: {resp.status_code} {resp.text}")
        return None
    key = resp.json().get("key")
    print(f"[INFO] Created JIRA issue: {key} for {summary}")
    return key


def comment_on_issue(session, issue_key, text):
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    payload = {
        "body": text
    }
    resp = session.post(url, json=payload)
    if resp.status_code >= 400:
        print(f"[WARN] Failed to comment on {issue_key}: {resp.status_code} {resp.text}")
    else:
        print(f"[INFO] Commented on {issue_key}")


def handle_failed_tests(session, failed_tests):
    """
    실패한 테스트들에 대해:
    - 같은 summary를 가진 이슈가 열려 있으면 → 코멘트만 추가
    - 없으면 → 새 Bug 이슈 생성
    """
    for test in failed_tests:
        summary = make_summary(test)
        existing_key = find_existing_issue(session, summary)

        if existing_key:
            print(f"[INFO] Existing issue found for {summary}: {existing_key}, adding comment")
            comment_text = (
                f"*자동 테스트 실패 재발생*\n\n"
                f"- 브랜치: `{BRANCH_NAME}`\n"
                f"- 잡: `{JOB_NAME}`\n"
                f"- 빌드 번호: `{BUILD_NUMBER}`\n"
                f"- 빌드 URL: {BUILD_URL}\n"
                f"- 메시지:\n"
                f"{{code}}\n{test['message']}\n{{code}}"
            )
            comment_on_issue(session, existing_key, comment_text)
        else:
            key = create_jira_issue(session, test)
            if key:
                # 첫 생성 시에는 코멘트까지는 굳이 안 달고 summary/description만으로 충분
                pass


def handle_all_passed(session):
    """
    이번 빌드에서 실패한 테스트가 하나도 없을 때:
    - 자동 생성된 이슈들을 찾아서
    - "현재 빌드에서 테스트가 통과했다"는 코멘트만 남김
    (상태 전환은 워크플로우마다 달라서 여기서는 코멘트까지만)
    """
    jql = (
        f'project = "{JIRA_PROJECT}" '
        f'AND labels = {LABEL_AUTOTEST} '
        f'AND statusCategory != Done'
    )
    url = f"{JIRA_URL}/rest/api/3/search?jql={quote(jql)}&maxResults=50"
    resp = session.get(url)

    if resp.status_code >= 400:
        print(f"[WARN] JIRA search for open autotest issues failed: {resp.status_code} {resp.text}")
        return

    issues = resp.json().get("issues", [])
    if not issues:
        print("[INFO] No open autotest issues to comment on.")
        return

    for issue in issues:
        key = issue["key"]
        comment_text = (
            f"*자동 테스트 통과 알림*\n\n"
            f"- 브랜치: `{BRANCH_NAME}`\n"
            f"- 잡: `{JOB_NAME}`\n"
            f"- 빌드 번호: `{BUILD_NUMBER}`\n"
            f"- 빌드 URL: {BUILD_URL}\n\n"
            f"이 빌드에서는 관련 자동 테스트가 모두 통과했습니다."
        )
        comment_on_issue(session, key, comment_text)


def main():
    try:
        session = jira_session()
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        return

    failed_tests = parse_failed_tests(JUNIT_PATH)

    if failed_tests:
        print(f"[INFO] Found {len(failed_tests)} failed tests. Creating/updating JIRA issues.")
        handle_failed_tests(session, failed_tests)
    else:
        print("[INFO] No failed tests found. Commenting on existing autotest issues if any.")
        handle_all_passed(session)


if __name__ == "__main__":
    main()
