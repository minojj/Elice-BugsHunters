FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 브라우저/드라이버 (가능한 경우 설치, 실패해도 통과)
RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      chromium chromium-driver fonts-liberation tzdata curl ca-certificates git || true; \
    rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver
WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# pytest를 기본 엔트리포인트로
ENTRYPOINT ["pytest"]
CMD ["tests","-v","--maxfail=1","--tb=short"]