# Milestone 3: Authentication System

## What We Built Today

### 1. Authentication Features
- **Guest Users**: Anonymous users with 30-day expiration
- **Registered Users**: Email/password authentication with permanent accounts
- **JWT Tokens**: Secure session management

### 2. Database Integration
- PostgreSQL stores users and chat history
- User table with guest/registered user support
- ChatHistory table linked to users
- 30-day auto-expiration for guest accounts

### 3. API Endpoints
- `POST /auth/guest` - Create anonymous guest user
- `POST /auth/register` - Register with email/password
- `POST /auth/login` - Login existing user
- `GET /auth/verify` - Verify JWT token
- `POST /chat` - Send message (saves to database)
- `GET /chat/history/{user_id}` - Retrieve user's chat history

### 4. Tech Stack
- FastAPI backend
- PostgreSQL for persistence
- SQLAlchemy ORM
- JWT (python-jose) for authentication
- Bcrypt for password hashing

## Files Structure
```
milestone3_authentication/
├── auth/
│   ├── __init__.py
│   ├── models.py       # User & ChatHistory models
│   ├── schemas.py      # Pydantic models
│   ├── routes.py       # Auth endpoints
│   └── utils.py        # Password hashing & JWT
├── database/
│   ├── __init__.py
│   └── db.py           # Database connection
├── main.py             # Updated FastAPI app
└── README.md           # This file
```

## How to Run

1. Start PostgreSQL:
```bash
docker run -d --name propbot-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=propbot_db \
  -p 5432:5432 postgres:15
```

2. Install dependencies:
```bash
pip install sqlalchemy psycopg2-binary python-jose passlib bcrypt
```

3. Run backend:
```bash
cd milestone2/backend
uvicorn main:app --reload
```

## Testing

### Create Guest User
```bash
curl -X POST http://127.0.0.1:8000/auth/guest
```

### Register User
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

### Send Chat (saves to DB)
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Back Bay", "user_id": 1}'
```

### Get Chat History
```bash
curl http://127.0.0.1:8000/chat/history/1
```

## Key Features
- ✅ Guest users with 30-day history
- ✅ Registered users with permanent history
- ✅ PostgreSQL persistence
- ✅ JWT authentication
- ✅ Secure password hashing
- ✅ Chat history per user