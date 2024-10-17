FROM python:3.11-alpine

WORKDIR /app
ENV TZ=etc/UTC 

# Install dependencies
RUN apk add --no-cache \
    git \
    build-base 

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt 

COPY . .

CMD ["python", "app.py"] 