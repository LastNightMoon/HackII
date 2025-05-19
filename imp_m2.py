import librosa
import soundfile as sf
import numpy as np
import pydub
from pydub.effects import normalize

# Параметры
input_file = "enhanced_song.wav"
output_file = "g.wav"
sample_rate = 44100  # Частота дискретизации
chunk_duration = 10  # Длительность чанка (секунды)

# Шаг 1: Загрузка и обработка аудио по чанкам
audio, sr = librosa.load(input_file, sr=sample_rate, mono=True)
chunk_size = chunk_duration * sample_rate
clean_audio = []

for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i + chunk_size]
    # Подавление шумов (pre-emphasis фильтр)
    clean_chunk = librosa.effects.preemphasis(chunk, coef=0.97)
    clean_audio.append(clean_chunk)

clean_audio = np.concatenate(clean_audio)
sf.write("clean_song.wav", clean_audio, sample_rate)

# Шаг 2: Усиление вокала и подавление громкой музыки
audio_segment = pydub.AudioSegment.from_file("clean_song.wav")

# Нормализация громкости
audio_segment = normalize(audio_segment)

# Эквализация: усиление вокала (1–4 кГц), подавление басов и высоких частот
audio_segment = audio_segment.high_pass_filter(100)  # Убрать басы
audio_segment = audio_segment.low_pass_filter(10000)  # Убрать высокие частоты
audio_segment = audio_segment + 6  # Усилить вокал на 6 дБ

# Компрессия для выравнивания громкости (подавление громкой музыки)
audio_segment = audio_segment.compress_dynamic_range(threshold=-20.0, ratio=6.0)

# Сохранение результата
audio_segment.export(output_file, format="wav")

print(f"Обработка завершена. Результат сохранен в {output_file}")