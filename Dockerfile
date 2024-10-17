FROM python:3.10

WORKDIR /app
ENV TZ=etc/UTC DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential 

# Install Python dependencies
COPY requirements.txt .
COPY app.py .
RUN pip install -r requirements.txt



CMD ["python", "app.py"] 