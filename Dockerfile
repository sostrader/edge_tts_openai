FROM python:3.11-alpine

WORKDIR /app
ENV TZ=etc/UTC 

# Install dependencies
RUN apk add --no-cache \
    git \
    build-base \
    g++ \
    libc-dev

# Install Python dependencies
COPY . .
RUN pip3 install -r requirements.txt 



CMD ["python", "app.py"] 