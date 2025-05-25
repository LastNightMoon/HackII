import os
import logging
import json
from dotenv import load_dotenv
from kombu import Connection, Queue, Producer
import sqlalchemy

from DataBaseManager import db, MusicMeta
from DataBaseManager.minio_manager import minio_manager
from recognition.schems import Song
from recognition.recognition_pipeline import AudioTranscriber


def process_message(body: str) -> dict:
    pipeline = AudioTranscriber(work_dir=WORK_DIR)

    try:
        meta_data = Song.model_validate_json(body)

        logger.info(f"Fetching audio metadata for ID: {meta_data.id}")
        audio_meta = db.select_music_by_id(meta_data.id)

        logger.info(f"Downloading audio from Minio: {audio_meta.url}")
        data = minio_manager.download_file("music", audio_meta.url)

        logger.info("Starting audio processing pipeline...")
        text = pipeline.process(data)
        db.execute_commit(
            sqlalchemy.update(MusicMeta).where(MusicMeta.music_id == audio_meta.music_id).values(text_music=text))
        return {
            "status": "success",
            "text": text,
        }
    except Exception as e:
        logger.exception("Ошибка в обработке аудио:")
        return {
            "status": "error",
            "error": str(e),
        }


def main():
    input_queue = Queue(INPUT_QUEUE, durable=True)
    output_queue = Queue(OUTPUT_QUEUE, durable=True)

    with Connection(RABBIT_URL) as conn:
        with conn.SimpleQueue(input_queue) as simple_queue:
            logger.info(f"🟢 Слушаю очередь: {INPUT_QUEUE}")
            while True:
                try:
                    message = simple_queue.get(timeout=1)
                    if not message:
                        continue

                    audio_path = message.payload.strip()
                    logger.info(f"📩 Получено сообщение: {audio_path}")

                    result = process_message(audio_path)

                    # Отправка результата
                    producer = Producer(conn)
                    producer.publish(
                        body=json.dumps(result, ensure_ascii=False),
                        routing_key=OUTPUT_QUEUE,
                        exchange='',
                        content_type='application/json',
                        delivery_mode=2  # persistent
                    )
                    logger.info(f"📤 Результат отправлен в очередь {OUTPUT_QUEUE}")
                    message.ack()

                except simple_queue.Empty:
                    continue
                except Exception as e:
                    logger.exception("Ошибка обработки сообщения:")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger(__name__)

    try:
        load_dotenv()

        RABBIT_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost//")
        INPUT_QUEUE = 'audio_output1'
        OUTPUT_QUEUE = 'audio_output2'
        WORK_DIR = 'temp_output_r'

        main()
    except KeyboardInterrupt:
        logger.info("🛑 Остановлено пользователем")
