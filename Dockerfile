FROM python:3.10-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование зависимостей и установка
COPY requirements_api.txt .

RUN pip install --no-cache-dir -r requirements_api.txt
#RUN
# Копирование исходников
COPY . .


LABEL authors="LapTop_Bogdan"
EXPOSE 8000
EXPOSE 6543

#CMD ["python", "-m",  "improvement.listener"]