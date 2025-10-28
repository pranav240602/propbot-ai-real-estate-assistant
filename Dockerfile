cat > Dockerfile << 'EOF'
FROM apache/airflow:2.7.1-python3.9

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements and install
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy project files
COPY dags /opt/airflow/dags
COPY scripts /opt/airflow/scripts
COPY data /opt/airflow/data
COPY great_expectations /opt/airflow/great_expectations

# Set working directory
WORKDIR /opt/airflow

# Environment variables
ENV PYTHONUNBUFFERED=1
EOF
