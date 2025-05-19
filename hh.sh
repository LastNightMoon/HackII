#!/bin/bash

set -e

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install vosk soundfile torchaudio

# Создаём директорию для модели
mkdir -p models
cd models

# Скачиваем русскую модель
echo "⬇️ Скачивание модели Vosk для русского языка..."
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip"
MODEL_ZIP="vosk-model-ru-0.42.zip"
MODEL_DIR="vosk-model-ru-0.42"

if [ ! -f "$MODEL_ZIP" ]; then
    wget $MODEL_URL
fi

# Распаковываем модель
if [ ! -d "$MODEL_DIR" ]; then
    echo "📦 Распаковка модели..."
    unzip -q $MODEL_ZIP
else
    echo "✅ Модель уже распакована."
fi

echo "✅ Установка завершена. Модель находится в models/$MODEL_DIR"
