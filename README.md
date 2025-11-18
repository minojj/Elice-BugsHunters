# Elice BugsHunters 🐞

Elice BugsHunters는 엘리스 플랫폼의 **AI Helpy Chat** 웹 애플리케이션을 대상으로 한  
자동화 테스트 & 버그 헌팅 프로젝트입니다.  
Selenium + pytest 기반 E2E 테스트와 Docker/Jenkins 기반 CI 환경을 포함합니다.



## 📌 프로젝트 소개 (Overview)

- 대상 서비스: Elice AI Helpy Chat
- 목적: 반복되는 기능 테스트를 자동화하고, 회귀 테스트를 안정적으로 수행
- 특징:
  - Page Object Model(POM) 기반 구조
  - 명시적 대기를 활용한 안정적인 테스트
  - CI 환경(GitHub Actions, Jenkins, Docker) 연동



## 🧰 Tech Stack

- **Language**: Python (3.10+ 권장)
- **Test Framework**: pytest
- **Browser Automation**: Selenium WebDriver (Chrome)
- **CI/CD**: GitHub Actions, Jenkins
- **Container**: Docker, docker-compose



## 📁 폴더 구조

```text
.
├─ src/                 # Page Object, 유틸, 설정 코드
│  ├─ pages/            # 각 페이지(POM) 클래스
│  └─ utils/            # 공통 유틸리티, 헬퍼
├─ tests/               # pytest 테스트 코드
├─ resources/           # 테스트 데이터 (예: 계정/시나리오 데이터)
├─ reports/             # (선택) 테스트 리포트/로그
├─ tools/               # 스크립트, 유틸 도구
├─ .github/workflows/   # GitHub Actions 워크플로우
├─ Dockerfile
├─ Dockerfile.jenkins
├─ docker-compose.yml
├─ Jenkinsfile
├─ requirements.txt
└─ pytest.ini
```
## 🚀 시작하기 (Getting Started)

### 1) 레포지토리 클론

```bash
git clone https://github.com/minojj/Elice-BugsHunters.git
cd Elice-BugsHunters
git checkout develop



