FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver fonts-liberation tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["pytest"]    
   