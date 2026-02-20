# Use official Python runtime
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Upgrade pip and install aiogram directly
RUN pip install --upgrade pip && \
    pip install --no-cache-dir aiogram==3.25.0

# Copy all files
COPY . .

# Command to run bot
CMD ["python", "tg.py"]
