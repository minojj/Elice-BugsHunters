FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 시스템 패키지: chromium + 폰트/헤드리스 의존성
RUN apt-get update && apt-get install -y --no-install-recommends \
      chromium \
      fonts-liberation \
      libnss3 \
      libasound2 \
      libatk-bridge2.0-0 \
      libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
      libxrandr2 libgbm1 libgtk-3-0 \
      ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# 파이썬 의존성
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# 테스트 툴
RUN pip install pytest pytest-cov pytest-html webdriver-manager

# 소스/테스트
COPY src ./src
COPY tests ./tests

# 리포트 디렉토리
RUN mkdir -p /reports
VOLUME ["/reports"]

# 기본 실행: 헤드리스 pytest
ENV CHROME_BIN=/usr/bin/chromium
CMD ["pytest", "-q",
     "--junitxml=/reports/test-results.xml",
     "--html=/reports/report.html", "--self-contained-html",
     "--cov=src", "--cov-report=xml:/reports/coverage.xml"]
