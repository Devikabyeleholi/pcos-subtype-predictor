# Use ultra-slim base image
FROM python:3.10-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (media and OpenCV requirements)
RUN apk add --no-cache \
    libstdc++ \
    ffmpeg \
    libx11 \
    libgcc \
    libjpeg-turbo \
    libwebp \
    tiff \
    zlib

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Expose port
EXPOSE 10000

# Start the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
