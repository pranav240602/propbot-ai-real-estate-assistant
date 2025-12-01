FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || pip install fastapi uvicorn pandas

COPY . .

EXPOSE 8001

CMD ["echo", "PropBot Docker build successful"]
