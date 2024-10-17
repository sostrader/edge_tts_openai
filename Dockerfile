FROM python:3.11-alpine

WORKDIR /app
ENV TZ=etc/UTC 

# Install dependencies
RUN apk add --no-cache \
    git \
    build-base \
    ffmpeg \
    libmagic \
    espeak-ng

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt 

COPY . .

CMD ["python", "app.py"] 