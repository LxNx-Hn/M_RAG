# PostgreSQL 완전 입문 가이드

> M-RAG 프로젝트 기준 — "처음 써보는 PostgreSQL" 대상

---

## 0. PostgreSQL이 뭐야?

**한 줄 요약**: 엑셀처럼 표(테이블)로 데이터를 저장하는 프로그램인데, 여러 사람이 동시에 읽고 써도 안 꼬이게 해주는 전문 소프트웨어.

```
PostgreSQL (서버 프로그램)
    ↕  SQL 명령어 (SELECT, INSERT 등)
Python / FastAPI (우리 코드)
    ↕  SQLAlchemy ORM (Python 객체 ↔ DB 테이블 자동 변환)
```

M-RAG에서 PostgreSQL이 저장하는 것:
- **User** 테이블: 아이디, 비밀번호(해시), 이메일
- **Conversation** 테이블: 대화 세션 (제목, 생성일)
- **Message** 테이블: 실제 채팅 메시지 (질문/답변, 타임스탬프)

> **ChromaDB(벡터DB)는 별개**: 논문 청크와 임베딩은 PostgreSQL이 아니라 ChromaDB에 저장됨.

---

## 1. 로컬 설치 (맥 기준)

### 방법 A: Homebrew (추천, 개발용)

```bash
# 설치
brew install postgresql@16

# 서비스 시작 (맥 재부팅 시 자동 시작)
brew services start postgresql@16

# 잘 됐는지 확인
psql postgres -c "SELECT version();"
# → PostgreSQL 16.x ... 출력되면 성공
```

### 방법 B: Docker (팀 협업, 프로덕션 환경 통일)

```bash
docker run -d \
  --name mrag-postgres \
  -e POSTGRES_USER=mrag \
  -e POSTGRES_PASSWORD=mrag \
  -e POSTGRES_DB=mrag \
  -p 5432:5432 \
  postgres:16-alpine

# 확인
docker ps  # mrag-postgres가 Up 상태여야 함
```

> M-RAG Docker Compose (`docker-compose.yml`)는 이 방법을 자동으로 처리함.

---

## 2. 데이터베이스 & 유저 생성

```bash
# PostgreSQL 콘솔 접속 (Homebrew 설치한 경우)
psql postgres

# 또는 Docker 컨테이너 내부
docker exec -it mrag-postgres psql -U mrag
```

콘솔 안에서 실행:

```sql
-- 1. 사용자(role) 생성
CREATE USER mrag WITH PASSWORD 'mrag';

-- 2. 데이터베이스 생성
CREATE DATABASE mrag OWNER mrag;

-- 3. 권한 부여
GRANT ALL PRIVILEGES ON DATABASE mrag TO mrag;

-- 4. 확인
\l          -- 데이터베이스 목록
\du         -- 유저 목록
\q          -- 콘솔 종료
```

---

## 3. M-RAG 백엔드 연결 설정

### 3-1. 환경변수 설정

`backend/` 디렉토리에 `.env` 파일 생성:

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://mrag:mrag@localhost:5432/mrag
```

> **형식 설명**: `postgresql+asyncpg://[유저]:[비밀번호]@[호스트]:[포트]/[DB이름]`  
> `asyncpg`는 FastAPI의 비동기 처리를 위한 PostgreSQL 드라이버.

### 3-2. 테이블 자동 생성 (마이그레이션)

```bash
cd backend
# FastAPI 앱을 한 번 실행하면 SQLAlchemy가 테이블을 자동으로 만들어줌
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 또는 직접 생성 스크립트
python -c "
import asyncio
from api.database import init_db
asyncio.run(init_db())
print('테이블 생성 완료')
"
```

### 3-3. 테이블 생성 확인

```bash
# DB 접속
psql -U mrag -d mrag

# 테이블 목록 확인
\dt

# 예상 출력:
#  Schema |     Name      | Type  | Owner
# --------+---------------+-------+-------
#  public | users         | table | mrag
#  public | conversations | table | mrag
#  public | messages      | table | mrag
```

---

## 4. 자주 쓰는 SQL 명령어

```sql
-- 접속
psql -U mrag -d mrag

-- 유저 목록 보기
SELECT id, username, email, created_at FROM users;

-- 특정 유저의 대화 목록
SELECT c.id, c.title, c.created_at
FROM conversations c
WHERE c.user_id = 1
ORDER BY c.created_at DESC;

-- 메시지 내용 보기
SELECT role, content, created_at
FROM messages
WHERE conversation_id = 1
ORDER BY created_at;

-- 유저 삭제 (테스트 데이터 정리)
DELETE FROM users WHERE username = 'test_user';

-- 테이블 전체 비우기 (개발 중 초기화)
TRUNCATE users, conversations, messages RESTART IDENTITY CASCADE;
```

> **CASCADE**: 연결된 데이터도 같이 삭제 (예: 유저 삭제 시 해당 대화/메시지도 삭제)

---

## 5. 로컬 개발 전체 실행 순서

```bash
# 터미널 1: PostgreSQL 실행 확인
brew services list | grep postgresql
# → postgresql@16  started 이어야 함

# 터미널 1: 백엔드 실행
cd M_RAG/backend
DATABASE_URL=postgresql+asyncpg://mrag:mrag@localhost:5432/mrag \
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 터미널 2: 프론트엔드 실행
cd M_RAG/frontend
npm run dev
# → http://localhost:5173 접속

# 또는 한 번에: (루트에서)
./dev.sh all
```

---

## 6. Docker Compose로 전체 실행 (추천)

PostgreSQL 수동 설치 없이 Docker 하나로 해결:

```bash
# Docker Desktop 먼저 설치 필요
# https://www.docker.com/products/docker-desktop/

# 실행 (처음엔 이미지 빌드로 5~10분 소요)
cd M_RAG
docker compose up --build

# 서비스 확인
docker compose ps
# db         Up (healthy)
# backend    Up
# frontend   Up

# 접속
# → 프론트엔드: http://localhost:3000
# → FastAPI Swagger: http://localhost:8000/docs
```

### Docker Compose 주요 명령어

```bash
# 중단 (데이터 보존)
docker compose stop

# 중단 + 컨테이너 삭제 (데이터 보존, 이미지 유지)
docker compose down

# 완전 초기화 (데이터 포함 전체 삭제 ⚠️)
docker compose down -v

# 로그 보기
docker compose logs -f backend
docker compose logs -f db

# DB 컨테이너 접속
docker compose exec db psql -U mrag -d mrag
```

---

## 7. 문제 해결

### "connection refused" 오류

```bash
# PostgreSQL이 안 켜진 것
brew services start postgresql@16
# 또는
docker start mrag-postgres
```

### "role 'mrag' does not exist" 오류

```bash
psql postgres -c "CREATE USER mrag WITH PASSWORD 'mrag';"
psql postgres -c "CREATE DATABASE mrag OWNER mrag;"
```

### "asyncpg not found" 오류

```bash
pip install asyncpg
# 또는
pip install -r backend/requirements.txt
```

### 테이블이 생성 안 됨

```bash
# api/database.py의 init_db()를 직접 호출
cd backend
python -c "
import asyncio
from api.database import engine, Base
from api import models  # ORM 모델 임포트 필수

async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('테이블 생성 완료')

asyncio.run(create())
"
```

---

## 8. RunPod 서버 배포 시 PostgreSQL 설정

### 8-1. RunPod 인스턴스에서

```bash
# Ubuntu 기준
apt update && apt install -y postgresql postgresql-client

# 서비스 시작
systemctl start postgresql
systemctl enable postgresql

# DB 설정 (위 2번 섹션과 동일)
sudo -u postgres psql -c "CREATE USER mrag WITH PASSWORD '강력한비밀번호';"
sudo -u postgres psql -c "CREATE DATABASE mrag OWNER mrag;"
```

### 8-2. 외부 접속 허용 (선택사항)

```bash
# /etc/postgresql/16/main/postgresql.conf 수정
listen_addresses = '*'

# /etc/postgresql/16/main/pg_hba.conf 추가
host    mrag    mrag    0.0.0.0/0    scram-sha-256

systemctl restart postgresql
```

### 8-3. 환경변수 설정

```bash
# RunPod의 경우 Environment Variables 탭에서 설정
DATABASE_URL=postgresql+asyncpg://mrag:비밀번호@localhost:5432/mrag
```

> 프로덕션에서는 비밀번호를 `mrag`처럼 단순하게 쓰지 마세요.

---

## 9. SQLAlchemy ORM이란? (개념 이해)

M-RAG 코드에서 DB를 어떻게 쓰는지 보면:

```python
# backend/api/models.py — 테이블 = Python 클래스
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String)

# backend/api/routers/auth.py — 데이터 조회
user = await db.execute(select(User).where(User.username == username))
# → SQL: SELECT * FROM users WHERE username = ?

# 데이터 추가
new_user = User(username="kim", email="kim@example.com")
db.add(new_user)
await db.commit()
# → SQL: INSERT INTO users (username, email) VALUES (?, ?)
```

SQL 직접 안 써도 되고, Python 객체로 DB를 다룰 수 있게 해주는 게 SQLAlchemy의 역할.

---

## 10. SQLite로 단순화 (개발/데모 전용)

PostgreSQL 서버 없이 파일 하나로 운영하고 싶으면:

```bash
# backend/.env 수정
DATABASE_URL=sqlite+aiosqlite:///./mrag.db
```

```bash
pip install aiosqlite
```

> **주의**: SQLite는 동시 쓰기(write)가 제한됨. 다중 사용자 서비스에는 부적합. 데모/테스트 전용.

---

## 참고 명령어 카드

```bash
# PostgreSQL 상태 확인
brew services list | grep postgresql

# DB 접속
psql -U mrag -d mrag

# 테이블 목록
\dt

# 현재 DB 확인
SELECT current_database();

# 연결 상태 확인
SELECT count(*) FROM pg_stat_activity WHERE datname = 'mrag';

# 종료
\q
```
