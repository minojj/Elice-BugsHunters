# 테스트 컨테이너 이미지 (python 3.11)
FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 종속성 캐시 최적화: 먼저 requirements만 복사
COPY requirements.txt /app/requirements.txt

# 빌드 필수 패키지가 필요하면 여기에 추가(예: gcc, libpq-dev 등)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt || true

# 소스/테스트 복사
COPY src /app/src
COPY tests /app/tests

# pytest가 requirements에 없을 수도 있으니 보강
RUN pip install pytest pytest-cov

# 테스트 결과를 꺼낼 경로
RUN mkdir -p /reports
VOLUME ["/reports"]

# 컨테이너 실행 시 pytest가 기본 동작
CMD ["pytest", "-q", \
     "--junitxml=/reports/test-results.xml", \
     "--cov=src", "--cov-report=xml:/reports/coverage.xml"]


