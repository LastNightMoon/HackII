# import os
# from pydub import AudioSegment
# import whisper
# import sys

# Папка с аудиофайлами
MUSIC_FOLDER = "."  # Укажи путь к папке
OUTPUT_FOLDER = "separated"  # Папка для текстов

# Создаем папку для текстов, если не существует
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Загружаем модель Whisper (tiny, base, small, medium, large — выбирай по ресурсам)
model = whisper.load_model("large-v3-turbo")  # "base" — компромисс между скоростью и качеством


def transcribe_audio(file_path):
    """Транскрипция аудиофайла в текст."""
    try:
        # Загружаем аудио
        audio = AudioSegment.from_file(file_path)

        # Whisper работает лучше с WAV, конвертируем
        wav_path = file_path.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")

        # Транскрипция
        result = model.transcribe(wav_path, language="ru", condition_on_previous_text=False)  # Укажи язык, если знаешь (например, "ru" для русского)
        text = result["text"]

        # # Удаляем временный WAV
        # os.remove(wav_path)

        return text
    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")
        return None


def main():
    # Обрабатываем все MP3 в папке
    for filename in os.listdir(MUSIC_FOLDER):
        if filename.endswith(".wav"):
            file_path = os.path.join(MUSIC_FOLDER, filename)
            print(f"Обработка: {filename}")

            # Транскрипция
            lyrics = transcribe_audio(file_path)
            if lyrics:
                # Сохраняем текст в файл
                output_file = os.path.join(OUTPUT_FOLDER, filename.replace(".wav", ".txt"))
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(lyrics)
                print(f"Текст сохранен: {output_file}")
            else:
                print(f"Не удалось транскрибировать: {filename}")


if __name__ == "__main__":
    main()