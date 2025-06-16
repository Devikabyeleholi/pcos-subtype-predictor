# Use an official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV + MediaPipe
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Expose the port Render or other platforms will use
EXPOSE 10000

# Run the app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
