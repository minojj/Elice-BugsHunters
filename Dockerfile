FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

COPY src /app/src
COPY tests /app/tests

# pytest 설치 (requirements.txt에 없다면)
RUN pip install pytest

CMD ["pytest", "-q"]
