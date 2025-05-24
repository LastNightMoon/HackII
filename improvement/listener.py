import os
import logging
from kombu import Connection, Queue, Producer
from dotenv import load_dotenv

from improvement.audio_pipeline import process_audio
from improvement.schems import Song
from DataBaseManager import db
from DataBaseManager.minio_manager import minio_manager


def audio_download(body):
    print("Parsing input metadata...")
    meta_data = Song.model_validate_json(body)

    print(f"Fetching audio metadata for ID: {meta_data.id}")
    audio_meta = db.select_music_by_id(meta_data.id)

    print(f"Downloading audio from Minio: {audio_meta.url}")
    data = minio_manager.download_file("music", audio_meta.url)

    print("Starting audio processing pipeline...")
    audio = process_audio(data)

    new_filename = "imp" + audio_meta.url
    print(f"Uploading processed audio to Minio as: {new_filename}")
    minio_manager.upload_file("music", audio, new_filename)

    print("Audio processing and upload completed successfully.")


if __name__ == "__main__":
    # Set up logging
    load_dotenv()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configuration
    rabbitmq_url = os.environ.get('RABBITMQ_URL')
    INPUT_QUEUE = 'audio_input'
    OUTPUT_QUEUE = 'audio_output1'
    WORK_DIR = 'temp_output_i'

    # Define durable queues
    input_queue = Queue(INPUT_QUEUE, durable=True, queue_declare=True)
    notification_queue = Queue(OUTPUT_QUEUE, durable=True, queue_declare=True)
    logger.info(INPUT_QUEUE)
    try:
        with Connection(rabbitmq_url) as conn:
            with conn.SimpleQueue(input_queue) as simple_queue:
                logger.info(f" [*] Waiting for messages on queue '{INPUT_QUEUE}'. To exit press CTRL+C")
                while True:
                    try:
                        message = simple_queue.get(timeout=1)
                        if message:
                            body = message.payload
                            logger.info(f" [x] Received: {body}")

                            try:
                                # Обработка аудио
                                audio_download(body)
                                logger.info(f" [x] Processed audio file: {body}")

                                # Отправка нотификации
                                producer = Producer(conn)
                                producer.publish(
                                    body=str(Song(id=2).json()),
                                    routing_key=OUTPUT_QUEUE,
                                    exchange='',
                                    delivery_mode=2
                                )
                                logger.info(f" [x] Notification sent")

                            except Exception as process_err:
                                logger.error(f"Failed to process audio: {process_err}")

                            message.ack()

                    except simple_queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Error in message loop: {e}")

    except KeyboardInterrupt:
        logger.info(' [*] Stopped consuming')
    except Exception as conn_err:
        logger.error(f"Connection error: {conn_err}")
