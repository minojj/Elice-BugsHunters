# Elice BugsHunters 🐞

Elice BugsHunters는 엘리스 플랫폼의 AI Helpy Chat 웹 애플리케이션을 대상으로 한
자동화 테스트 & 버그 헌팅 프로젝트입니다.
Selenium + pytest 기반 E2E 테스트와 Docker/Jenkins 기반 CI 환경을 포함합니다.

## 📌 프로젝트 소개 (Overview)

- 대상 서비스: Elice AI Helpy Chat
- 목적: 반복되는 기능 테스트를 자동화
- 특징:
  - Page Object Model(POM) 기반 구조
  - 명시적 대기를 활용한 안정적인 테스트
  - CI 환경(Jenkins, Docker) 연동

## 🏗️ 프로젝트 구조
<img src="./images/스크린샷 2025-11-19 135759.png" width="300" />

## 🧰 Tech Stack

- **Language**: Python (3.14+ 권장)
- **Test Framework**: pytest 8.3.3
- **Browser Automation**: Selenium WebDriver 4.25.0 (Chrome)
- **CI/CD**: Jenkins
- **Container**: Docker, docker-compose
- **테스트케이스 관리**: JIRA

<p align="center">
  <img src="https://img.shields.io/badge/python-3.14+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/selenium-webdriver-43B02A?logo=selenium&logoColor=white" />
  <img src="https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/jenkins-pipeline-D24939?logo=jenkins&logoColor=white" />
</p>



## 🏗 Architecture (Page Object Model)

- `src/pages/base_page.py` : 모든 페이지 객체(POM)의 공통 부모 클래스입니다. 각 페이지에서 자주 사용하는 대기 + 요소 조회 + 안전 클릭 로직을 한 곳에 모아 재사용합니다.

- `src/pages/billing_page.py` : AI Helpy Chat의 결제/과금 영역(크레딧 사용 내역, 결제 수단 등록, 다날 카드 결제창, 이용내역·ML API·Serverless 상태·API 키 관리)을 자동으로 열고 조작·검증하기 위한 Billing/Usage 전용 POM 클래스 묶음

- `src/pages/chat_base_page.py` : AI 채팅 화면에서 메시지 전송·응답 확인·파일 업로드·복사·편집·스크롤 등 주요 상호작용을 담당하는 Chat 페이지 POM 클래스

- `src/pages/chat_expanse_page.py` : AI Helpy Chat의 파일 업로드·퀴즈·PPT·이미지·구글 검색·심층 조사 등 “+ 버튼” 기반 확장 기능을 일괄 자동화·검증하는 통합 Chat 확장 POM 클래스

- `src/pages/custom_agent_page.py` : AI Helpy Chat의 에이전트 탐색·생성·관리 전 과정을 자동화·검증하기 위해 에이전트 관련 화면을 역할별 POM 클래스로 나눈 페이지 객체 묶음

- `src/pages/history_page.py` : AI Helpy Chat에서 대화 시작·메시지 전송·히스토리/검색·에이전트 탐색을 자동화하기 위한 핵심 화면들을 묶어 둔 POM 세트

- `src/pages/login_page.py` : AI Helpy Chat에서 로그인·회원가입·로그아웃·히스토리 초기화 등 계정 관련 흐름을 자동화하고 로그인 성공 여부를 검증하는 로그인 전용 POM 클래스

- `tests/` : 위 POM을 조합해서 E2E 시나리오 정의

## 🧪 Test Scenarios

| ID        | 영역            | 설명                                                |
|-----------|-----------------|-----------------------------------------------------|
| HT_001    | 히스토리        | 새 대화 생성 시 사이드바 최상단에 스레드 추가 검증 |
| HT_002    | 히스토리 검색   | 검색 오버레이에서 키워드로 스레드 검색            |
| HT_003    | 에이전트 탐색   | 에이전트 검색 시 결과 필터링 확인                 |
| BU_001    | 빌링/크레딧     | 크레딧 사용 섹션 로드 여부 확인                   |
| ...       | ...             | ...                                                 |


## 📝 테스트케이스 관리

<img src="./images/스크린샷 2025-11-19 105457.png" width="300" />
<img src="./images/스크린샷 2025-11-19 110155.png" width="300" />

JIRA를 통해 관리

## 🚀 시작하기 (Getting Started)

### 1) 레포지토리 클론

```bash
git clone https://github.com/minojj/Elice-BugsHunters.git
cd Elice-BugsHunters
git checkout develop
```
### 2) 가상환경 생성 및 의존성 설치
```bash
python -m venv .venv
```
## ⚙️ 환경 변수 설정 (.env)
프로젝트 루트에 .env 파일을 생성하고 다음과 같이 설정합니다.
```bash
python -m venv .venv
```
## 🧪 테스트 실행 방법

### 1) 전체테스트 실행
```bash
python -m venv .venv
```

## 🧱 주요 테스트 시나리오
- 계정/조직

    - 회원가입, 로그인, 로그아웃 기능 확인

- 빌링 & 이용내역

    - 크레딧 사용 섹션이 정상적으로 로드되는지 확인
    - 결제창이 로딩될 때까지 presence 기반 대기

- 채팅 히스토리

    - 새 대화 생성 시 사이드바에 스레드가 시간순으로 추가되는지 검증
    - 스레드 이름 변경 및 삭제 기능 검증

- 채팅 기본기능

    - 자연어로 AI와 실시간 질문/답변 대화 검증
    - AI 답변에 대한 좋아요/싫어요 평가 검증

- 채팅 고급기능

    - 문서, 이미지 등 파일을 업로드하여 AI가 분석 검증
    - 주제와 조건에 따른 프레젠테이션 슬라이드 자동 생성 검증

- 맞춤화기능

    - 채팅으로 에이전트 생성 검증
    - 에이전트 제거 검증


## 🐳 Docker / CI

### Docker로 실행
```bash
python -m venv .venv
```


## 👥 Members

| 장민호 | 조예진 | 김준서 | 최윤영 | 이태경 |
|:------:|:------:|:------:|:------:|:------:|
| <img src="https://avatars.githubusercontent.com/u/240609214?v=4" width="150"/> | <img src="https://avatars.githubusercontent.com/u/240632153?v=4" width="150"/> | <img src="https://avatars.githubusercontent.com/u/146753764?v=4" width="150"/> | <img src="https://avatars.githubusercontent.com/u/240609114?v=4" width="150"/> | <img src="https://avatars.githubusercontent.com/u/147461911?v=4" width="150"/> |
| [![GitHub](https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/minojj) | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yejin1024) | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/junseoseki) | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nwweiit) | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dlxorud1256) |
| [![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:user1@example.com) | [![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:user2@example.com) | [![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:user3@example.com) | [![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:user4@example.com) | [![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:user5@example.com) |
