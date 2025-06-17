FROM python:3.10-slim

WORKDIR /app

# Install only the absolutely necessary system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]

