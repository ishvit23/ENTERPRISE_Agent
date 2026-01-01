# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements (if exists) and install Python dependencies
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Set environment variables (override in docker-compose for secrets)
ENV PYTHONUNBUFFERED=1

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
