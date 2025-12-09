FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn

COPY . .

EXPOSE 8080

CMD ["echo", "PropBot Docker build successful"]
