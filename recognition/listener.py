import os
import logging
import json

from kombu import Connection, Queue, Producer
from audio_pipeline import AudioTranscriber  # Импортируем твой класс

# Конфигурация
RABBIT_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost//")
INPUT_QUEUE = 'audio_output1'
OUTPUT_QUEUE = 'audio_output2'
WORK_DIR = 'temp_output_r'

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_message(audio_path):
    pipeline = AudioTranscriber(work_dir=WORK_DIR)
    try:
        text = pipeline.process(audio_path)
        return {
            "status": "success",
            "text": text,
            "path": audio_path
        }
    except Exception as e:
        logger.error(f"Ошибка в обработке аудио: {e}")
        return {
            "status": "error",
            "error": str(e),
            "path": audio_path
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
                        delivery_mode=2
                    )
                    logger.info(f"📤 Результат отправлен в очередь {OUTPUT_QUEUE}")
                    message.ack()

                except simple_queue.Empty:
                    continue
                except Exception as e:
                    logger.exception(f"Ошибка обработки сообщения: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Остановлено пользователем")
