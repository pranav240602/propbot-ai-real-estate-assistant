# Backend Setup Instructions

## Prerequisites
- Python 3.9+
- Docker Desktop
- PostgreSQL (via Docker)

## Setup Steps

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd propbot-ai-real-estate-assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib bcrypt pydantic[email]
```

### 4. Setup Environment Variables
```bash
cp .env.example .env
```
Then edit `.env` and add your actual values:
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `OPENAI_API_KEY`: Your OpenAI API key (if using)

### 5. Start PostgreSQL Database
```bash
docker run -d \
  --name propbot-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=propbot_db \
  -p 5432:5432 \
  postgres:15
```

### 6. Run Backend
```bash
cd milestone2/backend
uvicorn main:app --reload
```

Backend will be available at: http://127.0.0.1:8000

### 7. Test Endpoints

**Create Guest User:**
```bash
curl -X POST http://127.0.0.1:8000/auth/guest
```

**Register User:**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

**Send Chat:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Back Bay", "user_id": 1}'
```

## API Documentation
Once backend is running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Troubleshooting

**Database connection error?**
- Make sure PostgreSQL container is running: `docker ps`
- Check DATABASE_URL in .env matches container settings

**Import errors?**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Port already in use?**
- Change port: `uvicorn main:app --reload --port 8001`

## Common Issues & Fixes

### ChromaDB Telemetry Error
If you see "telemetry data not found" or ChromaDB connection errors:

**Already fixed in `.env.example`!** Just make sure your `.env` has:
```bash
ANONYMIZED_TELEMETRY=False
```

### Docker ChromaDB Setup
If running ChromaDB in Docker, use this in your `docker-compose.yml`:
```yaml
services:
  chroma:
    image: chromadb/chroma:latest
    environment:
      - ANONYMIZED_TELEMETRY=False
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_data:/chroma/chroma
```

Then start with:
```bash
docker-compose up -d
```
