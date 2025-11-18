# Elice BugsHunters 🐞

Elice BugsHunters 프로젝트는 엘리스 플랫폼의 **AI Helpy Chat** 웹 애플리케이션을 대상으로 한  
자동화 테스트 & 버그헌팅 프로젝트입니다.  
Selenium + pytest 기반의 E2E 테스트와 Docker/Jenkins 기반 CI 환경을 포함하고 있습니다.

---

## 📁 프로젝트 구조

```text
.
├─ src/                 # Page Object, 유틸, 환경 설정 코드
├─ tests/               # pytest 기반 테스트 코드
├─ resources/
│  └─ testdata/         # 테스트 데이터 (예: 계정, 시나리오용 데이터)
├─ reports/             # (선택) 테스트 리포트/로그
├─ tools/               # 스크립트, 유틸리티 도구
├─ .github/workflows/   # GitHub Actions 워크플로우
├─ Dockerfile           # 기본 Docker 이미지
├─ Dockerfile.jenkins   # Jenkins용 Docker 이미지
├─ docker-compose.yml   # 로컬/CI 환경용 docker-compose 설정
├─ Jenkinsfile          # Jenkins 파이프라인 스크립트
├─ requirements.txt     # Python 패키지 의존성
└─ pytest.ini           # pytest 설정

🧰 Tech Stack

Language: Python (3.10+ 권장)

Test Framework: pytest

Browser Automation: Selenium WebDriver

CI/CD: GitHub Actions, Jenkins

Container: Docker, docker-compose
