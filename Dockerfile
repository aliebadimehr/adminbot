# Use official Python runtime
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir aiogram==3.25.0

# Command to run bot
CMD ["python", "tg.py"]
