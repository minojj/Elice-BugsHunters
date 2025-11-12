FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Chrome 대체(Chromium) + 드라이버 + 필요한 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver \
    fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libdrm2 libgbm1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -U pip && pip install -r requirements.txt || true
RUN pip install selenium pytest pytest-cov pytest-html

COPY src ./src
COPY tests ./tests

ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver

# headless 기본
CMD ["bash","-lc","pytest tests -v \
  --junitxml=reports/test-results.xml \
  --html=reports/report.html --self-contained-html --tb=short"]
