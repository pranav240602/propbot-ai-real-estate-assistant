# PropBot Milestone 2 - Backend Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY backend/ ./backend/
COPY results/ ./results/
COPY models/ ./models/
COPY .env .env

# Expose port
EXPOSE 8001

# Run backend
CMD ["python", "backend/main.py"]
