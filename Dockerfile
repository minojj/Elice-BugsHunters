FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Chromium + Chromedriver 설치 (아키텍처 자동 매칭: amd64/arm64)
RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      chromium chromium-driver \
      fonts-liberation tzdata ca-certificates curl git; \
    rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .

# pytest를 컨테이너 기본 엔트리포인트로
ENTRYPOINT ["pytest"]
CMD ["tests","-v","--maxfail=1","--tb=short"]