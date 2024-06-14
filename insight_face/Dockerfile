FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
build-essential \
cmake \
git \
libatlas-base-dev \
libboost-all-dev \
libgl1-mesa-glx \
libglib2.0-dev \
libgtk2.0-dev \
libsm6 \
libssl-dev \
libv4l-dev \
libxext6 \
libxfixes3 \
libxi6 \
libxml2-dev \
libxrender-dev \
libzbar-dev \
pkg-config \
software-properties-common \
unzip \
wget \
zlib1g-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["uvicorn", "insight-face:apps", "--host", "127.0.0.1", "--port", "8000"]