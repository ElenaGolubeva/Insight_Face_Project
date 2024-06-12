FROM python:3.9-slim

# Устанавливаем необходимые зависимости
# Устанавливаем альтернативную библиотеку OpenGL
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    libglib2.0-dev \
    libgtk2.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libatlas-base-dev \
    gfortran \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . /app
WORKDIR /app

# Запускаем скрипт
CMD ["python", "frame.py"]
