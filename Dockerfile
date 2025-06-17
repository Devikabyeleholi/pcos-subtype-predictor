FROM python:3.10-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
