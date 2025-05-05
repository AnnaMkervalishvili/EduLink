# Use a lightweight Python base image
FROM python:3.11-slim

# Set author info (optional)
LABEL maintainer="HP"

# Environment settings to speed things up
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory in container
WORKDIR /app

# Copy dependency list and install it
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your entire project folder into the container
COPY . .

# Open port 5000 for your Flask app
EXPOSE 5000

# Run your Flask app
CMD ["python", "service505.py"]
