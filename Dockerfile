FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# 시스템 패키지 (psycopg2 빌드용 libpq-dev 포함)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY . .

# 데이터/DB 디렉토리
RUN mkdir -p data chroma_db logs

# 환경 변수
ENV TOKENIZERS_PARALLELISM=false

# 포트
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
