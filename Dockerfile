# Use official lightweight Python image
FROM python:3.12-slim
# Add at the top after FROM
RUN pip install --no-cache-dir psycopg2-binary sqlmodel

# Set working directory
WORKDIR /app

# Copy requirements first (optimizes caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]