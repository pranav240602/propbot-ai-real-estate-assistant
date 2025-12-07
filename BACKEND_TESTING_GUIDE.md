# PropBot Backend Testing Guide

**Last Updated:** December 6, 2025  
**Backend Version:** 2.0.0  
**Team Members:** Test this on your laptop!

---

## 🎯 What You'll Test

This backend includes:
- ✅ User Authentication (Guest + Email/Password)
- ✅ AI-Powered Chat with Real Boston Property Data
- ✅ Price Extraction & Display
- ✅ Chat History Storage (30 days for guests, permanent for registered users)
- ✅ Property Search, Analytics, Commute Calculator

---

## 📋 Prerequisites

### Required Software:
1. **Python 3.9** (MUST be 3.9, NOT 3.12 or 3.13!)
2. **Docker Desktop**
3. **Git**
4. **OpenAI API Key** (get from https://platform.openai.com/api-keys)

### Check Your Python Version:
```bash
python --version
# OR
python3 --version
```

**If you have Python 3.12+, you MUST install Python 3.9!**

---

## 🚀 Setup Instructions

### Step 1: Clone Repository

**Mac/Linux:**
```bash
cd ~/Documents
git clone https://github.com/pranav240602/propbot-ai-real-estate-assistant.git
cd propbot-ai-real-estate-assistant
```

**Windows:**
```cmd
cd C:\Users\%USERNAME%\Documents
git clone https://github.com/pranav240602/propbot-ai-real-estate-assistant.git
cd propbot-ai-real-estate-assistant
```

---

### Step 2: Create Virtual Environment

**Mac/Linux (using Conda - Recommended):**
```bash
conda create -n propbot python=3.9 -y
conda activate propbot
```

**Mac/Linux (using venv):**
```bash
python3.9 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(propbot)` or `(venv)` at the start of your terminal.

---

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**This takes 10-15 minutes!** Be patient.

**Common Errors & Fixes:**

**Error: pandas build fails**
```bash
pip install pandas --upgrade
```

**Error: onnxruntime DLL (Windows only)**
- Download and install: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Restart computer
- Run `pip install onnxruntime` again

**Error: sentence-transformers import error**
```bash
pip install sentence-transformers --upgrade
```

**Error: pyspellchecker not found**
```bash
pip install pyspellchecker
```

---

### Step 4: Setup Environment Variables

**Create .env file:**

**Mac/Linux:**
```bash
cp .env.example .env
nano .env
```

**Windows:**
```cmd
copy .env.example .env
notepad .env
```

**Update these fields in .env:**
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/propbot_db
SECRET_KEY=your-super-secret-key-change-this
OPENAI_API_KEY=sk-YOUR-ACTUAL-OPENAI-KEY-HERE
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
ANONYMIZED_TELEMETRY=False
```

**IMPORTANT:** Replace `sk-YOUR-ACTUAL-OPENAI-KEY-HERE` with your real OpenAI API key!

Save and close.

---

### Step 5: Start Docker Containers

**Make sure Docker Desktop is running!**

**Start PostgreSQL:**
```bash
docker run -d \
  --name propbot-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=propbot_db \
  -p 5432:5432 \
  postgres:15
```

**Start ChromaDB:**
```bash
docker run -d \
  --name propbot-chroma \
  -p 8000:8000 \
  -e ANONYMIZED_TELEMETRY=False \
  chromadb/chroma:latest
```

**Verify both containers are running:**
```bash
docker ps
```

You should see both `propbot-postgres` and `propbot-chroma`.

**If containers already exist but stopped:**
```bash
docker start propbot-postgres propbot-chroma
```

---

### Step 6: Start Backend

**Mac/Linux:**
```bash
cd milestone2/backend
conda activate propbot  # or source ../../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Windows:**
```cmd
cd milestone2\backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Wait for these messages:**
```
INFO: ✅ RAG Pipeline initialized
INFO: ✅ Database tables created
INFO: ✅ Authentication routes registered
INFO: Application startup complete.
```

**Backend is now running on http://localhost:8001** ✅

---

## 🧪 Testing the Backend

### Test 1: Health Check

**Open browser:** http://localhost:8001/health

**Expected Response:**
```json
{
  "status": "healthy",
  "chromadb": "connected",
  "rag": "active",
  "collections": 17
}
```

---

### Test 2: Swagger UI (Best for Testing!)

**Open browser:** http://localhost:8001/docs

You'll see all API endpoints with a nice testing interface!

---

### Test 3: Create Guest User

**In Swagger UI:**
1. Click **POST /auth/guest**
2. Click "Try it out"
3. Click "Execute"

**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "is_guest": true,
  "guest_id": "uuid-here"
}
```

**Copy the `user_id` number** (e.g., 1, 2, 3)

---

### Test 4: Test Greeting

**In Swagger UI:**
1. Click **POST /chat**
2. Click "Try it out"
3. Enter this (replace USER_ID with your number):
```json
{
  "query": "Hi I am John",
  "user_id": 1
}
```
4. Click "Execute"

**Expected Response:**
```json
{
  "answer": "Hi John! 👋 How can I help you today?",
  "sources": [],
  "documents_retrieved": 0
}
```

✅ **PASS if:** Bot greets you by name with no property suggestions

---

### Test 5: Test Property Search with Real Prices

**In Swagger UI - POST /chat:**
```json
{
  "query": "Show me 3 bedroom properties in Jamaica Plain under 1 million",
  "user_id": 1
}
```

**Expected Response:**
```json
{
  "answer": "Here are three 3-bedroom properties...\n\nProperty 1:\n- Price: $600,000\n- Bedrooms: 3\n- Bathrooms: 2...",
  "sources": [...],
  "documents_retrieved": 10
}
```

✅ **PASS if:** Response shows ACTUAL PRICES like $600,000 (not "Price: Not Available")

---

### Test 6: Test Chat History

**In Swagger UI - GET /chat/history/{user_id}:**
1. Enter your user_id (e.g., 1)
2. Click "Execute"

**Expected Response:**
```json
{
  "user_id": 1,
  "is_guest": true,
  "history": [
    {
      "query": "Show me 3 bedroom properties...",
      "response": "Here are three...",
      "timestamp": "2025-12-06T..."
    }
  ]
}
```

✅ **PASS if:** Shows your previous chat messages

---

### Test 7: Test Analytics Dashboard

**In Swagger UI - GET /analytics/dashboard:**

**Expected Response:**
```json
{
  "total_properties": 29978,
  "total_searches": 5,
  "hottest_neighborhoods": [...],
  "market_insights": {...}
}
```

✅ **PASS if:** Returns market data

---

### Test 8: Test Price Prediction

**In Swagger UI - POST /predict-price:**
```json
{
  "neighborhood": "Back Bay",
  "bedrooms": 3,
  "bathrooms": 2
}
```

**Expected Response:**
```json
{
  "predicted_price": 950000,
  "confidence": 0.87,
  "price_range": {
    "min": 855000,
    "max": 1045000
  }
}
```

✅ **PASS if:** Returns price prediction

---

## ✅ Success Checklist

After all tests, you should have:

- [x] Backend starts without errors
- [x] Health check returns "healthy"
- [x] Can create guest user
- [x] Greeting detection works (responds to "Hi I am [name]")
- [x] Property search shows REAL PRICES ($600,000, etc.)
- [x] Chat history shows your messages
- [x] Analytics dashboard loads
- [x] Price prediction works
- [x] Match scores are POSITIVE percentages (15%, 48%, etc.)
- [x] Addresses display properly (not "Address not available")

---

## 🐛 Troubleshooting

### Backend won't start

**Check Python version:**
```bash
python --version  # Must be 3.9.x
```

**If wrong version, recreate venv with Python 3.9**

---

### "Module not found" errors

**Make sure venv is activated:**
```bash
# You should see (venv) or (propbot) in your terminal
```

**Reinstall packages:**
```bash
pip install -r requirements.txt
```

---

### Can't connect to PostgreSQL

**Check container is running:**
```bash
docker ps | grep postgres
```

**If not running:**
```bash
docker start propbot-postgres
```

**If doesn't exist:**
```bash
docker run -d --name propbot-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=propbot_db -p 5432:5432 postgres:15
```

---

### Can't connect to ChromaDB

**Check container is running:**
```bash
docker ps | grep chroma
```

**If not running:**
```bash
docker start propbot-chroma
```

**If doesn't exist:**
```bash
docker run -d --name propbot-chroma -p 8000:8000 -e ANONYMIZED_TELEMETRY=False chromadb/chroma:latest
```

---

### Port 8001 already in use

**Mac/Linux:**
```bash
lsof -i :8001
kill -9 <PID>
```

**Windows:**
```cmd
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

**Or use different port:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

---

### "Address not available" in responses

**Make sure you pulled the LATEST code:**
```bash
git pull origin main
```

The latest `rag_pipeline.py` has improved address parsing!

---

### Negative match scores (-48%)

**Make sure you pulled the LATEST code:**
```bash
git pull origin main
```

The latest `rag_pipeline.py` fixes score calculation!

---

## 🔄 How to Restart Everything

**Stop:**
```bash
# Press Ctrl+C in backend terminal
docker stop propbot-postgres propbot-chroma
```

**Start:**
```bash
docker start propbot-postgres propbot-chroma
cd milestone2/backend
conda activate propbot  # or venv activation
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

---

## 📞 Getting Help

**If you encounter issues:**

1. Check this guide's troubleshooting section
2. Verify all prerequisites are installed
3. Make sure you pulled latest code: `git pull origin main`
4. Check backend terminal for error messages
5. Contact Pranav with:
   - Error message screenshot
   - Output of `docker ps`
   - Output of `python --version`

---

## 🎯 What to Report After Testing

**Send to team:**

✅ **Working:**
- List which tests passed
- Screenshots of successful responses

❌ **Issues:**
- Which tests failed
- Error messages
- Your OS (Mac/Windows/Linux)
- Python version

---

## 📚 API Documentation

Once backend is running, full API docs available at:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

---

## 🎉 Expected Behavior

**Greeting Test:**
- Input: "Hi I am Sarah"
- Output: "Hi Sarah! 👋 How can I help you today?"

**Property Search Test:**
- Input: "Show me 3 bedroom properties in Jamaica Plain"
- Output: Actual properties with REAL PRICES ($600,000, $415,000, etc.)

**Match Scores:**
- Should be POSITIVE percentages: 15%, 48%, 75%
- NOT negative: -48% ❌

**Addresses:**
- Should show real addresses: "130 Minden St, Jamaica Plain"
- NOT "Address not available" ❌

---

## ✅ Backend is Production-Ready!

Once all tests pass, the backend is ready for:
- Frontend integration
- Deployment
- Demo/presentation

Happy testing! 🚀
