FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 필요 시 시스템 드라이버 사전 설치(ARM에서 권장)
RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      chromium chromium-driver fonts-liberation tzdata ca-certificates curl git || true; \
    rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .
ENTRYPOINT ["pytest"]
CMD ["tests","-v","--maxfail=1","--tb=short"]