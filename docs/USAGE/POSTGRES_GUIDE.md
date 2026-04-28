# PostgreSQL 운영 가이드

## 기준

- 논문 실험 빠른 실행은 SQLite를 사용한다
- 서비스/운영 배포는 PostgreSQL을 사용한다
- 두 경우 모두 SQLAlchemy ORM을 사용한다

## 현재 ORM 모델

| 모델 | 용도 |
|---|---|
| User | 사용자 계정 |
| Conversation | 대화 세션 |
| Message | 메시지 |
| Paper | 업로드 문서 메타데이터 |
| RevokedToken | 로그아웃/폐기된 JWT |

## PostgreSQL Docker 실행

```bash
docker run -d \
  --name mrag-postgres \
  -e POSTGRES_USER=mrag \
  -e POSTGRES_PASSWORD=mrag \
  -e POSTGRES_DB=mrag \
  -p 5432:5432 \
  postgres:16-alpine
```

## Backend 연결

```bash
cd backend
set DATABASE_URL=postgresql+asyncpg://mrag:mrag@localhost:5432/mrag
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

PowerShell

```powershell
cd backend
$env:DATABASE_URL = "postgresql+asyncpg://mrag:mrag@localhost:5432/mrag"
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 테이블 생성

현재 코드는 시작 시 `init_db()`를 통해 SQLAlchemy metadata 기반 테이블 생성을 수행한다. 운영 마이그레이션이 필요하면 Alembic을 사용한다.

```bash
cd backend
alembic upgrade head
```

## 확인 SQL

```sql
\dt
SELECT id, username, email, created_at FROM users;
SELECT id, user_id, title, created_at FROM conversations;
SELECT id, user_id, doc_id, collection_name, title FROM papers;
SELECT id, user_id, jti, expires_at FROM revoked_tokens;
```

## 주의

- ChromaDB는 PostgreSQL에 저장되지 않는다
- 업로드 원본 파일은 `backend/data`에 저장된다
- 벡터 데이터는 `backend/chroma_db`에 저장된다
- 따라서 운영 백업은 PostgreSQL, ChromaDB, data 폴더를 함께 포함해야 한다
