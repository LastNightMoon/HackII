import numpy as np
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment
from pydub.effects import normalize

# Шаг 1: Загрузка и проверка аудио
audio, sample_rate = sf.read("src/Боевая-пехотная.wav")

# Проверка формы аудио
print(f"Audio shape: {audio.shape}, Sample rate: {sample_rate}")

# Преобразование в моно, если стерео
if len(audio.shape) > 1 and audio.shape[1] > 1:
    audio = np.mean(audio, axis=1)  # Среднее по каналам

# Шаг 2: Подавление шумов
# Обрабатываем аудио по частям, чтобы избежать перегрузки памяти
chunk_size = 10 * sample_rate  # 10 секунд
clean_audio = []

for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i + chunk_size]
    clean_chunk = nr.reduce_noise(y=chunk, sr=sample_rate, prop_decrease=0.8)
    clean_audio.append(clean_chunk)

clean_audio = np.concatenate(clean_audio)

# Сохранение очищенного аудио
sf.write("clean_song.wav", clean_audio, sample_rate)

# Шаг 3: Улучшение вокала и подавление громкой музыки
audio = AudioSegment.from_file("clean_song.wav")
audio = normalize(audio)
audio = audio.high_pass_filter(100)  # Убрать басы
audio = audio.low_pass_filter(10000)  # Убрать высокие частоты
audio = audio + 4  # Усилить вокал
audio = audio.compress_dynamic_range(threshold=-20.0, ratio=5.0)
audio.export("enhanced_song.wav", format="wav")