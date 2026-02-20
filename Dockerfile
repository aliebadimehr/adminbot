# Use official Python runtime
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt if it exists
COPY requirements.txt ./

# Upgrade pip and install dependencies
RUN echo "force rebuild"
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir aiogram==3.25.0; fi

# Copy all files
COPY . .

# Command to run bot
CMD ["python", "tg.py"]
