# Elice BugsHunters 🐞

Elice BugsHunters는 엘리스 플랫폼의 AI Helpy Chat 웹 애플리케이션을 대상으로 한
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

- 채팅 히스토리

    - 새 대화 생성 시 사이드바에 스레드가 시간순으로 추가되는지 검증

    - 스레드 이름 변경 및 삭제 기능 검증

- 빌링/크레딧 페이지

    - 크레딧 사용 섹션이 정상적으로 로드되는지 확인

    - 특정 요소가 로딩될 때까지 presence 기반 대기

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
