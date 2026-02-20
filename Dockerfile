# Use official Python runtime
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies if you have any (مثلا requirements.txt)
# RUN pip install -r requirements.txt

# Command to run bot
CMD ["python", "tg.py"]
